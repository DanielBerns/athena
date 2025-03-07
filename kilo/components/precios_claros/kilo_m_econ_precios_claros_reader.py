import logging
from pathlib import Path
from typing import Generator

from components.precios_claros.kilo_precios_claros_io import get_price_in_cents
from components.precios_claros.kilo_precios_claros_reader import KiloPreciosClarosReader

class KiloMEconPreciosClarosReader:
    def __init__(
        self,
        reader: KiloPreciosClarosReader
    ):
        self._reader = reader

    def get_point_of_sale(
        self,
        event: dict[str, str]
    ) -> dict[str, str] | None:
        try:
            point_of_sale = {
                "point_of_sale_key": event["id"],
                "state": (event["provincia"]).lower(),
                "city": (event["localidad"]).lower(),
                "address": (event["direccion"]).lower(),
                "flag": (event["banderaDescripcion"]).lower(),
                "business": (event["comercioRazonSocial"]).lower(),
                "branch": (event["sucursalNombre"]).lower(),
            }
            return point_of_sale
        except Exception as message:
            logging.error(f"KiloMEconPreciosClarosReader.get_point_of_sale {message}\n")
            logging.error(f"  {as_jsonl(event):s}\n")
            return None

    def get_article_per_point_of_sale(
        self,
        event: dict[str, str]
    ) -> dict[str, str] | None:
        try:
            article_per_point_of_sale = {
                "article_key": event["id"],
                "brand": (event["marca"]).lower(),
                "name": (event["nombre"]).lower(),
                "package": (event["presentacion"]).lower(),
                "price": get_price_in_cents(event["precio"]),
                "point_of_sale_key": event["point_of_sale"],
            }
            return article_per_point_of_sale
        except Exception as message:
            logging.error(f"KiloMEconPreciosClarosReader.get_article_per_point_of_sale {message}\n")
            logging.error(f"  {as_jsonl(event):s}\n")
            return None

    def read_sample_home(precios_claros_home: Path) -> Generator[Path, None, None]:
        yield from self.reader.read_sample_home(precios_claros_home)

    def read_metadata(self) -> dict[str, str]:
        return self.reader.read_metadata

    def read_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        for event in self.reader.read_points_of_sale():
            yield self.get_point_of_sale(event)

    def read_selected_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        for event in self.reader.read_selected_points_of_sale():
            yield self.get_point_of_sale(event)

    def read_articles_per_point_of_sale(self) -> Generator[dict[str, str], None, None]:
        for event in self.reader.read_article_per_point_of_sale():
            yield self.get_article_per_point_of_sale(event)

import logging
from typing import Generator
from pathlib import Path

from components.precios_claros.juliet_precios_claros_reader import JulietPreciosClarosReader
from components.precios_claros.kilo_precios_claros_io import get_price_in_cents
from components.helpers.helpers import as_jsonl

class KiloJulietPreciosClarosReader:
    def __init__(
        self,
        reader: JulietPreciosClarosReader
    ):
        self._reader = reader

    @property
    def reader(self) -> JulietPreciosClarosReader:
        return self._reader

    def get_juliet_version(self, event: dict[str, str]) -> dict[str, str] | None:
        point_of_sale = {
            "point_of_sale_key": event["identifier"],
            "state": (event["provincia"]).lower(),
            "city": (event["localidad"]).lower(),
            "address": (event["direccion"]).lower(),
            "flag": (event["bandera"]).lower(),
            "business": (event["comercio"]).lower(),
            "branch": (event["sucursal"]).lower(),
        }
        return point_of_sale

    def get_older_version(self, event: dict[str, str]) -> dict[str, str] | None:
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

    def get_point_of_sale(
        self,
        event: dict[str, str]
    ) -> dict[str, str] | None:
        try:
            return self.get_juliet_version(event)
        except Exception:
           try:
               return self.get_older_version(event)
           except Exception as message:
               logging.error(f"KiloJulietPreciosClarosReader.get_point_of_sale {message}\n")
               if event:
                    logging.error(f"  {as_jsonl(event):s}\n")
               return None

    def get_article_per_point_of_sale(
        self,
        event
    ) -> dict[str, str] | None:
        try:
            article_per_point_of_sale = {
                "article_key": event["identifier"],
                "brand": (event["marca"]).lower(),
                "name": (event["nombre"]).lower(),
                "package": (event["presentacion"]).lower(),
                "price": get_price_in_cents(event["precio"]),
                "point_of_sale_key": event["point_of_sale"],
            }
            return article_per_point_of_sale
        except Exception as message:
            logging.error(f"KiloJulietPreciosClarosReader.get_article_per_point_of_sale {message}\n")
            if event:
                logging.error(f"  {as_jsonl(event):s}\n")
            return None

    def read_sample_home(self) -> Generator[Path, None, None]:
        for juliet_sample_home in self.reader.read_sample_home():
            self.current_sample_home = juliet_sample_home
            yield juliet_sample_home

    def read_metadata(self) -> dict[str, str]:
        sample_key = self.current_sample_home.stem
        return {"sample_key": sample_key}

    def read_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.reader.read_points_of_sale():
            yield self.get_point_of_sale(juliet_json)

    def read_selected_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.reader.read_selected_points_of_sale():
            yield self.get_point_of_sale(juliet_json)

    def read_articles_per_point_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.reader.read_articles_per_point_of_sale():
            yield self.get_article_per_point_of_sale(juliet_json)

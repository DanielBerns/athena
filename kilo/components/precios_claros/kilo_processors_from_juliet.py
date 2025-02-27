import logging

from components.precios_claros.kilo_processors import get_price_in_cents
from components.helpers.helpers import as_jsonl

class KiloPreciosClarosFromJuliet:
    def __init__(self):
        pass

    def get_point_of_sale(
        self,
        event: dict[str, str]
    ) -> dict[str, str] | None:
        if event is None:
            logging.error("KiloPreciosClarosFromJuliet.get_point_of_sale: event is None")
            return None
        try:
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
        except KeyError:
        except Exception
            logging.error(f"KiloPreciosClarosFromJuliet.get_point_of_sale {message}\n")
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
            logging.error(f"KiloPreciosClarosFromJuliet.get_article_per_point_of_sale {message}\n")
            logging.error(f"  {as_jsonl(event):s}\n")
            return None


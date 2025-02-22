
from dataclasses import dataclass
from typing import Dict

@dataclass
class JulietPointOfSale:
    point_of_sale: Dict[str, str]
    ok: bool

@dataclass
class JulietArticlePerPointOfSale:
    article_per_point_of_sale: Dict[str, str]
    ok: bool

def get_juliet_point_of_sale(
    json_from_scraper: dict[str, str]
) -> JulietPointOfSale:
    try:
        point_of_sale = {
            "identifier": json_from_scraper["id"],
             "provincia": (json_from_scraper["provincia"]).lower(),
             "localidad": (json_from_scraper["localidad"]).lower(),
             "direccion": (json_from_scraper["direccion"]).lower(),
               "bandera": (json_from_scraper["banderaDescripcion"]).lower(),
              "comercio": (json_from_scraper["comercioRazonSocial"]).lower(),
              "sucursal": (json_from_scraper["sucursalNombre"]).lower(),
        }
        return JulietPointOfSale(point_of_sale, True)
    except Exception as message:
        return JulietPointOfSale({}, False)

def get_juliet_article_per_point_of_sale(
    json_from_scraper
) -> JulietArticlePerPointOfSale
    try:
        article_per_point_of_sale = {
            "identifier": json_from_scraper["id"],
            "marca": (json_from_scraper["marca"]).lower(),
            "nombre": (json_from_scraper["nombre"]).lower(),
            "presentacion": (json_from_scraper["presentacion"]).lower(),
            "precio": json_from_scraper["precio"],
            "precio_min": json_from_scraper["precioMin"],
            "precio_max": json_from_scraper["precioMax"],
            "point_of_sale": json_from_scraper["point_of_sale"],
        }
        return JulietArticlePerPointOfSale(article_per_point_of_sale, True)
    except Exception as message:
        return JulietArticlePerPointOfSale({}, True)

from components.precios_claros.kilo_processors import KiloData, get_price_in_cents


class KiloPreciosClarosFromJuliet:
    def __init__(self):
        pass

    def get_point_of_sale(
        event: dict[str, str]
    ) -> dict[str, str] | None:
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
        except Exception as message:
            return None

    def get_article_per_point_of_sale(
        event
    ) -> dict[str, str] | None:
        try:
            article_per_point_of_sale = {
                "article_key": event["id"],
                "brand": (event["marca"]).lower(),
                "name": (event["nombre"]).lower(),
                "package": (event["presentacion"]).lower(),
                "price": get_price(event["precio"]),
                "point_of_sale_key": event["point_of_sale"],
            }
            return article_per_point_of_sale
        except Exception as message:
            return None

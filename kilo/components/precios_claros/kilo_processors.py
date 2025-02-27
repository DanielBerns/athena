from typing import Protocol
import json

class KiloPreciosClarosProcessor(Protocol):
    def get_point_of_sale(
        self,
        event: dict[str, str]
    ) -> dict[str, str] | None:
        ...

    def get_article_per_point_of_sale(
        self,
        event: dict[str, str]
    ) -> dict[str, str] | None:
        ...

def get_price_in_cents(price: str) -> str:
    return str(int(float(price) * 100))


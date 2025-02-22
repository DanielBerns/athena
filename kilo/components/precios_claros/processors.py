from dataclasses import dataclass
from typing import Protocol

@dataclass
class KiloPointOfSale:
    point_of_sale: dict[str, str] | None
    ok: bool


@dataclass
class KiloArticlePerPointOfSale:
    article_per_point_of_sale: dict[str, str] | None
    ok: bool


class KiloPreciosClarosProcessor(Protocol):
    def get_point_of_sale(
        self,
        event: dict[str, str]
    ) -> KiloPointOfSale:
        ...

    def get_article_per_point_of_sale(
        self,
        event: dict[str, str]
    ) -> KiloArticlePerPointOfSale:
        ...


def get_price(scraped_price: str) -> str:
    return str(int(float(price_str) * 100))


import logging
from typing import Protocol
from pathlib import Path
from components.precios_claros.database import (
    Timestamp,
    Tag,
    State,
    City,
    Place,
    PointOfSale,
    ArticleCode,
    ArticleCard,
    Price,
)


class DBTarget(Protocol):

    @property
    def current_sample_home(self) -> Path:
        ...

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        ...

    @property
    def current_timestamp(self) -> Timestamp | None:
        ...

    @current_timestamp.setter
    def current_timestamp(self, value: Timestamp | None) -> None:
        ...

    def kilo_points_of_sale(self, event: dict[str, str]) -> None:
        ...

    def kilo_articles_per_point_of_sale(self, event: dict[str, str]) -> None:
        ...

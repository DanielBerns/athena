import logging
from collections.abc import Callable

from pathlib import Path
from typing import Generator, Protocol

class KiloPreciosClarosTarget(Protocol):

    @property
    def current_sample_home(self) -> Path:
        ...

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        ...

    def kilo_points_of_sale(
        self,
        read_points_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        ...

    def kilo_selected_point_of_sale(
        self,
        read_selected_points_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        ...

    def kilo_articles_per_point_of_sale(
        self,
        read_article_per_point_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        ...

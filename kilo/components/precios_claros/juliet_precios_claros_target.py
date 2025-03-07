# Please, find the syntax error
from collections.abc import Callable
from typing import Protocol, Generator
from pathlib import Path


class JulietPreciosClarosTarget(Protocol):

    @property
    def current_sample_home(self) -> Path:
        ...

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        ...

    def juliet_points_of_sale(
        self,
        action: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        ...

    def juliet_selected_points_of_sale(
        self,
        action: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        ...

    def juliet_articles_per_point_of_sale(
        self,
        action: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        ...

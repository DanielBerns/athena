# Please, find the syntax error
from collections.abc import Callable
from typing import Protocol, Generator
from pathlib import Path


class JulietPreciosClarosTarget(Protocol):
    def current_sample_home(self, juliet_sample_home: Path) -> None:
        ...

    def juliet_points_of_sale(self, action: Callable[[Path], Generator[Path, None, None]]) -> None:
        ...

    def juliet_selected_points_of_sale(self, action: Callable[[Path], Generator[Path, None, None]]) -> None:
        ...

    def juliet_articles_per_point_of_sale(self, action: Callable[[Path], Generator[Path, None, None]]) -> None:
        ...

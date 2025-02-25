from typing import Protocol
from pathlib import Path


class JulietPreciosClarosTarget(Protocol):
    def juliet_sample_home(self, juliet_sample_home: Path) -> None:
        ...

    def juliet_point_of_sale(self, Callable[[Path], Generator[Path, None, None]]) -> None:
        ...

    def juliet_selected_point_of_sale(self, Callable[[Path], Generator[Path, None, None]]) -> None:
        ...

    def juliet_articles_per_point_of_sale(self, Callable[[Path], Generator[Path, None, None]]) -> None:
        ...

from typing import Protocol
from pathlib import Path


class JulietPreciosClarosTarget(Protocol):
    def juliet_sample_home(self, juliet_sample_home: Path) -> None:
        ...

    def juliet_point_of_sale_start(self) -> None:
        ...

    def juliet_point_of_sale(self, a_json_line: dict[str, str]) -> None:
        ...

    def juliet_point_of_sale_stop(self) -> None:
        ...

    def juliet_selected_point_of_sale_start(self) -> None:
        ...

    def juliet_selected_point_of_sale(self, a_json_line: dict[str, str]) -> None:
        ...

    def juliet_selected_point_of_sale_stop(self) -> None:
        ...

    def juliet_articles_per_point_of_sale_start(self) -> None:
        ...

    def juliet_articles_per_point_of_sale(self, a_json_line: dict[str, str]) -> None:
        ...

    def juliet_articles_per_point_of_sale_stop(self) -> None:
        ...

from pathlib import Path
from typing import Generator, Protocol


class JulietPreciosClarosReader(Protocol):

    @property
    def store_home(self) -> Path:
        ...

    @property
    def current_sample_home(self) -> Path | None:
        ...

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        ...

    def read_sample_home(self) -> Generator[Path, None, None]:
        ...

    def read_json(self, sample_home: Path, name: str) -> Generator[dict[str, str], None, None]:
        ...

    def read_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        ...

    def read_selected_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        ...

    def read_articles_per_point_of_sale(self) -> Generator[dict[str, str], None, None]:
        ...

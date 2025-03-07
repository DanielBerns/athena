from pathlib import Path
from typing import Generator, Protocol

class KiloPreciosClarosReader(Protocol):

    def read_sample_home(precios_claros_home: Path) -> Generator[Path, None, None]:
        ...

    def read_metadata(self) -> dict[str, str]:
        ...

    def read_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        ...

    def read_selected_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        ...

    def read_articles_per_point_of_sale(self) -> Generator[dict[str, str], None, None]:
        ...

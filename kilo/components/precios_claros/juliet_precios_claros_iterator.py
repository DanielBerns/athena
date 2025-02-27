from pathlib import Path
from typing import Generator
from components.core.flat_store import FlatStore
from components.helpers import get_json_lines, get_container

class JulietPreciosClarosIterator:
    @staticmethod
    def get_sample_home(precios_claros_flatstore: Path) -> Generator[Path, None, None]:
        flatstore = FlatStore(precios_claros_flatstore, "samples")
        for juliet_sample_home in flatstore.iterate():
            yield juliet_sample_home

    @staticmethod
    def get_points_of_sale(juliet_sample_home: Path) -> Generator[dict[str, str], None, None]:
        for juliet_json in get_json_lines(juliet_sample_home, "points_of_sale", "messages"):
            yield juliet_json

    @staticmethod
    def get_selected_points_of_sale(juliet_sample_home: Path) -> Generator[dict[str, str], None, None]:
        for juliet_json in get_json_lines(juliet_sample_home, "selected_points_of_sale", "messages"):
            yield juliet_json

    @staticmethod
    def get_articles_per_point_of_sale(juliet_sample_home: Path) -> Generator[dict[str, str], None, None]:
        for juliet_json in get_json_lines(juliet_sample_home, "articles_per_point_of_sale", "messages"):
            yield juliet_json


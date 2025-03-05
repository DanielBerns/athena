from pathlib import Path
from typing import Generator
from components.core.flat_store import FlatStore
from components.helpers import get_json_lines, get_container, read_text_file

class KiloPreciosClarosReader:
    @staticmethod
    def read_sample_home(precios_claros: Path) -> Generator[Path, None, None]:
        treestore = TreeStore(precios_claros, "samples")
        for kilo_sample_home in treestore.iterate():
            yield kilo_sample_home

    @staticmethod
    def read_metadata(kilo_sample_home: Path) -> dict[str, str]:
        metadata_resource = get_resource(self.kilo_sample_home, "metadata", ".json")
        metadata = read_json(metadata_resource)
        return metadata

    @staticmethod
    def read_points_of_sale(kilo_sample_home: Path) -> Generator[dict[str, str], None, None]:
        for kilo_json in get_json_lines(kilo_sample_home, "points_of_sale", "messages"):
            yield kilo_json

    @staticmethod
    def read_selected_points_of_sale(kilo_sample_home: Path) -> Generator[dict[str, str], None, None]:
        for kilo_json in get_json_lines(kilo_sample_home, "selected_points_of_sale", "messages"):
            yield kilo_json

    @staticmethod
    def get_articles_per_point_of_sale(kilo_sample_home: Path) -> Generator[dict[str, str], None, None]:
        for kilo_json in get_json_lines(kilo_sample_home, "articles_per_point_of_sale", "messages"):
            yield kilo_json


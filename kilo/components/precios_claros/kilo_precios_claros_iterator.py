from pathlib import Path
from typing import Generator
from components.core.flat_store import FlatStore
from components.helpers import get_json_lines, get_container, read_text_file

class KiloPreciosClarosIterator:
    @staticmethod
    def get_sample_home(precios_claros: Path) -> Generator[Path, None, None]:
        treestore = TreeStore(precios_claros, "samples")
        for kilo_sample_home in treestore.iterate():
            yield kilo_sample_home

    @staticmethod
    def get_metadata(kilo_sample_home: Path) -> Generator[dict[str, str], None, None]:
        metadata_resource = get_resource(self.kilo_sample_home, "metadata", ".jsonl")
        with read_text_file(metadata_resource) as metadata:
            line = metadata.read()
            yield from_jsonl(line)

    @staticmethod
    def get_points_of_sale(kilo_sample_home: Path) -> Generator[dict[str, str], None, None]:
        for kilo_json in get_json_lines(kilo_sample_home, "points_of_sale", "messages"):
            yield kilo_json

    @staticmethod
    def get_selected_points_of_sale(kilo_sample_home: Path) -> Generator[dict[str, str], None, None]:
        for kilo_json in get_json_lines(kilo_sample_home, "selected_points_of_sale", "messages"):
            yield kilo_json

    @staticmethod
    def get_articles_per_point_of_sale(kilo_sample_home: Path) -> Generator[dict[str, str], None, None]:
        for kilo_json in get_json_lines(kilo_sample_home, "articles_per_point_of_sale", "messages"):
            yield kilo_json


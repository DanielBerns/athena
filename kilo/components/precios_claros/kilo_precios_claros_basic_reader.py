from pathlib import Path
from typing import Generator
from components.core.tree_store import TreeStore
from components.helpers import read_json_lines, get_resource

class KiloPreciosClarosBasicReader:

    def __init__(self, kilo_precios_claros_home: Path) -> None:
        self._kilo_precios_claros_home = kilo_precios_claros_home
        self._current_sample_home: Path | None = None

    @property
    def kilo_precios_claros_home(self) -> Path:
        return self._kilo_precios_claros_home

    @property
    def current_sample_home(self) -> Path | None:
        return self._current_sample_home

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        self._current_sample_home = value

    def read_sample_home(self) -> Generator[Path, None, None]:
        treestore = TreeStore(self.kilo_precios_claros_home, "treestore")
        for kilo_sample_home in treestore.iterate():
            self.current_sample_home = kilo_sample_home
            yield kilo_sample_home

    def read_metadata(self) -> dict[str, str]:
        metadata_resource = get_resource(self.current_sample_home, "metadata", ".json")
        metadata = read_json(metadata_resource)
        return metadata

    def read_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        resource = get_resource(self.current_sample_home, "points_of_sale", ".jsonl")
        for kilo_json in read_json_lines(resource):
            yield kilo_json

    def read_selected_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        resource = get_resource(self.current_sample_home, "selected_points_of_sale", ".jsonl")
        for kilo_json in read_json_lines(resource):
            yield kilo_json

    def read_articles_per_point_of_sale(self) -> Generator[dict[str, str], None, None]:
        resource = get_resource(self.current_sample_home, "articles_per_point_of_sale", ".jsonl")
        for kilo_json in read_json_lines(resource):
            yield kilo_json


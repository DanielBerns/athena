from pathlib import Path
from typing import Generator, Tuple
from components.core.tree_store import TreeStore
from components.helpers import read_json, read_json_lines, get_resource

class KiloPreciosClarosBasicReader:

    def __init__(self, kilo_precios_claros_home: Path) -> None:
        self._kilo_precios_claros_home = kilo_precios_claros_home
        self._current_sample_home: Path | None = None
        self._current_sample_key: str | None = None
        self._tree_store = TreeStore(self.kilo_precios_claros_home, "treestore")

    @property
    def kilo_precios_claros_home(self) -> Path:
        return self._kilo_precios_claros_home

    @property
    def tree_store(self) -> TreeStore:
        return self._tree_store

    @property
    def current_sample_home(self) -> Path | None:
        return self._current_sample_home

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        self._current_sample_home = value

    @property
    def current_sample_key(self) -> str | None:
        return self._current_sample_key

    @current_sample_key.setter
    def current_sample_key(self, value: str) -> None:
        self._current_sample_key = value

    def read_metadata(self) -> dict[str, str]:
        metadata_resource = get_resource(self.current_sample_home, "metadata", ".json")
        metadata = read_json(metadata_resource)
        return metadata

    def read_sample(self, first_sample: int = 0, top_sample: int = -1) -> Generator[Tuple[Path, str], None, None]:
        for sample_index in self.tree_store.iterate(first_sample, top_sample):
            self.current_sample_home = self.tree_store.sample_home_by_index(sample_index)
            metadata = self.read_metadata()
            self.current_sample_key = metadata["sample_key"]
            yield self.current_sample_home, self.current_sample_key

    def read_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        resource = get_resource(self.current_sample_home, "points_of_sale", ".jsonl")
        for kilo_json in read_json_lines(resource):
            if kilo_json and len(kilo_json):
                yield kilo_json
            else:
                logging.error(f"*** Error {classname(self)}.read_points_of_sale: kilo_json is None or Empty")
                logging.error(f"    {str(resource)}")
                message = f"*** Error {classname(self)}.read_points_of_sale: stop"
                raise LoggedException(message)

    def read_selected_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        resource = get_resource(self.current_sample_home, "selected_points_of_sale", ".jsonl")
        for kilo_json in read_json_lines(resource):
            if kilo_json and len(kilo_json):
                yield kilo_json
            else:
                logging.error(f"*** Error {classname(self)}.read_selected_points_of_sale: kilo_json is None or Empty")
                logging.error(f"    {str(resource)}")
                message = f"*** Error {classname(self)}.read_selected_points_of_sale: stop"
                raise LoggedException(message)

    def read_articles_per_point_of_sale(self) -> Generator[dict[str, str], None, None]:
        resource = get_resource(self.current_sample_home, "articles_per_point_of_sale", ".jsonl")
        for kilo_json in read_json_lines(resource):
            if kilo_json and len(kilo_json):
                kilo_json["sample_key"] = self.current_sample_key
                yield kilo_json
            else:
                logging.error(f"*** Error {classname(self)}.read_articles_per_point_of_sale: kilo_json is None or Empty")
                logging.error(f"    {str(resource)}")
                message = f"*** Error {classname(self)}.read_articles_per_point_of_sale: stop"
                raise LoggedException(message)


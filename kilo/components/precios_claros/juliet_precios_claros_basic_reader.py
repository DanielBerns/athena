from pathlib import Path
from typing import Generator
from components.core.flat_store import FlatStore
from components.helpers import read_json_lines, get_container, get_resource


class JulietPreciosClarosBasicReader:
    def __init__(self, store_home: Path) -> None:
        self._store_home = store_home
        self._current_sample_home: Path | None = None

    @property
    def store_home(self) -> Path:
        return self._store_home

    @property
    def current_sample_home(self) -> Path | None:
        return self._current_sample_home

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        self._current_sample_home = value

    def read_sample_home(self) -> Generator[Path, None, None]:
        flatstore = FlatStore(self.store_home, "samples")
        for juliet_sample_home in flatstore.iterate():
            self.current_sample_home = juliet_sample_home
            yield juliet_sample_home

    def read_juliet_json(self, sample_home: Path, name: str) -> Generator[dict[str, str], None, None]:
        container = get_container(self.current_sample_home, name)
        resource = get_resource(container, "messages", ".jsonl")
        for juliet_json in read_json_lines(resource):
            yield juliet_json

    def read_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.read_juliet_json(self.current_sample_home, "points_of_sale"):
            yield juliet_json

    def read_selected_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.read_juliet_json(self.current_sample_home, "selected_points_of_sale"):
            yield juliet_json

    def read_articles_per_point_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.read_juliet_json(self.current_sample_home, "articles_per_point_of_sale"):
            yield juliet_json


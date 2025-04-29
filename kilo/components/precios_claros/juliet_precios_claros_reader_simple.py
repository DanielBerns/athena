import logging
from pathlib import Path
from typing import Generator
from components.core.flat_store import FlatStore
from components.helpers.helpers import read_json_lines, get_container, get_resource, classname
from components.core.logged_exception import LoggedException

class JulietPreciosClarosReaderSimple:
    def __init__(self, store_home: Path, first_sample: str = "") -> None:
        self._store_home = store_home
        self._current_sample_home: Path | None = None
        self._first_sample = first_sample

    @property
    def store_home(self) -> Path:
        return self._store_home

    @property
    def current_sample_home(self) -> Path | None:
        return self._current_sample_home

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        self._current_sample_home = value

    @property
    def first_sample(self) -> str:
        return first_sample

    @property
    def sample_keys(self) -> List[str]:
        flatstore = FlatStore(self.store_home, "samples")
        return flatstore.sorted_sample_keys()

    def read_sample_home(self) -> Generator[Path, None, None]:
        flatstore = FlatStore(self.store_home, "samples")
        for juliet_sample_home in flatstore.iterate(self.first_sample):
            self.current_sample_home = juliet_sample_home
            yield juliet_sample_home

    def read_juliet_json(self, sample_home: Path, name: str) -> Generator[dict[str, str], None, None]:
        container = get_container(self.current_sample_home, name)
        resource = get_resource(container, "messages", ".jsonl")
        for juliet_json in read_json_lines(resource):
            yield juliet_json

    def read_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.read_juliet_json(self.current_sample_home, "points_of_sale"):
            # (key, point_of_sale_key) = self.new_point_of_sale_code(juliet_json)
            # self.map_of_point_of_sale_codes[key] = point_of_sale_key
            # juliet_json["point_of_sale_key"] = point_of_sale_key
            yield juliet_json

    def read_selected_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.read_juliet_json(self.current_sample_home, "selected_points_of_sale"):
            # (key, point_of_sale_key) = self.new_point_of_sale_code(juliet_json)
            # self.map_of_point_of_sale_codes[key] = point_of_sale_key
            # juliet_json["point_of_sale_key"] = point_of_sale_key
            yield juliet_json

    def read_articles_per_point_of_sale(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.read_articles_per_point_of_sale start")
        for juliet_json in self.read_juliet_json(self.current_sample_home, "articles_per_point_of_sale"):
            # key = juliet_json["point_of_sale_code"]
            # point_of_sale_key = self.map_of_point_of_sale_codes.get(key, None)
            # if point_of_sale_key is None:
            #     logging.error(f"*** Error {classname(self):s}.read_articles_per_point_of_sale: unkown point_of_sale_code")
            #     for kk, vv in event.items():
            #         logging.error(f"    {kk}: {vv}")
            #     message = f"*** Error {classname(self):s}.read_articles_per_point_of_sale stop: unkown point_of_sale_code"
            #     raise LoggedException(message)
            # else:
            #     juliet_json["point_of_sale_key"] = point_of_sale_key
            yield juliet_json
        logging.info(f"{classname(self)}.read_articles_per_point_of_sale end")


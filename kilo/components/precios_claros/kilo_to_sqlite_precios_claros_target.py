import logging
from pathlib import Path
from collections.abc import Callable
from typing import TextIO, Generator

from components.kilo.kilo_paths import KiloPaths

from components.core.stats import Stats
from components.core.tree_store import TreeStore
from components.helpers import (
    get_container,
    get_resource,
    as_jsonl,
    create_text_file,
    classname,
    read_json)


class KiloToSqlitePreciosClarosException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


class KiloToSqlitePreciosClarosTarget:
    def __init__(self, kilo_paths: KiloPaths) -> None:
        self._kilo_paths = kilo_paths
        kilo_precios_claros = get_container(kilo_paths.storage, "precios_claros")
        self._kilo_precios_claros_db = get_container(kilo_precios_claros, "sqlite")
        self._current_sample_home: Path | None = None
        self._skip_sample = False

    @property
    def skip_sample(self) -> bool:
        return self._skip_sample

    @skip_sample.setter
    def skip_sample(self, value: bool) -> None:
        self._skip_sample = value

    @property
    def kilo_paths(self) -> KiloPaths:
        return self._kilo_paths

    @property
    def kilo_precios_claros_sqlite(self) -> Path:
        return self._kilo_precios_claros_db

    @property
    def sample_key(self) -> str | None:
        return self._sample_key

    @sample_key.setter
    def sample_key(self, value: str) -> None:
        self._sample_key = value

    @property
    def current_sample_home(self) -> Path:
        return self._current_sample_home

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        self.skip_sample = False
        self._current_sample_home = value
        try:
            resource = get_resource(self.current_sample_home, "metadata", ".json")
            metadata = read_json(resource)
            self.sample_key = metadata["sample_key"]
        except Exception as message:
            logging.error(f"*** ERROR -{classname(self):s}.current_sample_home")
            logging.error(f"    skipping sample: {str(value):s}")
            self.skip_sample = True

    def kilo_points_of_sale(
        self,
        get_points_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        if self.skip_sample:
            print("skipped")
        else:
            print("done")

    def kilo_selected_point_of_sale(
        self,
        get_selected_points_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        if self.skip_sample:
            print("skipped")
        else:
            print("done")


    def kilo_articles_per_point_of_sale(
        self,
        get_article_per_point_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        if self.skip_sample:
            print("skipped")
        else:
            print("done")

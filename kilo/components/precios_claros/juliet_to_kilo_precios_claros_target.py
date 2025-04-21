import logging
from pathlib import Path
from collections import defaultdict, Counter
from collections.abc import Callable
# from contextlib import contextmanager
from typing import DefaultDict, TextIO, Generator

from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_io import KiloPreciosClarosIO
from components.precios_claros.kilo_juliet_precios_claros_reader import KiloJulietPreciosClarosReader

from components.core.stats import Stats
from components.core.tree_store import TreeStore
from components.helpers import get_container, create_text_file, as_jsonl




class JulietToKiloPreciosClarosTarget:
    def __init__(self, kilo_paths: KiloPaths) -> None:
        self._kilo_paths = kilo_paths
        kilo_precios_claros = get_container(kilo_paths.storage, "precios_claros")

        self._dataset_stats: DefaultDict[str, Counter[str]] = Stats.create()
        self._points_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create()
        self._selected_points_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create()
        self._articles_per_point_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create()
        self._points_of_sale_table: dict[str, str] = {}
        self._treestore = TreeStore(kilo_precios_claros, "treestore")
        self._juliet_sample_home: Path | None = None
        self._kilo_io: KiloPreciosClarosIO = KiloPreciosClarosIO()

    @property
    def points_of_sale_table(self) -> dict[str, str]:
        return self._points_of_sale_table

    @property
    def treestore(self) -> TreeStore:
        return self._treestore

    @property
    def juliet_sample_home(self) -> str | None:
        return self._juliet_sample_home

    @juliet_sample_home.setter
    def juliet_sample_home(self, value: str) -> None:
        self._juliet_sample_home = value

    @property
    def sample_key(self) -> str | None:
        return self.juliet_sample_home.stem

    @property
    def kilo_io(self) -> KiloPreciosClarosIO:
        return self._kilo_io

    @property
    def dataset_stats(self) -> DefaultDict[str, Counter[str]]:
        return self._dataset_stats

    @property
    def points_of_sale_stats(self) -> DefaultDict[str, Counter[str]]:
        return self._points_of_sale_stats

    @property
    def selected_points_of_sale_stats(self) -> DefaultDict[str, Counter[str]]:
        return self._selected_points_of_sale_stats

    @property
    def articles_per_point_of_sale_stats(self) -> DefaultDict[str, Counter[str]]:
        return self._articles_per_point_of_sale_stats

    @property
    def kilo_paths(self) -> KiloPaths:
        return self._kilo_paths

    @property
    def current_sample_home(self) -> Path:
        return self.kilo_io.home

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        self.juliet_sample_home = value
        self.kilo_io.home = self.treestore.create_sample_home()
        self.kilo_io.create_metadata(self.sample_key)
        logging.info(f"{str(self.juliet_sample_home):s} -> {str(self.kilo_io.home):s}")

    def create_events_file(
        self,
        resource: Path, # resource = get_resource(self.home, name, ".jsonl")
        fun: Callable[[dict[str, str]], dict[str, str]],
        get_events: Callable[[], Generator[dict[str, str] | None, None, None]]
    ) -> Generator[dict[str, str], None, None]:
        with create_text_file(resource) as target:
            for event in get_events():
                kilo_event = fun(event)
                yield kilo_event
                target.write(as_jsonl(kilo_event))

    def juliet_points_of_sale(
        self,
        read_events: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        self.dataset_stats[self.sample_key]["point_of_sale"] += 1
        resource = self.kilo_io.get_events_resource("points_of_sale")
        fun = lambda x : self.kilo_io.get_point_of_sale_juliet_to_kilo(x)
        for event in self.create_events_file(resource, fun, read_events):
            self.points_of_sale_table[event["point_of_sale_code"]] = event["point_of_sale_key"]

    def juliet_selected_points_of_sale(
        self,
        read_events: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        self.dataset_stats[self.sample_key]["selected_point_of_sale"] += 1
        resource = self.kilo_io.get_events_resource("selected_points_of_sale")
        fun = lambda x : self.kilo_io.get_point_of_sale_juliet_to_kilo(x)
        for event in self.create_events_file("selected_points_of_sale", fun, read_events):
            pass

    def juliet_articles_per_point_of_sale(
        self,
        read_events: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        self.dataset_stats[self.sample_key]["articles_per_point_of_sale"] += 1
        resource = self.kilo_io.get_events_resource("selected_points_of_sale")
        fun = lambda x : self.kilo_io.get_article_per_point_of_sale_juliet_to_kilo(x)
        for event in self.create_events_file("articles_per_point_of_sale", fun, read_events):
            point_of_sale_code_string = event["point_of_sale_code"]
            event["point_of_sale_code"] = self.points_of_sale_table[point_of_sale_code_string]

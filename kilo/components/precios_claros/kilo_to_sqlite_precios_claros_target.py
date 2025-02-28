import logging
from pathlib import Path
from collections import defaultdict, Counter
from collections.abc import Callable
from contextlib import contextmanager
from typing import DefaultDict, TextIO, Generator

from components.kilo.kilo_paths import KiloPaths

from components.core.stats import Stats
from components.core.tree_store import TreeStore
from components.helpers import get_container, get_resource, as_jsonl, create_text_file


class KiloToSqlitePreciosClarosException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


class KiloToSqlitePreciosClarosTarget:
    def __init__(self, kilo_paths: KiloPaths) -> None:
        self._kilo_paths = kilo_paths
        kilo_precios_claros = get_container(kilo_paths.storage, "precios_claros")

        # Initialization and type hinting
        self._dataset_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()
        self._points_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()
        self._selected_points_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()
        self._articles_per_point_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()

        self._treestore = TreeStore(kilo_precios_claros, "treestore")
        self._processor = KiloPreciosClarosFromJuliet()
        self._kilo_sample_home: Path | None = None

    @property
    def treestore(self) -> TreeStore:
        return self._treestore

    @property
    def processor(self) -> KiloPreciosClarosFromJuliet:
        return self._processor

    @property
    def sample_key(self) -> str | None:
        return self.juliet_sample_home.stem

    @property
    def kilo_sample_home(self) -> Path | None:
        return self._kilo_sample_home

    @kilo_sample_home.setter
    def kilo_sample_home(self, value: Path) -> None:
        self._kilo_sample_home = value

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

    def current_sample_home(self, kilo_sample_home: Path) -> None:
        self.kilo_sample_home = kilo_sample_home
        logging.info(f"{str(self.kilo_sample_home):s} -> sqlite")
        sample_key = self.sample_key
        if sample_key:
            metadata_resource = get_resource(self.kilo_sample_home, "metadata", ".jsonl")
            with read_text_file(metadata_resource) as metadata:
                metadata.write(as_jsonl({"sample_key": sample_key}))
        else:
            message = f"KiloToSqlitePreciosClarosTarget.current_sample_home: null sample_key\n" \
                      f"  at {str(juliet_sample_home):s}"
            raise KiloToSqlitePreciosClarosException(message)

    def juliet_points_of_sale(
        self,
        get_points_of_sale: Callable[[Path], Generator[dict[str, str], None, None]]
    ) -> None:
        self.dataset_stats[self.sample_key]["point_of_sale"] += 1
        points_of_sale_resource = get_resource(self.kilo_sample_home, "points_of_sale", ".jsonl")
        with create_text_file(points_of_sale_resource) as points_of_sale:
             for juliet_json in get_points_of_sale(self.juliet_sample_home):
                 kilo_point_of_sale = self.processor.get_point_of_sale(juliet_json)
                 if kilo_point_of_sale:
                     points_of_sale.write(as_jsonl(kilo_point_of_sale))
                     for key, value in kilo_point_of_sale.items():
                         self.points_of_sale_stats[key][value] += 1
                 else:
                     logging.error("KiloToSqlitePreciosClarosTarget.juliet_points_of_sale: " \
                                   "kilo_point_of_sale is None\n" \
                                   f"  check {as_jsonl(juliet_json):s}")

    def juliet_selected_point_of_sale(
        self,
        get_selected_points_of_sale: Callable[[Path], Generator[dict[str, str], None, None]]
    ) -> None:
        self.dataset_stats[self.sample_key]["selected_point_of_sale"] += 1
        selected_points_of_sale_resource = get_resource(self.kilo_sample_home, "selected_points_of_sale", ".jsonl")
        with create_text_file(selected_points_of_sale_resource) as selected_points_of_sale:
             for juliet_json in get_selected_points_of_sale(self.juliet_sample_home):
                 kilo_selected_point_of_sale = self.processor.get_point_of_sale(juliet_json)
                 if kilo_selected_point_of_sale:
                     selected_points_of_sale.write(as_jsonl(kilo_selected_point_of_sale))
                     for key, value in kilo_selected_point_of_sale.items():
                         self.selected_points_of_sale_stats[key][value] += 1
                 else:
                     logging.error("KiloToSqlitePreciosClarosTarget.juliet_selected_points_of_sale: " \
                                   "kilo_point_of_sale is None\n" \
                                   f"  check {as_jsonl(juliet_json):s}")


    def juliet_articles_per_point_of_sale(
        self,
        get_article_per_point_of_sale: Callable[[Path], Generator[dict[str, str], None, None]]
    ) -> None:
        self.dataset_stats[self.sample_key]["articles_per_point_of_sale"] += 1
        articles_per_point_of_sale_resource = get_resource(self.kilo_sample_home, "articles_per_point_of_sale", ".jsonl")
        with create_text_file(articles_per_point_of_sale_resource) as articles_per_point_of_sale:
             for juliet_json in get_article_per_point_of_sale(self.juliet_sample_home):
                 kilo_article_per_point_of_sale = self.processor.get_article_per_point_of_sale(juliet_json)
                 if kilo_article_per_point_of_sale:
                     articles_per_point_of_sale.write(as_jsonl(kilo_article_per_point_of_sale))
                     for key, value in kilo_article_per_point_of_sale.items():
                         self.articles_per_point_of_sale_stats[key][value] += 1
                 else:
                     logging.error("KiloToSqlitePreciosClarosTarget.juliet_articles_per_point_of_sale: " \
                                   "kilo_article_per_point_of_sale is None\n" \
                                   f"  check {as_jsonl(juliet_json):s}")

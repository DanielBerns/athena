from pathlib import Path
from collections import defaultdict, Counter
from typing import DefaultDict

from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.processors_from_juliet import KiloProcessorFromJuliet
from components.core.stats import Stats


class JulietToKiloPreciosClarosTarget:
    def __init__(self, kilo_paths: KiloPaths) -> None:
        self._kilo_paths = kilo_paths
        self._counter_points_of_sale: int = 0
        self._counter_selected_points_of_sale: int = 0
        self._counter_articles_per_point_of_sale: int = 0

        self._total_counter_points_of_sale: int = 0
        self._total_counter_selected_points_of_sale: int = 0
        self._total_counter_articles_per_point_of_sale: int = 0

        # Initialization and type hinting
        self._points_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()
        self._selected_points_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()
        self._articles_per_point_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()

        self._processor = KiloProcessorFromJuliet()

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
    def counter_points_of_sale(self) -> int:
        return self._counter_points_of_sale

    @counter_points_of_sale.setter
    def counter_points_of_sale(self, value: int) -> None:
        self._counter_points_of_sale = value

    @property
    def counter_selected_points_of_sale(self) -> int:
        return self._counter_selected_points_of_sale

    @counter_selected_points_of_sale.setter
    def counter_selected_points_of_sale(self, value: int) -> None:
        self._counter_selected_points_of_sale = value

    @property
    def counter_articles_per_point_of_sale(self) -> int:
        return self._counter_articles_per_point_of_sale

    @counter_articles_per_point_of_sale.setter
    def counter_articles_per_point_of_sale(self, value: int) -> int:
        self._counter_articles_per_point_of_sale = value

    @property
    def total_counter_points_of_sale(self) -> int:
        return self._total_counter_points_of_sale

    @total_counter_points_of_sale.setter
    def total_counter_points_of_sale(self, value: int) -> None:
        self._total_counter_points_of_sale = value

    @property
    def total_counter_selected_points_of_sale(self) -> int:
        return self._total_counter_selected_points_of_sale

    @total_counter_selected_points_of_sale.setter
    def total_counter_selected_points_of_sale(self, value: int) -> None:
        self._total_counter_selected_points_of_sale = value

    @property
    def total_counter_articles_per_point_of_sale(self) -> int:
        return self._total_counter_articles_per_point_of_sale

    @total_counter_articles_per_point_of_sale.setter
    def total_counter_articles_per_point_of_sale(self, value: int) -> int:
        self._total_counter_articles_per_point_of_sale = value

    def juliet_sample_home(self, juliet_sample_home: Path) -> None:
        print(f"{str(juliet_sample_home):s}")

    def juliet_point_of_sale_start(self) -> None:
        self.counter_points_of_sale = 0

    def juliet_point_of_sale(self, a_json_line: dict[str, str]) -> None:
        self.counter_points_of_sale += 1
        for key, value in a_json_line.items():
            self.points_of_sale_stats[key][value] += 1

    def juliet_point_of_sale_stop(self) -> None:
        print(f"Points of sale: {self.counter_points_of_sale:d}")
        self.total_counter_points_of_sale += self.counter_points_of_sale

    def juliet_selected_point_of_sale_start(self) -> None:
        self.counter_selected_points_of_sale = 0

    def juliet_selected_point_of_sale(self, a_json_line: dict[str, str]) -> None:
        self.counter_selected_points_of_sale += 1
        for key, value in a_json_line.items():
            self.selected_points_of_sale_stats[key][value] += 1

    def juliet_selected_point_of_sale_stop(self) -> None:
        print(f"Selected points of sale: {self.counter_selected_points_of_sale:d}")
        self.total_counter_selected_points_of_sale += self.counter_selected_points_of_sale

    def juliet_articles_per_point_of_sale_start(self) -> None:
        self.counter_articles_per_point_of_sale = 0

    def juliet_articles_per_point_of_sale(self, a_json_line: dict[str, str]) -> None:
        self.counter_articles_per_point_of_sale += 1
        for key, value in a_json_line.items():
            self.articles_per_point_of_sale_stats[key][value] += 1

    def juliet_articles_per_point_of_sale_stop(self) -> None:
        print(f"Articles per point of sale: {self.counter_articles_per_point_of_sale:d}")
        self._total_counter_articles_per_point_of_sale += self.counter_articles_per_point_of_sale

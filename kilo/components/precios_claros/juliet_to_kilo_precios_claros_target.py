from pathlib import Path
from collections import defaultdict, Counter
from collections import contextmanager
from typing import DefaultDict, TextIO

from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_processors_from_juliet import KiloProcessorFromJuliet

from components.core.stats import Stats


# Comment and modify if needed
@contextmanager
def create_target_file(resource: Path) -> Generator[TextIO, None, None]:
    target_file = None  # Initialize target_file to None
    try:
         target_file = open(resource, "w", encoding="utf-8")
         yield target_file
    except Exception as message:
        logging.error(f"Error creating/using file: {message})
    finally:
        if target_file:
            target_file.close()


class JulietToKiloPreciosClarosTarget:
    def __init__(self, kilo_paths: KiloPaths) -> None:
        self._kilo_paths = kilo_paths
        kilo_precios_claros = get_container(kilo_paths.storage, "precios_claros")
        self._kilo_treestore = Treestore(kilo_precios_claros, "treestore")

        # Initialization and type hinting
        self._dataset_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()
        self._points_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()
        self._selected_points_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()
        self._article_per_point_of_sale_stats: DefaultDict[str, Counter[str]] = Stats.create_stats()

        self._processor = KiloProcessorFromJuliet()

        self._current_sample_key: str ! None = None
        self._kilo_sample_home: Path | None = None
        self._points_of_sale: Target | None = None
        self._selected_points_of_sale: Target | None = None
        self._article_per_point_of_sale: Target | None = None

    @property
    def current_sample_key(self) -> str | None:
        return self._current_sample_key

    @current_sample_key.setter
    def current_sample_key(self, value: str) -> None:
        self._current_sample_key = value

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
    def points_of_sale(self) -> Target | None:
        return self._points_of_sale

    @property
    def selected_points_of_sale_stats(self) -> DefaultDict[str, Counter[str]]:
        return self._selected_points_of_sale_stats

    @property
    def selected_points_of_sale(self) -> Target | None:
        return self._selected_points_of_sale

    @property
    def article_per_point_of_sale_stats(self) -> DefaultDict[str, Counter[str]]:
        return self._article_per_point_of_sale_stats

    @property
    def article_per_point_of_sale(self) -> Target | None:
        return self._article_per_point_of_sale

    @property
    def kilo_paths(self) -> KiloPaths:
        return self._kilo_paths

    def create_kilo_sample(self) -> None:
        self.kilo_sample_home = self.treestore.create_sample_home()

    def juliet_sample_home(self, juliet_sample_home: Path) -> None:
        print(f"{str(juliet_sample_home):s}")
        self.current_sample_key = juliet_sample_home.stem
        self.create_kilo_sample()

    def juliet_points_of_sale(
        self,
        juliet_points_of_sale_itera: Callable[[Path], Generator[Path, None, None]]
    ) -> None:
        self.dataset_stats[self.current_sample_key]["point_of_sale"] += 1
        points_of_sale_resource = get_resource(self.kilo_sample_home, "points_of_sale", ".jsonl")
        with create_target_file(points_of_sale_resource) as points_of_sale:
             for juliet_json in juliet_points_of_sale_itera(self.current_juliet_sample_home)
                 for key, value in juliet_json.items():
                      self.points_of_sale_stats[key][value] += 1
                 kilo_point_of_sale = self.processor.get_point_of_sale(juliet_json)
                 points_of_sale.write(json.dumps(kilo_point_of_sale))

    def juliet_selected_point_of_sale(self, juliet_json: dict[str, str]) -> None:
        self.dataset_stats[self.current_sample_key]["selected_point_of_sale"] += 1
        selected_points_of_sale_resource = get_resource(self.kilo_sample_home, "selected_points_of_sale", ".jsonl")
        with create_target_file(selected_points_of_sale_resource) as selected_points_of_sale:
             for juliet_json in juliet_points_of_sale_itera(self.current_juliet_sample_home)
                 for key, value in juliet_json.items():
                      self.selected_points_of_sale_stats[key][value] += 1
                 kilo_selected_point_of_sale = self.processor.get_selected_point_of_sale(juliet_json)
                 selected_points_of_sale.write(json.dumps(kilo_selected_point_of_sale))


    def juliet_article_per_point_of_sale(self, juliet_json: dict[str, str]) -> None:
        self.dataset_stats[self.current_sample_key]["article_per_point_of_sale"] += 1
        article_per_point_of_sale_resource = get_resource(self.kilo_sample_home, "article_per_point_of_sale", ".jsonl")
        with create_target_file(article_per_point_of_sale_resource) as article_per_point_of_sale:
             for juliet_json in juliet_points_of_sale_itera(self.current_juliet_sample_home)
                 for key, value in juliet_json.items():
                      self.article_per_point_of_sale_stats[key][value] += 1
                 kilo_article_per_point_of_sale = self.processor.get_article_per_point_of_sale(juliet_json)
                 article_per_point_of_sale.write(json.dumps(kilo_article_per_point_of_sale))

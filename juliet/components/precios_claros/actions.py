from pathlib import Path
from typing import Callable, Dict, Tuple, Optional, List
from components.core import Application, FlatStore, show
from components.configuration import CLI
from components.helpers import get_container, get_timestamp, get_directory, get_resource
from components.nlp.old_sequences import get_patterns
from components.precios_claros.adapters import DeltaChild, DeltaIndex, DeltaRoot
from components.precios_claros.io import IO, Sample
from components.precios_claros.models import ArticleWithPricesTable, PointOfSale

ONE_WORD: int = 1
TWO_CHARACTERS: int = 2



class ActionsException(Exception):
    pass


def show_awp(xxx_test: List[Tuple[PointOfSale, int]]) -> None:
    print("*"*80)
    for awp in xxx_test:
        print(f"article name: {awp.article.name:s} {awp.article.code:s}")
        for pos, price in awp.prices_per_point_of_sale:
            print(f"    {pos.name:>40s} - {price:>8d}")

class Actions:
    @staticmethod
    def create_sample(
        application: Application, select: Callable[[Dict[str, str]], bool]
    ) -> str:
        precios_claros = get_container(
            application.file_system.storage, "precios_claros"
        )
        store = FlatStore(precios_claros, "flatstore")
        store.start()
        timestamp = get_timestamp()
        sample_home = store.sample_home(timestamp)
        sample = Sample(sample_home)
        sample.start()
        IO.write(sample, select)
        sample.stop()
        store.stop()
        return sample.key

    @staticmethod
    def write_origin(
        article_with_prices_table: ArticleWithPricesTable, container: Path
    ) -> Path:
        resource = get_resource(container, "article_names", ".txt")
        with open(resource, "w") as target:
            for line in article_with_prices_table.article_names():
                target.write(line + "\n")
        return resource

    @staticmethod
    def write_target(resource: Path, content: str) -> None:
        show(f"Actions.write_target({str(resource):s})")
        with open(resource, "w") as target:
            target.write(content)

    @staticmethod
    def start(
        application: Application, delta_key: str
    ) -> Tuple[Path, Path, Path, Path]:
        storage: Path = get_container(application.file_system.storage, "precios_claros")
        results: Path = get_container(Path(application.file_system.results, "precios_claros"), delta_key)
        reports_root: Path = get_container(Path(application.file_system.reports), "precios_claros")
        reports: Path = get_container(reports_root, delta_key)
        index_alpha_html: Path = Path(reports_root, "index_alpha").with_suffix(".html")
        
        show(f"    {str(storage):s}")
        show(f"    {str(results):s}")
        show(f"    {str(reports):s}")
        return storage, results, reports, index_alpha_html

    @staticmethod
    def report_delta(
        application: Application, bravo_key: str, alpha_key: str, now_key: str
    ) -> None:
        show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 1")
        delta_root = DeltaRoot(bravo_key, alpha_key, now_key)
        (storage_precios_claros, results_precios_claros, reports_precios_claros, index_alpha_html
        ) = Actions.start(application, delta_root.root_constants.delta_key)
        store = FlatStore(storage_precios_claros, "flatstore")
        store.start()
        show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 2")
        bravo_home = store.sample_home(bravo_key)
        bravo_sample = Sample(bravo_home)
        bravo_points_of_sale_table, bravo_articles_reader = IO.read(bravo_sample)
        alpha_home = store.sample_home(alpha_key)
        alpha_sample = Sample(alpha_home)
        alpha_points_of_sale_table, alpha_articles_reader = IO.read(alpha_sample)
        now_home = store.sample_home(now_key)
        now_sample = Sample(now_home)
        now_points_of_sale_table, now_articles_reader = IO.read(now_sample)
        show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 3")        
        for now_place, now_article_with_prices_table, now_points_of_sale in IO.iterate(now_sample, now_points_of_sale_table, now_articles_reader):
            (bravo_place, bravo_article_with_prices_table, bravo_points_of_sale) = IO.retrieve(
                now_place, bravo_sample, bravo_points_of_sale_table, bravo_articles_reader)
            (alpha_place, alpha_article_with_prices_table, alpha_points_of_sale) = IO.retrieve(
                now_place, alpha_sample, alpha_points_of_sale_table, alpha_articles_reader)
            delta_index = DeltaIndex(delta_root.root_constants, bravo_place, alpha_place, now_place)            
            results_precios_claros_with_place_key = get_container(results_precios_claros, delta_index.index_constants.now_place_key)
            origin = Actions.write_origin(now_article_with_prices_table, results_precios_claros_with_place_key)
            reports_precios_claros_with_place_key = get_container(reports_precios_claros, delta_index.index_constants.now_place_key)
            show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 4")                    
            show(f"    {str(reports_precios_claros_with_place_key):s}")
            for pattern in get_patterns(origin, max_length=ONE_WORD):
                if len(pattern) < TWO_CHARACTERS:
                    show(f"    Actions.report_delta: pattern too short {pattern:s}")
                    continue
                child = delta_index.add(pattern)
                child.fill_table(bravo_article_with_prices_table, bravo_points_of_sale, child.bravo_table)
                bravo_test = [vv for vv in child.bravo_table.values()]
                child.fill_table(alpha_article_with_prices_table, alpha_points_of_sale, child.alpha_table)
                alpha_test = [vv for vv in child.alpha_table.values()]
                child.fill_table(now_article_with_prices_table, now_points_of_sale, child.now_table)
                now_test = [vv for vv in child.now_table.values()]
                show(f"tables {len(bravo_test):d}, {len(alpha_test):d}, {len(now_test):d}")
                # show_awp(bravo_test)
                # show_awp(alpha_test)
                # show_awp(now_test)
                store_key = child.child_constants.store_key
                directory = get_directory(Path(reports_precios_claros_with_place_key, store_key))
                content = child.write()
                resource = get_resource(directory, child.child_constants.name, ".html")
                Actions.write_target(resource, content)
            content = delta_index.write()
            resource = get_resource(
                reports_precios_claros_with_place_key, "index", ".html"
            )
            Actions.write_target(resource, content)
        show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 5")
        content = delta_root.write()
        Actions.write_target(index_alpha_html, content)
            
        store.stop()
        show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 6")

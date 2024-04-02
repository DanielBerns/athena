from pathlib import Path
from typing import Callable, Dict, Tuple
from components.core import Application, FlatStore, show
from components.configuration import CLI
from components.helpers import get_container, get_timestamp, get_directory, get_resource
from components.nlp.sequences import get_patterns
from components.precios_claros.adapters import DeltaChild, DeltaIndex
from components.precios_claros.io import IO, Sample
from components.precios_claros.models import ArticleWithPricesTable, get_place_key
from components.precios_claros.html import HTML_CHILD, HTML_INDEX

import pdb

ONE_WORD: int = 1
TWO_CHARACTERS: int = 2


class ActionsException(Exception):
    pass


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
        sample = IO.build(timestamp, sample_home)
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
    def open_report_delta(
        application: Application, bravo_key: str, alpha_key: str, now_key: str
    ) -> Tuple[Path, str, Path, Path]:
        storage: Path = get_container(application.file_system.storage, "precios_claros")
        delta_key = f"{bravo_key[:8]:s}-{alpha_key[:8]:s}-{now_key[:8]:s}"
        results: Path = get_container(
            Path(application.file_system.results, "precios_claros"), delta_key
        )
        reports: Path = get_container(
            Path(application.file_system.reports, "precios_claros"), delta_key
        )
        show(f"    {str(storage):s}")
        show(f"    {delta_key:s}")
        show(f"    {str(results):s}")
        show(f"    {str(reports):s}")
        return storage, delta_key, results, reports

    @staticmethod
    def report_delta(
        application: Application, bravo_key: str, alpha_key: str, now_key: str
    ) -> None:
        show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 1")
        (
            storage_precios_claros,
            delta_key,
            results_precios_claros,
            reports_precios_claros,
        ) = Actions.open_report_delta(application, bravo_key, alpha_key, now_key)
        store = FlatStore(storage_precios_claros, "flatstore")
        store.start()
        show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 2")
        bravo_home = store.sample_home(bravo_key)
        alpha_home = store.sample_home(alpha_key)
        now_home = store.sample_home(now_key)
        bravo_sample = IO.build(bravo_key, bravo_home)
        alpha_sample = IO.build(alpha_key, alpha_home)
        now_sample = IO.build(now_key, now_home)
        show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 3")
        bravo_points_of_sale_table, bravo_articles_reader = IO.read(bravo_sample)
        alpha_points_of_sale_table, alpha_articles_reader = IO.read(alpha_sample)
        now_points_of_sale_table, now_articles_reader = IO.read(now_sample)
        show(
            f"    bravo_points_of_sale.per_place     : {len(bravo_points_of_sale_table.per_place):d}"
        )
        show(
            f"    bravo_points_of_sale.per_identifier: {len(bravo_points_of_sale_table.per_identifier):d}"
        )
        show(
            f"    bravo_articles                     : {len(bravo_articles_reader.articles_counter):d}"
        )
        show(
            f"    alpha_points_of_sale.per_place     : {len(alpha_points_of_sale_table.per_place):d}"
        )
        show(
            f"    alpha_points_of_sale.per_identifier: {len(alpha_points_of_sale_table.per_identifier):d}"
        )
        show(
            f"    alpha_articles                     : {len(alpha_articles_reader.articles_counter):d}"
        )
        show(
            f"    now_points_of_sale.per_place       : {len(now_points_of_sale_table.per_place):d}"
        )
        show(
            f"    now_points_of_sale.per_identifier  : {len(now_points_of_sale_table.per_identifier):d}"
        )
        show(
            f"    now_articles                       : {len(now_articles_reader.articles_counter):d}"
        )
        show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 4")
        # pdb.set_trace()
        for now_place, now_article_with_prices_table, now_points_of_sale in IO.iterate(
            now_sample, now_points_of_sale_table, now_articles_reader
        ):
            # pdb.set_trace()
            (
                bravo_place,
                bravo_article_with_prices_table,
                bravo_points_of_sale,
            ) = IO.retrieve(
                now_place,
                bravo_sample,
                bravo_points_of_sale_table,
                bravo_articles_reader,
            )
            (
                alpha_place,
                alpha_article_with_prices_table,
                alpha_points_of_sale,
            ) = IO.retrieve(
                now_place,
                alpha_sample,
                alpha_points_of_sale_table,
                alpha_articles_reader,
            )
            bravo_place_key = get_place_key(bravo_place)
            alpha_place_key = get_place_key(alpha_place)
            now_place_key = get_place_key(now_place)
            results_precios_claros_with_place_key = get_container(
                results_precios_claros, now_place_key
            )
            reports_precios_claros_with_place_key = get_container(
                reports_precios_claros, now_place_key
            )
            origin = Actions.write_origin(
                now_article_with_prices_table, results_precios_claros_with_place_key
            )
            parts = now_place.split(":")
            if len(parts) != 2:
                remark = f"Actions.report_delta: bad place {now_place:s}"
                show(remark)
                raise ActionsException(remark)
            # pdb.set_trace()
            index: DeltaIndex = DeltaIndex(
                f"/precios_claros/category/{delta_key:s}/{now_place_key:s}",
                "Punto de venta",
                now_key[:8],
                alpha_key[:8],
                bravo_key[:8],
                province=parts[0],
                city=parts[1],
            )
            show(f"    {str(reports_precios_claros_with_place_key):s}")
            for pattern in get_patterns(origin, max_length=ONE_WORD):
                if len(pattern) < TWO_CHARACTERS:
                    show(f"Actions.report_delta: pattern too short {pattern:s}")
                    continue
                child = index.add(pattern)
                child.fill_now_table(now_article_with_prices_table, now_points_of_sale)
                child.fill_alpha_table(
                    alpha_article_with_prices_table, alpha_points_of_sale
                )
                child.fill_bravo_table(
                    bravo_article_with_prices_table, bravo_points_of_sale
                )
                store_key = child.store_key
                directory = get_directory(
                    Path(reports_precios_claros_with_place_key, store_key)
                )
                content = child.write(HTML_CHILD)
                resource = get_resource(directory, child.name, ".html")
                Actions.write_target(resource, content)
            content = index.write(HTML_INDEX)
            resource = get_resource(
                reports_precios_claros_with_place_key, "index", ".html"
            )
            Actions.write_target(resource, content)
        store.stop()
        show(f"Actions.report_delta({bravo_key:s}, {alpha_key:s}, {now_key:s}) 5")

from pathlib import Path
from typing import Callable, Dict, Tuple
from components.core import Application, FlatStore, show
from components.configuration import CLI
from components.helpers import (get_container, 
                                get_timestamp, 
                                get_directory, 
                                get_resource)
from components.nlp.sequences import get_patterns
from components.precios_claros.adapters import Child, Index, DeltaIndex
from components.precios_claros.io import IO, Sample
from components.precios_claros.models import ArticleWithPricesTable, get_place_key
from components.precios_claros.html import HTML_CHILD, HTML_INDEX

# import pdb

ONE_WORD: int = 1
TWO_CHARACTERS: int = 2

class ActionsException(Exception):
    pass

class Actions:
    @staticmethod
    def create_sample(
        application: Application, 
        select: Callable[[Dict[str, str]], bool]
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
        article_with_prices_table: ArticleWithPricesTable,
        container: Path
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
    
    # @staticmethod
    # def open_report_sample(
    #     application: Application,
    #     sample_key: str
    # ) -> Tuple[Path, Path, Path]:
    #     storage: Path = get_container(
    #         application.file_system.storage, "precios_claros"
    #     )
    #     results: Path = get_container(
    #         Path(application.file_system.results, "precios_claros"), 
    #         sample_key
    #     )
    #     reports: Path = get_container(
    #         Path(application.file_system.reports, "precios_claros"), 
    #         sample_key
    #     )         
    #     show(f"    {str(storage):s}")
    #     show(f"    {str(results):s}")
    #     show(f"    {str(reports):s}")                
    #     return storage, results, reports

    @staticmethod
    def open_report_delta(
        application: Application,
        a_month_ago_key: str,
        a_week_ago_key: str,
        now_key: str
    ) -> Tuple[Path, str, Path, Path]:
        storage: Path = get_container(
            application.file_system.storage, "precios_claros"
        )
        delta_key = f"{a_month_ago_key[:8]:s}-{a_week_ago_key[:8]:s}-{now_key[:8]:s}"
        results: Path = get_container(
            Path(application.file_system.results, "precios_claros"), 
            delta_key
        )
        reports: Path = get_container(
            Path(application.file_system.reports, "precios_claros"), 
            delta_key
        )         
        show(f"    {str(storage):s}")
        show(f"    {delta_key:s}")        
        show(f"    {str(results):s}")
        show(f"    {str(reports):s}")                
        return storage, delta_key, results, reports
    
    # @staticmethod
    # def report_sample(
    #     application: Application,
    #     sample_key: str
    # ) -> None:
    #     show(f"Actions.report_sample({sample_key:s}) 1")
    #     storage_precios_claros, results_precios_claros, reports_precios_claros = \
    #         Actions.open_report_sample(application, sample_key)
    #     store = FlatStore(storage_precios_claros, "flatstore")
    #     store.start()
    #     show(f"Actions.report_sample({sample_key:s}) 2")                
    #     sample_home = store.sample_home(sample_key)
    #     sample = IO.build(sample_key, sample_home)
    #     show(f"Actions.report_sample({sample_key:s}) 3")                
    #     points_of_sale_table, articles_reader = IO.read(sample)
    #     show(f"    points_of_sale.per_place     : {len(points_of_sale_table.per_place):d}")        
    #     show(f"    points_of_sale.per_identifier: {len(points_of_sale_table.per_identifier):d}")        
    #     show(f"    articles                     : {len(articles_reader.articles_counter):d}")
    #     show(f"Actions.report_sample({sample_key:s}) 4")                
    #     for place, article_with_prices_table, points_of_sale in IO.iterate(
    #         sample, 
    #         points_of_sale_table, 
    #         articles_reader
    #     ):
    #         place_key = get_place_key(place)
    #         results_precios_claros_with_place_key = get_container(
    #             results_precios_claros, 
    #             place_key
    #         )
    #         reports_precios_claros_with_place_key = get_container(
    #             reports_precios_claros, 
    #             place_key
    #         )
    #         origin = Actions.write_origin(
    #             article_with_prices_table,
    #             results_precios_claros_with_place_key
    #         )
    #         parts = place.split(':')
    #         if len(parts) != 2:
    #             remark = f"Actions.report_sample: bad place {place:s}"
    #             show(remark)
    #             raise ActionsException(remark)
    #         index: Index = Index(
    #             f"/precios_claros/category/{sample_key:s}/{place_key:s}",
    #             sample_key,
    #             province=parts[0],
    #             city=parts[1]
    #         )
    #         show(f"    {str(reports_precios_claros_with_place_key):s}")
    #         for pattern in get_patterns(origin, max_length=ONE_WORD):
    #             if len(pattern) < TWO_CHARACTERS:
    #                 show(f"Actions.report_sample: pattern too short {pattern:s}")
    #                 continue
    #             child = index.add(pattern)
    #             child.add(
    #                 article_with_prices_table, 
    #                 points_of_sale
    #             )
    #             store_key = child.store_key
    #             directory = get_directory(
    #                 Path(reports_precios_claros_with_place_key, store_key)
    #             )
    #             content = child.write(HTML_CHILD)
    #             resource = get_resource(directory, child.name, ".html")
    #             Actions.write_target(resource, content)                
    #         content = index.write(HTML_INDEX)
    #         resource = get_resource(reports_precios_claros_with_place_key, "index", ".html")
    #         Actions.write_target(resource, content)
    #     store.stop()
    #     show(f"Actions.report_sample({sample_key:s}) 5")                

    @staticmethod
    def report_delta(
        application: Application, 
        a_month_ago_key: str,
        a_week_ago_key: str,
        now_key: str
    ) -> None:
        show(f"Actions.report_delta({a_month_ago_key:s}, {a_week_ago_key:s}, {now_key:s}) 1")
        storage_precios_claros, delta_key, results_precios_claros, reports_precios_claros = \
            Actions.open_report_delta(application, a_month_ago_key, a_week_ago_key, now_key)
        store = FlatStore(storage_precios_claros, "flatstore")
        store.start()
        show(f"Actions.report_delta({a_month_ago_key:s}, {a_week_ago_key:s}, {now_key:s}) 2")
        a_month_ago_home = store.sample_home(a_month_ago_key)        
        a_week_ago_home = store.sample_home(a_week_ago_key)        
        now_home = store.sample_home(now_key)        
        a_month_ago_sample = IO.build(a_month_ago_key, a_month_ago_home)
        a_week_ago_sample = IO.build(a_week_ago_key, a_week_ago_home)                
        now_sample = IO.build(now_key, now_home)        
        show(f"Actions.report_delta({a_month_ago_key:s}, {a_week_ago_key:s}, {now_key:s}) 3")
        a_month_ago_points_of_sale_table, a_month_ago_articles_reader = IO.read(a_month_ago_sample)
        a_week_ago_points_of_sale_table, a_week_ago_articles_reader = IO.read(a_week_ago_sample)        
        now_points_of_sale_table, now_articles_reader = IO.read(now_sample)       
        show(f"    a_month_ago_points_of_sale.per_place     : {len(a_month_ago_points_of_sale_table.per_place):d}")        
        show(f"    a_month_ago_points_of_sale.per_identifier: {len(a_month_ago_points_of_sale_table.per_identifier):d}")        
        show(f"    a_month_ago_articles                     : {len(a_month_ago_articles_reader.articles_counter):d}")
        show(f"    a_week_ago_points_of_sale.per_place      : {len(a_week_ago_points_of_sale_table.per_place):d}")        
        show(f"    a_week_ago_points_of_sale.per_identifier : {len(a_week_ago_points_of_sale_table.per_identifier):d}")        
        show(f"    a_week_ago_articles                      : {len(a_week_ago_articles_reader.articles_counter):d}")
        show(f"    now_points_of_sale.per_place             : {len(now_points_of_sale_table.per_place):d}")        
        show(f"    now_points_of_sale.per_identifier        : {len(now_points_of_sale_table.per_identifier):d}")        
        show(f"    now_articles                             : {len(now_articles_reader.articles_counter):d}")
        show(f"Actions.report_delta({a_month_ago_key:s}, {a_week_ago_key:s}, {now_key:s}) 4")
        # pdb.set_trace()
        for now_place, now_article_with_prices_table, now_points_of_sale in IO.iterate(
            now_sample, 
            now_points_of_sale_table, 
            now_articles_reader
        ):
            a_month_ago_place, a_month_ago_article_with_prices_table, a_month_ago_points_of_sale = IO.retrieve(
                now_place,
                a_month_ago_sample,
                a_month_ago_points_of_sale_table,
                a_month_ago_articles_reader
            )
            a_week_ago_place, a_week_ago_article_with_prices_table, a_week_ago_points_of_sale = IO.retrieve(
                now_place,
                a_week_ago_sample,
                a_week_ago_points_of_sale_table,
                a_week_ago_articles_reader
            )
            a_month_ago_place_key = get_place_key(a_month_ago_place)
            a_week_ago_place_key = get_place_key(a_week_ago_place)            
            now_place_key = get_place_key(now_place)
            results_precios_claros_with_place_key = get_container(
                results_precios_claros, 
                now_place_key
            )
            reports_precios_claros_with_place_key = get_container(
                reports_precios_claros, 
                now_place_key
            )
            origin = Actions.write_origin(
                now_article_with_prices_table,
                results_precios_claros_with_place_key
            )
            parts = now_place.split(':')
            if len(parts) != 2:
                remark = f"Actions.report_delta: bad place {now_place:s}"
                show(remark)
                raise ActionsException(remark)
            # pdb.set_trace()
            index: DeltaIndex = DeltaIndex(
                f"/precios_claros/category/{delta_key:s}/{now_place_key:s}",
                now_key,
                province=parts[0],
                city=parts[1]
            )
            show(f"    {str(reports_precios_claros_with_place_key):s}")
            for pattern in get_patterns(origin, max_length=ONE_WORD):
                if len(pattern) < TWO_CHARACTERS:
                    show(f"Actions.report_delta: pattern too short {pattern:s}")
                    continue
                child = index.add(pattern)
                child.fill_reference_table(
                    now_article_with_prices_table, 
                    now_points_of_sale
                )
                child.fill_a_month_ago_table(
                    a_month_ago_article_with_prices_table, 
                    a_month_ago_points_of_sale
                )                    
                child.fill_a_week_ago_table(
                    a_week_ago_article_with_prices_table, 
                    a_week_ago_points_of_sale
                )                    
                store_key = child.store_key
                directory = get_directory(
                    Path(reports_precios_claros_with_place_key, store_key)
                )
                content = child.write(HTML_CHILD)
                resource = get_resource(directory, child.name, ".html")
                Actions.write_target(resource, content)                
            content = index.write(HTML_INDEX)
            resource = get_resource(reports_precios_claros_with_place_key, "index", ".html")
            Actions.write_target(resource, content)
        store.stop()
        show(f"Actions.report_delta({a_month_ago_key:s}, {a_week_ago_key:s}, {now_key:s}) 5")

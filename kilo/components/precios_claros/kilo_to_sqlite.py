import logging

from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_iterator import KiloPreciosClarosIterator
from components.precios_claros.kilo_precios_claros_target import KiloPreciosClarosTarget
from components.precios_claros.kilo_to_sqlite_precios_claros_target import KiloToSqlitePreciosClarosTarget

from components.core.stats import Stats
from components.helpers import get_container


def kilo_to_sqlite_precios_claros_process_storage(kilo_paths: KiloPaths) -> None:
    target = KiloToSqlitePreciosClarosTarget(kilo_paths)
    kilo_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    kilo_precios_claros_sqlite = get_container(kilo_precios_claros, "sqlite")
    for kilo_sample_home in KiloPreciosClarosIterator.get_sample_home(kilo_precios_claros):
        try:
            target.current_sample_home(kilo_sample_home)
            target.kilo_points_of_sale(KiloPreciosClarosIterator.get_points_of_sale)
            target.kilo_selected_point_of_sale(KiloPreciosClarosIterator.get_selected_points_of_sale)
            target.kilo_articles_per_point_of_sale(KiloPreciosClarosIterator.get_articles_per_point_of_sale)
        except Exception as message:
            logging.error(f"*** Error: {str(message):s}")
        # break

    Stats.write_stats("points_of_sale", target.points_of_sale_stats, kilo_paths.reports)
    Stats.write_stats("selected_points_of_sale", target.selected_points_of_sale_stats, kilo_paths.reports)
    Stats.write_stats("articles_per_point_of_sale", target.articles_per_point_of_sale_stats, kilo_paths.reports)
    Stats.write_stats("dataset", target.dataset_stats, kilo_paths.reports)

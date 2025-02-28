import logging
from components.juliet.juliet_paths import JulietPaths
from components.precios_claros.juliet_precios_claros_iterator import JulietPreciosClarosIterator
from components.precios_claros.juliet_precios_claros_target import JulietPreciosClarosTarget
from components.precios_claros.juliet_to_kilo_precios_claros_target import JulietToKiloPreciosClarosTarget

from components.kilo.kilo_paths import KiloPaths
from components.core.stats import Stats
from components.helpers import get_container


def juliet_to_kilo_precios_claros_process_storage(juliet_paths: JulietPaths, kilo_paths: KiloPaths) -> None:
    target = JulietToKiloPreciosClarosTarget(kilo_paths)
    juliet_precios_claros = get_container(juliet_paths.storage, "precios_claros")
    juliet_precios_claros_flatstore = get_container(juliet_precios_claros, "flatstore")
    for juliet_sample_home in JulietPreciosClarosIterator.get_sample_home(juliet_precios_claros_flatstore):
        try:
            target.current_sample_home(juliet_sample_home)
            target.juliet_points_of_sale(JulietPreciosClarosIterator.get_points_of_sale)
            target.juliet_selected_point_of_sale(JulietPreciosClarosIterator.get_selected_points_of_sale)
            target.juliet_articles_per_point_of_sale(JulietPreciosClarosIterator.get_articles_per_point_of_sale)
        except Exception as message:
            logging.error(f"*** Error: {str(message):s}")
        # break

    Stats.write_stats("points_of_sale", target.points_of_sale_stats, kilo_paths.reports)
    Stats.write_stats("selected_points_of_sale", target.selected_points_of_sale_stats, kilo_paths.reports)
    Stats.write_stats("articles_per_point_of_sale", target.articles_per_point_of_sale_stats, kilo_paths.reports)
    Stats.write_stats("dataset", target.dataset_stats, kilo_paths.reports)

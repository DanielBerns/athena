import logging

from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_reader import KiloPreciosClarosReader
from components.precios_claros.kilo_precios_claros_target import KiloPreciosClarosTarget

from components.helpers.helpers import get_container
from components.core.tree_store import TreeStore


class KiloPreciosClarosProcessor:
    def __init__(
        self
    ) -> None:
        pass

    def execute(
        self,
        reader: KiloPreciosClarosReader,
        target: KiloPreciosClarosTarget
    ) -> None:
        for current_sample_home in reader.read_sample_home():
            try:
                logging.info(f"{current_sample_home}")
                target.current_sample_home = current_sample_home
                target.kilo_points_of_sale(reader.read_points_of_sale)
                target.kilo_selected_point_of_sale(reader.read_selected_points_of_sale)
                target.kilo_articles_per_point_of_sale(reader.read_articles_per_point_of_sale)
            except Exception as message:
                logging.error(f"*** Error: {str(message):s}")

        # Stats.write("points_of_sale", target.points_of_sale_stats, kilo_paths.reports)
        # Stats.write("selected_points_of_sale", target.selected_points_of_sale_stats, kilo_paths.reports)
        # Stats.write("articles_per_point_of_sale", target.articles_per_point_of_sale_stats, kilo_paths.reports)
        # Stats.write("dataset", target.dataset_stats, kilo_paths.reports)

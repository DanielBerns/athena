# import pdb
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
        target: KiloPreciosClarosTarget,
        start: int,
        stop: int
    ) -> None:
        for count, current_sample_home in enumerate(reader.read_sample_home()):
            if count < start:
                logging.info(f"Skipped ({count}) - {str(current_sample_home):s}")
                continue
            try:
                logging.info(f"Start ({count}) - {current_sample_home}")
                target.current_sample_home = current_sample_home
                target.kilo_points_of_sale(reader.read_points_of_sale)
                target.kilo_selected_point_of_sale(reader.read_selected_points_of_sale)
                target.kilo_articles_per_point_of_sale(reader.read_articles_per_point_of_sale)
                logging.info(f"Done ({count}) - {current_sample_home}")
            except Exception as message:
                logging.error(f"*** Error: {str(message):s}")
            if stop > 0:
               if count > stop:
                   break



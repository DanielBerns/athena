import pdb
import os
import logging

from components.juliet import JulietPaths
from components.precios_claros.juliet_precios_claros_reader_simple import JulietPreciosClarosReaderSimple
from components.precios_claros.kilo_juliet_precios_claros_reader import KiloJulietPreciosClarosReader

from components.precios_claros.juliet_precios_claros_processor import JulietPreciosClarosProcessor
from components.kilo import KiloPaths
from components.precios_claros.juliet_to_kilo_precios_claros_target import JulietToKiloPreciosClarosTarget

from components.core.stats import Stats
from components.helpers.helpers import get_resource


def main() -> None:
    # script identifier,
    identifier = "translate_juliet_to_kilo_precios_claros"
    print(f"{__file__}", " - ", identifier)
    # log levels
    #     logging.NOTSET,
    #     logging.DEBUG,
    #     logging.INFO,
    #     logging.WARN,
    #     logging.ERROR,
    #     logging.CRITICAL,
    #
    log_level = logging.DEBUG
    mode = "live"

    juliet_paths = JulietPaths(mode)
    kilo_paths = KiloPaths(mode)

    # log_txt = str(get_resource_with_timestamp(kilo_paths.logs, identifier, ".txt"))
    log_txt = str(get_resource(kilo_paths.logs, identifier, ".txt"))


    logging.basicConfig(
        filename=log_txt,
        filemode="w",
        level=log_level,
        format="%(levelname)s > %(message)s",
    )

    logging.info("start")
    processor = JulietPreciosClarosProcessor(juliet_paths)
    juliet_store_home = processor.juliet_store_home
    pdb.set_trace()
    first_sample = os.environ.get("FIRST_SAMPLE", "0")
    juliet_reader = JulietPreciosClarosReaderSimple(juliet_store_home, first_sample)
    kilo_juliet_reader = KiloJulietPreciosClarosReader(juliet_reader)
    target = JulietToKiloPreciosClarosTarget(kilo_paths)
    processor.execute(kilo_juliet_reader, target)

    Stats.write("points_of_sale", target.points_of_sale_stats, kilo_paths.reports)
    Stats.write("selected_points_of_sale", target.selected_points_of_sale_stats, kilo_paths.reports)
    Stats.write("articles_per_point_of_sale", target.articles_per_point_of_sale_stats, kilo_paths.reports)
    Stats.write("dataset", target.dataset_stats, kilo_paths.reports)

    logging.info("stop")

if __name__ == "__main__":
    main()

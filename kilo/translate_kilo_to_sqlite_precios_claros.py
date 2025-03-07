import logging
from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_basic_reader import KiloPreciosClarosBasicReader
from components.precios_claros.kilo_to_sqlite_precios_claros_target import KiloToSqlitePreciosClarosTarget
from components.precios_claros.kilo_precios_claros_processor import KiloPreciosClarosProcessor

from components.helpers.helpers import get_container, get_resource

def main() -> None:
    # script identifier,
    identifier = "translate_kilo_to_sqlite_precios_claros"
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

    processor = KiloPreciosClarosProcessor()
    kilo_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    kilo_reader = KiloPreciosClarosBasicReader(kilo_precios_claros)
    target = KiloToSqlitePreciosClarosTarget(kilo_paths)
    processor.execute(kilo_reader, target)

    Stats.write("points_of_sale", target.points_of_sale_stats, kilo_paths.reports)
    Stats.write("selected_points_of_sale", target.selected_points_of_sale_stats, kilo_paths.reports)
    Stats.write("articles_per_point_of_sale", target.articles_per_point_of_sale_stats, kilo_paths.reports)
    Stats.write("dataset", target.dataset_stats, kilo_paths.reports)

    logging.info("stop")

if __name__ == "__main__":
    main()


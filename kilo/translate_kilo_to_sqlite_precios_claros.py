import logging
from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_basic_reader import KiloPreciosClarosBasicReader
from components.precios_claros.kilo_to_sqlite_precios_claros_target import KiloToSqlitePreciosClarosTarget
from components.precios_claros.kilo_precios_claros_processor import KiloPreciosClarosProcessor
from components.precios_claros.database_api import create_sqlite_database

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
    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    results_precios_claros = get_container(kilo_paths.results, "precios_claros")

    kilo_reader = KiloPreciosClarosBasicReader(storage_precios_claros)
    target = KiloToSqlitePreciosClarosTarget(kilo_paths)
    processor.execute(kilo_reader, target)

    target.dirty_timestamps.write(results_precios_claros)
    target.dirty_states.write(results_precios_claros)
    target.dirty_cities.write(results_precios_claros)
    target.dirty_places.write(results_precios_claros)
    target.dirty_point_of_sale_codes.write(results_precios_claros)
    target.dirty_point_of_sale_representations.write(results_precios_claros)
    target.dirty_article_codes.write(results_precios_claros)
    target.dirty_article_representations.write(results_precios_claros)
    target.dirty_prices.write(results_precios_claros)

    create_sqlite_database(
        kilo_paths,
        target.dirty_timestamps,
        target.dirty_states,
        target.dirty_cities,
        target.dirty_places,
        target.dirty_point_of_sale_codes,
        target.dirty_point_of_sale_representations,
        target.dirty_article_codes,
        target.dirty_article_representations,
        target.dirty_prices
    )


    logging.info("stop")

if __name__ == "__main__":
    main()


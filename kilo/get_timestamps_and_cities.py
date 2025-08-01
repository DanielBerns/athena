from typing import List, Generator, Tuple
from collections import defaultdict
import logging
import os
from pathlib import Path
from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_basic_reader import KiloPreciosClarosBasicReader
from components.precios_claros.db_kilo_precios_claros_reader import (
    DBKiloPreciosClarosReader,
    DBStatesGenerator,
    DBCitiesGenerator
)
from components.precios_claros.database import db_get_session
from components.precios_claros.db_interface_basic_queries import (
    DBInterfaceBasicQueries,
    geometric_mean_times_100
)
from components.helpers.helpers import get_container, get_resource, create_text_file, read_text_lines, measure_execution_time

logger = logging.getLogger(__file__)

class DatabaseQueriesException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logger.error(message)

DB_NAME = os.environ.get("DB_NAME", "mecon_dev")


def main() -> None:
    # script identifier,
    identifier = Path(__file__).stem
    print(f"{__file__}", " - ", identifier)
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


    logging.info(f"{identifier} start")
    logging.info(f"DB_NAME: {DB_NAME}")
    logging.info("--------------------")
    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    reports_precios_claros = get_container(kilo_paths.reports, "precios_claros")

    parameters_container = get_container(storage_precios_claros, "parameters")

    db_uri = str(get_resource(storage_precios_claros_sqlite, DB_NAME, ".db"))
    with db_get_session(db_uri) as session:
        db = DBInterfaceBasicQueries(session)
        db.get_all_the_cities()
        db.get_all_the_places()
        db.get_all_the_points_of_sale()
        db.get_all_the_article_codes()
        db.get_all_the_article_cards()
        db.get_all_the_timestamps()

        report_file = get_resource(reports_precios_claros, "timestamps", ".txt")
        with create_text_file(report_file) as text_file:
            for key, _ in db.all_the_timestamps.items():
                text_file.write(key + "\n")

        report_file = get_resource(reports_precios_claros, "cities", ".txt")
        with create_text_file(report_file) as text_file:
            for key, _ in db.all_the_cities.items():
                text_file.write(key + "\n")

    logging.info(f"{identifier} stop")


if __name__ == "__main__":
    main()


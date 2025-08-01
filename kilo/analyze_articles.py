import pdb
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
    description_set_resource = get_resource(reports_precios_claros, "descriptions", ".txt")
    brand_set_resource = get_resource(reports_precios_claros, "brand", ".txt")
    package_alpha_set_resource = get_resource(reports_precios_claros, "package_alpha_set", ".txt")
    package_bravo_set_resource = get_resource(reports_precios_claros, "package_bravo_set", ".txt")
    package_charlie_set_resource = get_resource(reports_precios_claros, "package_charlie_set", ".txt")
    check_this_resource = get_resource(reports_precios_claros, "check_this", ".txt")

    db_uri = str(get_resource(storage_precios_claros_sqlite, DB_NAME, ".db"))
    with db_get_session(db_uri) as session:
        db = DBInterfaceBasicQueries(session)
        db.get_all_the_states()
        db.get_all_the_cities()
        db.get_all_the_places()
        db.get_all_the_points_of_sale()
        db.get_all_the_article_codes()
        db.get_all_the_article_cards()
        db.get_all_the_timestamps()

        description_set: dict[str, bool] = {}
        brand_set: dict[str, bool] = {}
        check_this: List[int] = []
        package_alpha_set: dict[str, bool] = {}
        package_bravo_set: dict[str, bool] = {}
        package_charlie_set: dict[Tuple[str, str], bool] = {}

        pdb.set_trace()
        for key, article_card in db.all_the_article_cards.items():
            description, brand = article_card.description, article_card.brand
            clean_description, clean_brand = description.strip(), brand.strip()
            parts = clean_description.split(clean_brand)
            description_set[parts[0]] = True
            brand_set[clean_brand] = True
            if len(parts) == 2:
                alpha = parts[1]
                bravo = article_card.package
                charlie = (alpha, bravo)
                package_alpha_set[alpha] = True
                package_bravo_set[bravo] = True
                package_charlie_set[charlie] = True
            else:
                check_this.append(f"{article_card.id} - {clean_description} - {clean_brand}")

        with create_text_file(description_set_resource) as text:
            for description, test in description_set.items():
                text.write(f"{description}\n")

        with create_text_file(brand_set_resource) as text:
            for brand, test in brand_set.items():
                text.write(f"{brand}\n")

        with create_text_file(package_alpha_set_resource) as text:
            for package, test in package_alpha_set.items():
                text.write(f"{package}\n")

        with create_text_file(package_bravo_set_resource) as text:
            for package, test in package_bravo_set.items():
                text.write(f"{package_alpha}\n")

        with create_text_file(package_charlie_set_resource) as text:
            for package_charlie, test in package_charlie_set.items():
                text.write(f"{package_charlie[0]}: {package_charlie[1]}\n")

        with create_text_file(check_this_resource) as text:
            for message in check_this:
                text.write(f"{message}\n")

    logging.info(f"{identifier} stop")


if __name__ == "__main__":
    # 20250529
    main()


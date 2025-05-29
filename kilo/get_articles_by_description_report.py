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

from components.precios_claros.db_new_interface import db_get_new_interface
from components.precios_claros.db_precios_claros_new_interface import DBPreciosClarosNewInterface
from components.helpers.helpers import get_container, get_resource, measure_execution_time, create_text_file


def get_reader(storage_precios_claros: Path) -> DBKiloPreciosClarosReader:
    _reader = KiloPreciosClarosBasicReader(storage_precios_claros)
    return DBKiloPreciosClarosReader(_reader)

def main() -> None:
    # script identifier,
    identifier = Path(__file__).stem
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

    log_txt = str(get_resource(kilo_paths.logs, identifier, ".txt"))


    logging.basicConfig(
        filename=log_txt,
        filemode="w",
        level=log_level,
        format="%(levelname)s > %(message)s",
    )

    logging.info(f"{identifier} start")

    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    reports_precios_claros = get_container(kilo_paths.reports, "precios_claros")
    articles_report = get_resource(reports_precios_claros, "article_descriptions", ".csv")
    factory = lambda s: DBPreciosClarosNewInterface(s)
    with db_get_new_interface(storage_precios_claros, factory) as db, \
         create_text_file(articles_report) as report:
        known_article_codes: dict[str, bool] = {}
        for count, article_card in enumerate(db.query_ordered_article_cards(10)):
            article_code = article_card.article_code
            if known_article_codes.get(article_code.code, False):
                pass
            else:
                known_article_codes[article_code.code] = True
                for index, card in enumerate(article_code.cards):
                    report.write(f"{(card.description).strip()}|{(card.package).strip()}|{(card.brand).strip()}\n")

    logging.info(f"{identifier} stop")
    return 0

if __name__ == "__main__":
    (result, execution_time) = measure_execution_time(main)
    logging.info(f"Execution time (secs): {execution_time:>6.12f}")


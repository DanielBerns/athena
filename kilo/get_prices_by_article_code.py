import pdb
import logging
import os
from pathlib import Path
from components.kilo.kilo_paths import KiloPaths


from components.precios_claros.db_new_interface import db_get_new_interface
from components.precios_claros.db_precios_claros_new_interface import DBPreciosClarosNewInterface
from components.helpers.helpers import get_container, get_resource, measure_execution_time, create_text_file


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
    articles_report = get_resource(reports_precios_claros, "prices_by_article_code", ".csv")
    factory = lambda s: DBPreciosClarosNewInterface(s)
    pdb.set_trace()
    with db_get_new_interface(storage_precios_claros, factory) as db, \
         create_text_file(articles_report) as report:
        known_article_codes: dict[str, bool] = {}
        known_article_codes["7790070506917"] = True
        known_article_codes["7790070506924"] = True
        known_article_codes["7790272004457"] = True
        for key, value in known_article_codes.items():
            for count, price in enumerate(db.query_prices_by_article_code_ordered_by_timestamp(key)):
                pdb.set_trace()
                article_code = price.article_code
                card = article_code.cards[0]
                timestamp = price.timestamp
                pos = price.point_of_sale
                report.write(f"{count:>6d}|{str(timestamp)}|{article_code.code}|{price.amount/100:>6.2f}|")
                report.write(f"{card.brand}|{card.description}|{card.package}|{pos.flag}|{pos.place.city.name}\n")

    logging.info(f"{identifier} stop")
    return 0

if __name__ == "__main__":
    (result, execution_time) = measure_execution_time(main)
    logging.info(f"Execution time (secs): {execution_time:>6.12f}")


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
    parameters_container = get_container(storage_precios_claros, "parameters")
    known_article_codes_resource = get_resource(parameters_container, "article_codes", ".txt")
    known_article_codes: dict[str, bool] = {}
    if known_article_codes.exists():
        for line in read_text_lines(known_article_codes_resource):
            this_article_code = line.strip()
            known_article_codes[this_article_code] = True
    cities_resource = get_resource(parameters_container, "cities", ".txt")
    cities: dict[str, bool] = {}
    if cities_resource.exists():
        for line in read_text_lines(cities_resource):
            this_city = line.strip()
            cities[this_city] = True
    sample_keys_resource = get_resource(parameters, "sample_keys", ".txt")
    sample_keys = ][]
    if sample_keys_resource.exists()
        for line in read_text_lines(sample_keys_resource):
            this_sample_key = line.strip()
            sample_keys.append(this_sample_key)

    separator = "="*150
    for city_name, city_value in cities.items():
        city_underscore = city_name.replace(' ', '_')
        articles_report = get_resource(reports_precios_claros, f"prices_{city_underscore}", ".csv")
        factory = lambda s: DBPreciosClarosNewInterface(s)
        with db_get_new_interface(storage_precios_claros, factory) as db, \
            create_text_file(articles_report) as report:
            for a_sample_key in sample_keys:
                for article_code_value, _ in known_article_codes.items():
                    for count, price in enumerate(db.query_prices_by_article_code_city_and_timestamp(
                        article_code_value,
                        city_name,
                        a_sample_key
                    )):
                        article_code = price.article_code
                        card = article_code.cards[0]
                        timestamp = price.timestamp
                        pos = price.point_of_sale
                        price_string = f"{price.amount/100:>8.2f}"
                        report.write(f"{count:>6d}|{str(timestamp)}|{article_code.code}|{price_string}|")
                        report.write(f"{card.brand}|{card.description}|{card.package}|{pos.flag}|{pos.place.city.name}\n")
                report.write(f"{separator}\n")

    logging.info(f"{identifier} stop")
    return 0

if __name__ == "__main__":
    (result, execution_time) = measure_execution_time(main)
    logging.info(f"Execution time (secs): {execution_time:>6.12f}")


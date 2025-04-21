# import pdb
import logging
import os
from pathlib import Path
from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_basic_reader import KiloPreciosClarosBasicReader
from components.precios_claros.db_kilo_precios_claros_reader import (
    DBKiloPreciosClarosReader,
    DBStatesGenerator,
    DBCitiesGenerator,
    DBPlacesGenerator,
    DBPointsOfSalesGenerator,
    DBArticleCodesGenerator,
    DBArticleCardsGenerator,
    DBTimestampsGenerator,
    DBPricesGenerator
)

from components.precios_claros.database import db_get_session
from components.precios_claros.db_interface_new_precios_claros import DBInterfaceNewPreciosClaros
from components.helpers.helpers import get_container, get_resource, measure_execution_time

INSERT_PRICES = os.environ.get("INSERT_PRICES", "NO")
FIRST_SAMPLE = os.environ.get("FIRST_SAMPLE", "0")
TOP_SAMPLE = os.environ.get("TOP_SAMPLE", "-1")
DB_NAME = os.environ.get("DB_NAME", "mecon_dev")


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

    # log_txt = str(get_resource_with_timestamp(kilo_paths.logs, identifier, ".txt"))
    log_txt = str(get_resource(kilo_paths.logs, identifier, ".txt"))

    logging.basicConfig(
        filename=log_txt,
        filemode="w",
        level=log_level,
        format="%(levelname)s > %(message)s",
    )

    logging.info(f"{identifier} start")
    try:
        first_sample = int(FIRST_SAMPLE)
    except Exception:
        first_sample = 0
    try:
        top_sample = int(TOP_SAMPLE)
    except Exception:
        top_sample = -1

    insert_prices = INSERT_PRICES == "YES"

    logging.info(f"first sample = {FIRST_SAMPLE} > {first_sample}")
    logging.info(f"top sample = {TOP_SAMPLE} > {top_sample}")
    logging.info(f"insert prices = {INSERT_PRICES } > {insert_prices}")

    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    db_uri = str(get_resource(storage_precios_claros_sqlite, "mecon_dev", ".db"))
    with db_get_session(db_uri) as session:
        db = DBInterfaceNewPreciosClaros(session)
        _reader = KiloPreciosClarosBasicReader(storage_precios_claros)
        reader = DBKiloPreciosClarosReader(_reader)
        if insert_prices:
            # pdb.set_trace()
            # db.get_all_states()
            # db.get_all_the_cities()
            # db.get_all_the_places()
            db.get_all_the_points_of_sale()
            db.get_all_the_article_codes()
            # db.get_all_the_article_cards()
            db.get_all_the_timestamps()
            db_prices = DBPricesGenerator(
                reader,
                db.all_the_timestamps,
                db.all_the_article_codes,
                db.all_the_points_of_sale,
            )
            reader.first_sample = first_sample
            reader.top_sample = top_sample
            for sample_home, sample_key in reader.samples_generator():
                db.insert_prices(db_prices.iterate)
        else:
            db_timestamps = DBTimestampsGenerator(reader)
            db.insert_timestamps(db_timestamps.iterate)

            db_states = DBStatesGenerator(reader)
            db_cities = DBCitiesGenerator(reader, db_states.table)
            db_places = DBPlacesGenerator(reader, db_cities.table)
            db_points_of_sale = DBPointsOfSalesGenerator(reader, db_places.table)
            db_article_codes = DBArticleCodesGenerator(reader)
            db_article_cards = DBArticleCardsGenerator(reader, db_article_codes.table)

            db.insert_states(db_states.iterate)
            db.insert_cities(db_cities.iterate)
            db.insert_places(db_places.iterate)
            db.insert_points_of_sale(db_points_of_sale.iterate)
            db.insert_article_codes(db_article_codes.iterate)
            db.insert_article_cards(db_article_cards.iterate)

    logging.info(f"{identifier} stop")
    return 0

if __name__ == "__main__":
    task = lambda : main()
    (result, time) = measure_execution_time(task)
    logging.info(f"Result: {result} - time: {time}")


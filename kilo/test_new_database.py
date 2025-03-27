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
from components.precios_claros.db_interface_with_bulk_insert import DBInterfaceWithBulkInsert
from components.helpers.helpers import get_container, get_resource, measure_execution_time

FIRST_SAMPLE = os.environ.get("FIRST_SAMPLE", "-1")
LAST_SAMPLE = os.environ.get("LAST_SAMPLE", "-1")

# import pdb

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
        first_sample = -1
    try:
        last_sample = int(last_SAMPLE)
    except Exception:
        last_sample = -1

    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    factory = lambda s: DBInterfaceWithBulkInsert(s)
    with db_get_new_interface(storage_precios_claros, factory) as db:
        db.get_all_the_states()
        states = DBStatesGenerator(get_reader(storage_precios_claros))
        for a_state in states.iterate():
            db_state = db.query_state(a_state["code"])
            if db_state:
                logging.info(f"{db_state.code} - {db_state.name}")
            else:
                logging.info(f"None db_state for {str(a_state)}")
        db.get_all_the_cities()
        for a_key, a_city in db.all_the_cities.items():
            logging.info(f"    {a_key} :: {a_city.name} at {a_city.state.name} - {a_city.state.code}")
        db.get_all_the_places()
        for a_key, a_place in db.all_the_places.items():
            logging.info(f"    {a_key} :: {a_place.address} {a_place.city.name} at {a_place.city.state.name} - {a_place.city.state.code}")
        db.get_all_the_points_of_sale()
        for a_key, pos in db.all_the_points_of_sale.items():
            logging.info(f"    {a_key} :: {pos.flag} {pos.business} at {pos.branch} - {pos.place.address} - {pos.place.city.name}")
        db.get_all_the_article_codes()
        for a_key, ac in db.all_the_article_codes.items():
            logging.info(f"    {a_key} :: {ac.code}")
        db.get_all_the_article_cards()
        for a_key, ac in db.all_the_article_cards.items():
            logging.info(f"    {a_key} :: {ac.article_code.code} [[{len(ac.article_code.cards)}]] {ac.brand}")


    logging.info(f"{identifier} stop")

if __name__ == "__main__":
    main()


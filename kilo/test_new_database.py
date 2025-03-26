import logging
import os
from pathlib import Path
from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_basic_reader import KiloPreciosClarosBasicReader
from components.precios_claros.db_kilo_precios_claros_reader import DBKiloPreciosClarosReader, DBStatesGenerator

from components.precios_claros.db_new_interface import db_get_new_interface
from components.precios_claros.db_interface_with_bulk_insert import DBInterfaceWithBulkInsert
from components.helpers.helpers import get_container, get_resource, measure_execution_time

FIRST_SAMPLE = os.environ.get("FIRST_SAMPLE", "-1")
LAST_SAMPLE = os.environ.get("LAST_SAMPLE", "-1")

import pdb

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
        _reader = KiloPreciosClarosBasicReader(storage_precios_claros)
        reader = DBKiloPreciosClarosReader(_reader)
        states = DBStatesGenerator(reader)
        pdb.set_trace()
        for a_state in states.iterate():
            db_state = db.query_state(a_state["code"])
            if db_state:
                logging.info(f"{db_state.code} - {db_state.name}")
            else:
                logging.info(f"None db_state for {str(a_state)}")
    logging.info(f"{identifier} stop")

if __name__ == "__main__":
    main()


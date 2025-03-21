import logging
from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_basic_reader import KiloPreciosClarosBasicReader
from components.precios_claros.db_target import DBTarget
from components.precios_claros.kilo_to_sqlite_precios_claros_target import KiloToSqlitePreciosClarosTarget
from components.precios_claros.kilo_precios_claros_processor import KiloPreciosClarosProcessor
from components.precios_claros.db_interface import db_get_interface
from components.precios_claros.db_interface_with_test import DBInterfaceWithTest
from components.precios_claros.db_basic_target import DBBasicTarget
from components.helpers.helpers import get_container, get_resource

FIRST = 196
LAST = -1

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

    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    factory = lambda s: DBInterfaceWithTest(s)
    with db_get_interface(storage_precios_claros, factory) as db:
        db_target = DBBasicTarget(db)
        reader = KiloPreciosClarosBasicReader(storage_precios_claros)
        target = KiloToSqlitePreciosClarosTarget(db_target)
        processor = KiloPreciosClarosProcessor()
        processor.execute(reader, target, FIRST, LAST)

    logging.info("stop")

if __name__ == "__main__":
    main()


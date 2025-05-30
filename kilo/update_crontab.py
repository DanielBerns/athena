from pathlib import Path

from components.core.crontab import update_crontab_table
from components.kilo.kilo_paths import KiloPaths

from components.helpers.helpers import get_container, get_resource

import logging

logger = logging.getLogger(__file__)

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
    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    storage_precios_claros_crontab = get_container(storage_precios_claros, "crontab")
    crontab_txt = get_resource(storage_precios_claros_crontab, "crontab", ".txt")

    with update_crontab_table(crontab_txt) as crontab:
        crontab.add("1", "~/Commands/test.sh", "1 * * * *")
        for key, value in crontab.table.items():
            print(key, value)

if __name__ == "__main__":
    main()

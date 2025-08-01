import pdb
import os
from math import log, pow
from typing import List, Generator, Tuple
import logging
from pathlib import Path
from components.kilo.kilo_paths import KiloPaths

from components.precios_claros.report_by_brand import Report, ReportBuilder

from components.helpers.helpers import get_container, get_resource


class ReportTarget:
    def __init__(self, container: Path) -> None:
        self._container = container

    @property
    def container(self) -> Path:
        return self._container

    def write(self, report: Report) -> None:
        print(report.city.name)

DB_NAME = os.environ.get("DB_NAME", "mecon_dev")

def main() -> None:
    # script identifier,
    identifier = Path(__file__).stem
    print(f"{__file__}", " - ", identifier)
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
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    reports_precios_claros = get_container(kilo_paths.reports, "precios_claros")
    db_uri = str(get_resource(storage_precios_claros_sqlite, DB_NAME, ".db"))

    report_builder = ReportBuilder()
    report_target = ReportTarget(reports_precios_claros)
    state_code = "ar-u"
    timestamp_str = "20201028183600"
    report_builder.execute(
        db_uri,
        timestamp_str,
        state_code,
        report_target
        )

    logging.info(f"{identifier} stop")


if __name__ == "__main__":
    main()


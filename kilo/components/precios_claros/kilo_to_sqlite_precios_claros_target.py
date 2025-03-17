import logging
from pathlib import Path
from collections.abc import Callable
from collections import Counter
from typing import TextIO, Generator, DefaultDict


from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.db_target import DBTarget
from components.dirty_events.dirty_events import DirtyEvents
from components.core.stats import Stats
from components.helpers import (
    get_container,
    get_resource,
    get_stringy,
    as_jsonl,
    create_text_file,
    classname,
    read_json)


class KiloToSqlitePreciosClarosException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


class KiloToSqlitePreciosClarosTarget:
    def __init__(
        self,
        db_target: DBTarget,
        ) -> None:
        self._db_target = db_target

    @property
    def db_target(self) -> DBTarget:
        return self._db_target

    @property
    def current_sample_home(self) -> Path:
        return self.db_target.current_sample_home

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        self.db_target.current_sample_home = value

    def kilo_points_of_sale(
        self,
        read_points_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        logging.info(f"{classname(self):s}.kilo_points_of_sale start")
        try:
           for event in read_points_of_sale():
               self.db_target.kilo_points_of_sale(event)
        except Exception as panic:
            logging.error(f"*** Error")
            logging.error(f"    event: {str(event)}")
            message = f"*** Error {classname(self):s}.kilo_points_of_sale ({classname(panic)}): {str(panic):s}"
            raise KiloToSqlitePreciosClarosException(message)
        logging.info(f"{classname(self):s}.kilo_points_of_sale done")

    def kilo_selected_point_of_sale(
        self,
        read_selected_points_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        logging.info(f"{classname(self):s}.kilo_selected_points_of_sale start")
        try:
            for event in read_selected_points_of_sale():
                pass
            logging.info("done")
        except Exception as panic:
            message = f"{classname(self):s}.kilo_selected_point_of_sale ({classname(panic):s}): {str(panic):s}"
            raise KiloToSqlitePreciosClarosException(message)
        logging.info(f"{classname(self):s}.kilo_selected_points_of_sale done")


    def kilo_articles_per_point_of_sale(
        self,
        read_articles_per_point_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        logging.info(f"{classname(self):s}.kilo_articles_per_point_of_sale start")
        try:
            for event in read_articles_per_point_of_sale():
                self.db_target.kilo_articles_per_point_of_sale(event)
        except Exception as panic:
            self.skip_sample = True
            message = f"{classname(self):s}.kilo_articles_per_point_of_sale ({classname(panic):s}): {str(panic):s}"
            raise KiloToSqlitePreciosClarosException(message)
        logging.info(f"{classname(self):s}.kilo_articles_per_point_of_sale done")


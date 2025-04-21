import logging
from contextlib import contextmanager
from collections.abc import Callable
from pathlib import Path
from typing import Generator
from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from components.core.logged_exception import LoggedException
from components.helpers.helpers import classname, get_container, get_stringy

from components.precios_claros.database import (
    get_int,
    ArticleCode,
    ArticleCard,
    State,
    City,
    Place,
    PointOfSale,
    Timestamp,
    Price
)

from components.precios_claros.kilo_keys import KiloKeys


class DBInterfaceInsertion:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def insert_timestamps(
        self,
        known_sample_keys: Callable[[], Generator[str, None, None]]
    ) -> None:
        logging.info(f"{classname(self):s}.insert_timestamps start")
        try:
            bulk = [ {
                "year": get_int(sample_key[0:4]),
                "month": get_int(sample_key[4:6]),
                "day": get_int(sample_key[6:8]),
                "hour": get_int(sample_key[8:10]),
                "minute": get_int(sample_key[10:12]),
                "second": get_int(sample_key[12:14])
                } for sample_key in known_sample_keys()
            ]
            self.session.execute(insert(Timestamp), bulk)
            self.session.commit()
            self.get_all_the_timestamps()
            logging.info(f"{classname(self):s}.insert_timestamps ({len(self.all_the_timestamps)}) stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_timestamps ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)
        logging.info(f"{classname(self):s}.insert_timestamps done")

    def insert_states(
        self,
        known_states: Generator[dict[str, str], None, None]
    ) -> None:
        logging.info(f"{classname(self):s}.insert_states start")
        try:
            bulk = [
                {"code": record["code"],
                 "name": record["name"]
                }
                for record in known_states()
            ]
            for rr in bulk:
                logging.info(f"{str(rr)}")
            self.session.execute(insert(State), bulk)
            self.session.commit()
        except Exception as panic:
            self.session.rollback()
            logging.error( "*** Error State")
            logging.error(f"    states: {str(known_states):s}")
            message = f"*** Error {classname(self):s}.insert_states ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)
        logging.info(f"{classname(self):s}.insert_states stop")

    def insert_cities(
        self,
        known_cities: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        logging.info(f"{classname(self):s}.insert_cities start")
        try:
            bulk = [
                {"name": record["city"],
                 "state_id": self.query_state(record["state"]).id
                } for record in known_cities()]
            self.session.execute(insert(City), bulk)
            self.session.commit()
            logging.info(f"{classname(self):s}.insert_cities stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_cities ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)
        logging.info(f"{classname(self):s}.insert_cities done")

    def insert_places(
        self,
        known_places: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        logging.info(f"{classname(self):s}.insert_places start")
        try:
            bulk = [
                {"address": record["address"],
                 "city_id": self.look_for_city_id(record["city_key"])
                } for record in known_places()
            ]
            self.session.execute(insert(Place), bulk)
            self.session.commit()
            logging.info(f"{classname(self):s}.insert_places stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_places ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)
        logging.info(f"{classname(self):s}.insert_places done")


    def insert_points_of_sale(
        self,
        known_points_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ):
        logging.info(f"{classname(self):s}.insert_points_of_sale start")
        try:
            bulk = [
                {"code": record["point_of_sale_key"],
                 "flag": record["flag"],
                 "business": record["business"],
                 "branch": record["branch"],
                 "place_id": self.look_for_place_id(record["place_key"])
                } for record in known_points_of_sale()
            ]
            self.session.execute(insert(PointOfSale), bulk)
            self.session.commit()
            self.get_all_the_points_of_sale()
            logging.info(f"{classname(self):s}.insert_points_of_sale ({len(self.all_the_points_of_sale)}) stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_points_of_sale ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)

    def insert_article_codes(
        self,
        known_article_codes: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        logging.info(f"{classname(self)}.insert_article_codes start")
        try:
            bulk = [
                {"code": record["article_code"]
                } for record in known_article_codes()
            ]
            self.session.execute(insert(ArticleCode), bulk)
            self.session.commit()
            self.get_all_the_article_codes()
            logging.info(f"{classname(self)}.insert_article_codes ({len(self.all_the_article_codes)}) stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_article_codes ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)


    def insert_article_cards(
        self,
        known_article_cards:  Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        logging.info(f"{classname(self)}.insert_article_cards start")
        try:
            bulk = [
                { "brand": record["brand"],
                  "description": record["description"],
                  "package": record["package"],
                  "article_code_id": self.look_for_article_code_id(record["article_code"])
                } for record in known_article_cards()
            ]
            self.session.execute(insert(ArticleCard), bulk)
            self.session.commit()
            self.get_all_the_article_cards()
            logging.info(f"{classname(self)}.insert_article_cards ({len(self.all_the_article_cards)}) stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_article_cards ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)


    def insert_prices(
        self,
        known_prices:  Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        logging.info(f"{classname(self)}.insert_prices start")
        try:
            bulk = [
                { "amount": record["price"],
                  "timestamp_id": self.look_for_timestamp_id(record["sample_key"]),
                  "article_code_id": self.look_for_article_code_id(record["article_code"]),
                  "point_of_sale_id": self.look_for_point_of_sale_id(record["point_of_sale_code"])
                } for record in known_prices()
            ]
            self.session.execute(insert(Price), bulk)
            self.session.commit()
            logging.info(f"{classname(self)}.insert_prices stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_prices ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)


@contextmanager
def get_interface_insertion(
    session: Session,
) -> Generator[DBInterfaceInsertion, None, None]:
     try:
         db = DBInterfaceInsertion(session)
         db.update_cache()
         yield db
     except Exception as panic:
         message = f"*** Error db_insertion.interface.get_insertion_interface ({classname(panic)}) {str(panic):s}"
         raise LoggedException(message)

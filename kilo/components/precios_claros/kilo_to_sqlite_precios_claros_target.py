import pdb

import logging
from pathlib import Path
from collections.abc import Callable
from collections import Counter
from typing import TextIO, Generator, DefaultDict


from components.kilo.kilo_paths import KiloPaths
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
    def __init__(self, kilo_paths: KiloPaths) -> None:
        self._kilo_paths = kilo_paths
        kilo_precios_claros = get_container(kilo_paths.storage, "precios_claros")
        self._kilo_precios_claros_sqlite = get_container(kilo_precios_claros, "sqlite")
        self._sample_key: str | None = None
        self._current_sample_home: Path | None = None
        self._skip_sample = False
        self._points_of_sale: dict[str, str] = dict()

        self._dirty_timestamps = DirtyEvents("dirty_timestamps")
        self._dirty_states = DirtyEvents("dirty_states")
        self._dirty_cities = DirtyEvents("dirty_cities")
        self._dirty_places = DirtyEvents("dirty_places")
        self._dirty_point_of_sale_codes = DirtyEvents("dirty_point_of_sale_codes")
        self._dirty_point_of_sale_representations = DirtyEvents("dirty_point_of_sale_representations")
        self._dirty_article_codes = DirtyEvents("dirty_article_codes")
        self._dirty_article_representations = DirtyEvents("dirty_article_representations")
        self._dirty_prices = DirtyEvents("dirty_prices")

    @property
    def kilo_paths(self) -> KiloPaths:
        return self._kilo_paths

    @property
    def kilo_precios_claros_sqlite(self) -> Path:
        return self._kilo_precios_claros_db

    @property
    def sample_key(self) -> str | None:
        return self._sample_key

    @sample_key.setter
    def sample_key(self, value: str) -> None:
        self._sample_key = value

    @property
    def current_sample_home(self) -> Path:
        return self._current_sample_home

    @property
    def skip_sample(self) -> bool:
        return self._skip_sample

    @skip_sample.setter
    def skip_sample(self, value: bool) -> None:
        self._skip_sample = value

    @property
    def points_of_sale(self) -> dict[str, str]:
        return self._points_of_sale

    @property
    def dirty_timestamps(self) -> DirtyEvents:
        return self._dirty_timestamps

    @property
    def dirty_states(self) -> DirtyEvents:
        return self._dirty_states

    @property
    def dirty_cities(self) -> DirtyEvents:
        return self._dirty_cities

    @property
    def dirty_places(self) -> DirtyEvents:
        return self._dirty_places

    @property
    def dirty_point_of_sale_codes(self) -> DirtyEvents:
        return self._dirty_point_of_sale_codes

    @property
    def dirty_point_of_sale_representations(self) -> DirtyEvents:
        return self._dirty_point_of_sale_representations

    @property
    def dirty_article_codes(self) -> DirtyEvents:
        return self._dirty_article_codes

    @property
    def dirty_article_representations(self) -> DirtyEvents:
        return self._dirty_article_representations

    @property
    def dirty_prices(self) -> DirtyEvents:
        return self._dirty_prices

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        self.skip_sample = False
        self._current_sample_home = value
        try:
            resource = get_resource(self.current_sample_home, "metadata", ".json")
            metadata = read_json(resource)
            self.sample_key = sk = metadata["sample_key"]
            dirty_timestamp = {
                "timestamp": sk,
                "year": sk[0:4],
                "month": sk[4:6],
                "day": sk[6:8],
                "hour": sk[8:10],
                "minute": sk[10:12],
                "second": sk[12:14]
            }
            self.dirty_timestamps.add("timestamp", dirty_timestamp)
        except Exception as message:
            logging.error(f"*** ERROR -{classname(self):s}.current_sample_home: {str(message):s}")
            logging.error(f"    skipping sample: {str(value):s}")
            self.skip_sample = True

    def get_new_point_of_sale_code(self, point_of_sale_code: str, business: str) -> str:
        self.points_of_sale[point_of_sale_code] = result = f"[{point_of_sale_code:s}]-- {business:s}"
        return result

    def kilo_points_of_sale(
        self,
        read_points_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        if self.skip_sample:
            logging.info("skipped")
        else:
            try:
               for event in read_points_of_sale():
                   state_code = event["state"]
                   city = event["city"]
                   address = event["address"]
                   point_of_sale_code = event["point_of_sale_code"]
                   flag = event["flag"]
                   business = event["business"]
                   branch = event["branch"]
                   new_point_of_sale_code = self.get_new_point_of_sale_code(
                       point_of_sale_code, business
                   )
                   self.points_of_sale[point_of_sale_code] = new_point_of_sale_code
                   stringy_city = get_stringy([state_code, city])
                   stringy_place = get_stringy([state_code, city, address])
                   stringy_representation = get_stringy([flag, business, branch, point_of_sale_code])
                   dirty_state = {"state_code": state_code}
                   dirty_city = {
                       "name": city,
                       "state_code": state_code,
                       "stringy_city": stringy_city
                   }
                   dirty_place = {
                       "city": city,
                       "address": address,
                       "state_code": state_code,
                       "stringy_city": stringy_city,
                       "stringy_place": stringy_place
                   }
                   dirty_point_of_sale_code = {
                       "point_of_sale_code": new_point_of_sale_code,
                       "state_code": state_code,
                       "stringy_city": stringy_city,
                       "stringy_place": stringy_place
                   }
                   dirty_point_of_sale_representation = {
                       "flag": flag,
                       "business": business,
                       "branch": branch,
                       "point_of_sale_code": new_point_of_sale_code,
                       "timestamp": self.sample_key,
                       "stringy_representation": stringy_representation,
                       "stringy_place": stringy_place,
                   }
                   self.dirty_states.add(
                       "state_code",
                       dirty_state
                   )
                   self.dirty_cities.add(
                       "stringy_city",
                       dirty_city
                   )
                   self.dirty_places.add("stringy_place", dirty_place)
                   self.dirty_point_of_sale_codes.add("point_of_sale_code", dirty_point_of_sale_code)
                   self.dirty_point_of_sale_representations.add("stringy_representation", dirty_point_of_sale_representation)

               logging.info("done")
            except Exception as message:
                self.skip_sample = True
                logging.error(f"{classname(self):s}.kilo_points_of_sale: {str(message):s}")

    def kilo_selected_point_of_sale(
        self,
        read_selected_points_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        if self.skip_sample:
            logging.info(f"{self.sample_key:s}: selected_point_of_sale skipped")
        else:
            try:
                for event in read_selected_points_of_sale():
                    pass
                logging.info("done")
            except Exception as message:
                self.skip_sample = True
                logging.error(f"{classname(self):s}.kilo_selected_point_of_sale: {str(message):s}")


    def kilo_articles_per_point_of_sale(
        self,
        read_articles_per_point_of_sale: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        if self.skip_sample:
            logging.info(f"{self.sample_key:s}: articles_per_point_of_sale skipped")
        else:
            try:
                for event in read_articles_per_point_of_sale():
                    dirty_article_code = {
                        "article_code": event["article_code"]
                    }
                    dirty_article_representation = {
                        "article_code": event["article_code"],
                        "brand": event["brand"],
                        "description": event["description"],
                        "package": event["package"]
                    }
                    dirty_price = {
                        "amount": event["price"],
                        "timestamp": self.sample_key,
                        "article_code": event["article_code"],
                        "point_of_sale_code": self.points_of_sale[event["point_of_sale_code"]]
                    }
                    self.dirty_article_codes.add("article_code", dirty_article_code)
                    self.dirty_article_representations.add("article_code", dirty_article_representation)
                    self.dirty_prices.add("article_code", dirty_price)
                logging.info(f"{self.sample_key:s}: articles_per_point_of_sale done")
            except Exception as message:
                self.skip_sample = True
                logging.error(f"{classname(self):s}.kilo_articles_per_point_of_sale: {str(message):s}")


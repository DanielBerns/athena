import logging
from contextlib import contextmanager
from collections.abc import Callable
from pathlib import Path
from typing import Generator, Tuple, Optional
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
    Price,
)

from components.precios_claros.kilo_keys import KiloKeys
import sqlalchemy as sa
from sqlalchemy.orm import Session


def geometric_mean_times_100(column: sa.Column) -> sa.Function:
    """
    Calculates the geometric mean of a column, multiplies it by 100,
    and returns the integer part.  This is implemented using SQLAlchemy
    functions.

    Args:
        column: The SQLAlchemy column to calculate the geometric mean of.

    Returns:
        A SQLAlchemy function representing the calculated value.
    """
    return sa.cast(100 * (sa.func.power(10, sa.func.avg(sa.func.log(column)) - 2)), sa.Integer)


class DBInterfaceBasicQueries:
    def __init__(self, session: Session) -> None:
        self._session = session

        self._map_of_points_of_sale_code_string: dict[str, str] = dict()

        self._all_the_states: dict[str, State] = {}
        self._all_the_timestamps: dict[str, Timestamp] = {}
        self._all_the_cities: dict[str, City] = {}
        self._all_the_places: dict[str, Place] = {}
        self._all_the_article_codes: dict[str, ArticleCode] = {}
        self._all_the_article_cards: dict[str, ArticleCard] = {}
        self._all_the_points_of_sale: dict[str, PointOfSale] = {}

    @property
    def session(self) -> Session:
        return self._session

    def new_point_of_sale_code_string(
        self, point_of_sale_code_string: str, business: str
    ) -> str:
        return f"[{point_of_sale_code_string:s}]--({business:s})"

    @property
    def map_of_points_of_sale_code_string(self) -> dict[str, str]:
        return self._map_of_points_of_sale_string

    @property
    def all_the_states(self) -> dict[str, State]:
        return self._all_the_states

    @property
    def all_the_cities(self) -> dict[str, City]:
        return self._all_the_cities

    @property
    def all_the_places(self) -> dict[str, Place]:
        return self._all_the_places

    @property
    def all_the_points_of_sale(self) -> dict[str, PointOfSale]:
        return self._all_the_points_of_sale

    @property
    def all_the_article_codes(self) -> dict[str, ArticleCode]:
        return self._all_the_article_codes

    @property
    def all_the_article_cards(self) -> dict[str, ArticleCard]:
        return self._all_the_article_cards

    @property
    def all_the_timestamps(self) -> dict[str, Timestamp]:
        return self._all_the_timestamps

    def update_cache(self) -> None:
        logging.info(f"{classname(self)}.update_cache start")
        self.get_all_the_states()
        self.get_all_the_cities()
        self.get_all_the_places()
        self.get_all_the_points_of_sale()
        self.get_all_the_article_codes()
        self.get_all_the_article_cards()
        self.get_all_the_timestamps()
        logging.info(f"{classname(self)}.update_cache stop")

    def query_timestamp(self, sample_key: str) -> Timestamp | None:
        try:
            logging.info(f"{classname(self):s}.query_timestamp start")
            existing_timestamp = self.all_the_timestamps.get(sample_key, None)
            if existing_timestamp:
                logging.info(
                    f"{classname(self):s}.query_timestamp: ({str(existing_timestamp):s}) in database already"
                )
            logging.info(f"{classname(self):s}.query_timestamp stop")
            return existing_timestamp
        except Exception as panic:
            logging.error(f"*** Error {classname(self):s}.query_timestamp")
            logging.error(f"    {year} {month} {day} {hour} {minute} {second}")
            message = f"*** Error {classname(self):s}.query_timestamp  ({len(self.all_the_timestamps)})({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)

    def look_for_timestamp_id(self, sample_key: str) -> int:
        existing_timestamp = self.all_the_timestamps.get(sample_key, None)
        if existing_timestamp:
            return existing_timestamp.id
        else:
            message = f"*** Error {classname(self)}.look_for_timestamp_id: {sample_key}"
            raise LoggedException(message)

    def query_state(self, state_code: str) -> State | None:
        logging.info(f"{classname(self)}.query_state start")
        try:
            logging.info(f"    {state_code}")
            existing_state = self.all_the_states.get(state_code, None)
            if existing_state is None:
                logging.error(f"*** Error: no state")
            logging.info(f"{classname(self)}.query_state stop")
            return existing_state
        except Exception as panic:
            logging.error(f"*** Error {classname(self)}.query_state")
            logging.error(f"    state_code: {state_code:s}")
            for key, state in self.all_the_states.items():
                logging.error(f"    key: {key} - state {state.name}")
            message = f"*** Error {classname(self)}.query_state: {classname(panic)}"
            raise LoggedException(message)

    def query_city(self, name: str, city_state: State) -> City:
        logging.info(f"{classname(self):s}.query_city start")
        try:
            city_key = KiloKeys.city_key(city_state.code, name)
            existing_city = self.all_the_cities.get(city_key, None)
            if existing_city:
                logging.info(
                    f"{classname(self):s}.query_city: {name:s} at {city_state.name:s} in database already"
                )
                logging.info(f"{classname(self):s}.query_city stop")
                return existing_city
        except Exception as panic:
            self.session.rollback()
            logging.error(f"*** Error {classname(self):s}.query_city")
            logging.error(f"   city name: {name:s}")
            logging.error(f"       state: {city_state.code} - {city_state.name}")
            message = f"*** Error {classname(self):s}.get_city ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)

    def look_for_city_id(self, city_key: str) -> int:
        existing_city = self.all_the_cities[city_key]
        if existing_city:
            return existing_city.id
        else:
            message = f"*** Error {classname(self)}.look_for_city: {city_key}"
            raise LoggedException(message)

    def query_place(self, address: str, place_city: City) -> Place | None:
        logging.info(f"{classname(self):s}.query_place start")
        try:
            place_key = KiloKeys.place_key(
                place_city.state.code, place_city.name, address
            )
            existing_place = self.all_the_places.get(place_key, None)
            return existing_place
        except Exception as panic:
            logging.error(f"*** Error {classname(self):s}.query_place")
            logging.error(f"    place address: {str(address)}")
            logging.error(f"             city: {str(place_city)}")
            message = f"*** Error {classname(self):s}.query_place ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)

    def look_for_place_id(self, place_key: str) -> int:
        existing_place = self.all_the_places.get(place_key, None)
        if existing_place:
            return existing_place.id
        else:
            message = f"*** Error {classname(self)}.look_for_place: {place_key}"
            raise LoggedException(message)

    def query_point_of_sale(self, code: str) -> PointOfSale | None:
        logging.info(f"{classname(self):s}.query_point_of_sale start")
        try:
            existing_point_of_sale = self.all_the_points_of_sale.get(code, None)
            return existing_point_of_sale
        except Exception as panic:
            logging.error(f"*** Error {classname(self):s}.query_point_of_sale")
            logging.error(f"    code: {code}")
            message = f"*** Error {classname(self):s}.query_point_of_sale ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)

    def look_for_point_of_sale_id(self, point_of_sale_code: str) -> int:
        existing_point_of_sale = self.all_the_points_of_sale[point_of_sale_code]
        if existing_point_of_sale:
            return existing_point_of_sale.id
        else:
            message = f"*** Error {classname(self)}.look_for_article_code_id: {point_of_sale_code}"
            raise LoggedException(message)

    def query_article_code(self, code: str) -> Place | None:
        logging.info(f"{classname(self):s}.query_article_code start")
        try:
            existing_article_code = self.all_the_article_codes.get(code, None)
            return existing_article_code
        except Exception as panic:
            logging.error(f"*** Error {classname(self):s}.query_article_code")
            logging.error(f"    code: {code}")
            message = f"*** Error {classname(self):s}.query_article_code ({classname(panic):s}): {str(panic):s}"
            raise LoggedException(message)

    def look_for_article_code_id(self, article_code_string: str) -> int:
        existing_article_code = self.all_the_article_codes[article_code_string]
        if existing_article_code:
            return existing_article_code.id
        else:
            message = (
                f"*** Error {classname(self)}.look_for_article_code_id: {article_code}"
            )
            raise LoggedException(message)

    def get_all_the_states(self) -> None:
        statement = select(State)
        _all_the_states = list(self.session.scalars(statement).all())
        self.all_the_states.update(
            {a_state.code: a_state for a_state in _all_the_states}
        )

    def get_all_the_cities(self) -> None:
        statement = select(City)
        _all_the_cities = list(self.session.scalars(statement).all())
        self.all_the_cities.update(
            {
                KiloKeys.city_key(a_city.state.code, a_city.name): a_city
                for a_city in _all_the_cities
            }
        )

    def get_all_the_places(self) -> None:
        statement = select(Place)
        _all_the_places = list(self.session.scalars(statement).all())
        self.all_the_places.update(
            {
                KiloKeys.place_key(
                    a_place.city.state.code, a_place.city.name, a_place.address
                ): a_place
                for a_place in _all_the_places
            }
        )

    def get_all_the_points_of_sale(self) -> None:
        statement = select(PointOfSale)
        _all_the_points_of_sale = list(self.session.scalars(statement).all())
        self.all_the_points_of_sale.update(
            {pos.code: pos for pos in _all_the_points_of_sale}
        )

    def get_all_the_timestamps(self) -> None:
        statement = select(Timestamp)
        _all_the_timestamps = list(self.session.scalars(statement).all())
        self.all_the_timestamps.update({repr(ts): ts for ts in _all_the_timestamps})

    def get_all_the_article_codes(self) -> None:
        statement = select(ArticleCode)
        _all_the_article_codes = list(self.session.scalars(statement).all())
        self.all_the_article_codes.update(
            {ac.code: ac for ac in _all_the_article_codes}
        )

    def get_all_the_article_cards(self) -> None:
        statement = select(ArticleCard)
        _all_the_article_cards = list(self.session.scalars(statement).all())
        self.all_the_article_cards.update(
            {
                KiloKeys.article_card_key(
                    ac.article_code.code, ac.brand, ac.description, ac.package
                ): ac
                for ac in _all_the_article_cards
            }
        )

    def query_article_cards_ordered_by_brand_description_and_package(
        self,
        batch_size: int = 100
    ) -> Generator[ArticleCard, None, None]:
        """Queries article_cards ordered by brand, description, and package."""
        query = self.session.query(ArticleCard).order_by(
            ArticleCard.brand, ArticleCard.description, ArticleCard.package
        )
        for row in query.yield_per(batch_size):
            yield row

    def query_article_cards_ordered_by_description_package_and_brand(
        self,
        batch_size: int = 100
    ) -> Generator[ArticleCard, None, None]:
        """Queries article_cards ordered by description, package and brand."""
        query = self.session.query(ArticleCard).order_by(
            ArticleCard.description, ArticleCard.package, ArticleCard.brand
        )
        for row in query.yield_per(batch_size):
            yield row

    def query_ordered_article_codes(
        self,
        batch_size: int = 100
    ) -> Generator[ArticleCode, None, None]:
        """Queries article_cards ordered by brand, description, and package."""
        query = self.session.query(ArticleCode).order_by(ArticleCode.code)
        for row in query.yield_per(batch_size):
            yield row

    def query_prices_by_article_code(
        self,
        article_code_value: str,
        batch_size: int = 100
    ) -> Generator[Price, None, None]:
        """
        Iterates through prices for a given ArticleCode, ordered by their timestamps in batches.

        Args:
            article_code_value: The code of the ArticleCode to filter by.
            batch_size: The number of prices to fetch in each batch.

        Yields:
            Price objects ordered by their associated timestamp.
        """
        query = (
            self.session.query(Price)
            .join(Price.article_code)
            .join(Price.timestamp)
            .filter(ArticleCode.code == article_code_value)
            .order_by(
                Timestamp.year,
                Timestamp.month,
                Timestamp.day,
                Timestamp.hour,
                Timestamp.minute,
                Timestamp.second,
            )
        )
        for row in query.yield_per(batch_size):
            yield row

    def query_prices_by_article_code_and_city(
        self,
        article_code_value: str,
        city_name: str,
        batch_size: int = 100
    ) -> Generator[Price, None, None]:
        """
        Queries for prices associated with a given ArticleCode and city,
        ordered by timestamp and then by point of sale code.

        Args:
            article_code_value: The code of the ArticleCode to filter by.
            city_name: The name of the City to filter by.
            batch_size: retrieve all the data in batches
        Returns:
            A list of Price objects ordered first by timestamp and then by point of sale code.
        """
        query = (
            self.session.query(Price)
            .join(Price.article_code)
            .join(Price.timestamp)
            .join(Price.point_of_sale)
            .join(PointOfSale.place)
            .join(Place.city)
            .filter(ArticleCode.code == article_code_value, City.name == city_name)
            .order_by(
                Timestamp.year,
                Timestamp.month,
                Timestamp.day,
                Timestamp.hour,
                Timestamp.minute,
                Timestamp.second,
                PointOfSale.code,  # Order by point of sale code
            )
        )
        for row in query.yield_per(batch_size):
            yield row

    def query_prices_by_article_code_city_and_timestamp(
        self,
        article_code_value: str,
        city_name: str,
        target_timestamp: str,
        batch_size: int = 100,
    ) -> Generator[Price, None, None]:
        """
        Queries for prices associated with a given ArticleCode, city, and timestamp,
        ordered by timestamp and then by point of sale code.

        Args:
            article_code_value: The code of the ArticleCode to filter by.
            city_name: The name of the City to filter by.
            target_timestamp: The specific datetime to filter by.
            batch_size: retrieve all the data in batches

        Returns:
            A list of Price objects ordered first by timestamp and then by point of sale code.
        """
        target_ts = Timestamp.from_string(target_timestamp)
        query = (
            self.session.query(Price)
            .join(Price.article_code)
            .join(Price.timestamp)
            .join(Price.point_of_sale)
            .join(PointOfSale.place)
            .join(Place.city)
            .filter(
                ArticleCode.code == article_code_value,
                City.name == city_name,
                Timestamp.year == target_ts.year,
                Timestamp.month == target_ts.month,
                Timestamp.day == target_ts.day,
                Timestamp.hour == target_ts.hour,
                Timestamp.minute == target_ts.minute,
                Timestamp.second == target_ts.second,
            )
            .order_by(
                Timestamp.year,
                Timestamp.month,
                Timestamp.day,
                Timestamp.hour,
                Timestamp.minute,
                Timestamp.second,
                City.name,
                PointOfSale.code,
            )
        )
        for row in query.yield_per(batch_size):
            yield row


    def get_prices_by_article_code_city_and_timestamp(
        self,
        city_name: str,
        timestamp_str: str,
        aggregation_function: Callable[[sa.Column], sa.Function] = sa.func.avg,
        batch_size: int = 100,
    ) -> Generator[Tuple[str, Optional[int], Optional[int], Optional[int]], None, None]:
        """
        Retrieves the minimum, maximum, and a custom aggregated price for each article code
        within a specified city and at a given timestamp.

        Args:
            city_name: The name of the city to filter by.
            timestamp_str: timestamp to filter by, str format.
            aggregation_func: The SQLAlchemy function to use for aggregation
                (e.g., sa.func.avg, sa.func.min, sa.func.max, or a custom function).
                Defaults to sa.func.avg (arithmetic average).

        Returns:
            A list of tuples. Each tuple contains:
            - The article code (str).
            - The minimum price (int or None).
            - The maximum price (int or None).
            - The aggregated price, calculated using aggregation_func (int or None).
        """
        # Convert the datetime object into a Timestamp object using the from_datetime method.
        timestamp_obj = Timestamp.from_string(timestamp_str)

        # Construct the SQLAlchemy query.
        query = self.session.query(
            ArticleCode.code,
            sa.func.min(Price.amount).label("min_price"),
            sa.func.max(Price.amount).label("max_price"),
            aggregation_function(Price.amount).label("geomean_price"),
        )\
        .join(Price, Price.article_code_id == ArticleCode.id)\
        .join(PointOfSale, Price.point_of_sale_id == PointOfSale.id)\
        .join(Place, PointOfSale.place_id == Place.id)\
        .join(City, Place.city_id == City.id)\
        .join(Timestamp, Price.timestamp_id == Timestamp.id)\
        .filter(City.name == city_name)\
        .filter(Timestamp.year == timestamp_obj.year,
                Timestamp.month == timestamp_obj.month,
                Timestamp.day == timestamp_obj.day,
                Timestamp.hour == timestamp_obj.hour,
                Timestamp.minute == timestamp_obj.minute,
                Timestamp.second == timestamp_obj.second)\
        .group_by(ArticleCode.code)

        for row in query.yield_per(batch_size):
            yield row

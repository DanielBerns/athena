import pdb

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from components.helpers.helpers import classname, get_container, get_stringy

from components.precios_claros.database import (
    DatabaseException,
    get_int,
    State,
    City,
    Place,
    PointOfSale,
    Timestamp,
    ArticleCode,
    ArticleCard,
    Price
)
from components.precios_claros.db_interface import CODES_AND_STATES




class DBInterfaceWithQuery:
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

    def new_point_of_sale_code_string(self, point_of_sale_code_string: str, business: str) -> str:
        return f"[{point_of_sale_code_string:s}]--({business:s})"

    @property
    def map_of_points_of_sale_code_string(self) -> dict[str, str]:
        return self._map_of_points_of_sale_code_string

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
    def all_the_timestamps(self) -> dict[str, Timestamp]:
        return self._all_the_timestamps

    @property
    def all_the_points_of_sale(self) -> dict[str, PointOfSale]:
        return self._all_the_points_of_sale

    @property
    def all_the_article_codes(self) -> dict[str, ArticleCode]:
        return self._all_the_article_codes

    @property
    def all_the_article_cards(self) -> dict[str, ArticleCard]:
        return self._all_the_article_cards

    def update_cache(self) -> None:
        logging.info(f"{classname(self)}.update_cache start")
        self.get_all_the_states()
        self.get_all_the_cities()
        self.get_all_the_places()
        self.get_all_the_points_of_sale()
        self.get_all_the_timestamps()
        self.get_all_the_article_codes()
        self.get_all_the_article_cards()
        logging.info(f"{classname(self)}.update_cache stop")

    def get_timestamp(
        self,
        sample_key: str
    ) -> Timestamp:
       logging.info(f"{classname(self):s}.get_timestamp start")
       try:
           year = get_int(sample_key[0:4])
           month = get_int(sample_key[4:6])
           day = get_int(sample_key[6:8])
           hour = get_int(sample_key[8:10])
           minute = get_int(sample_key[10:12])
           second = get_int(sample_key[10:14])
           existing_timestamp = self.session.execute(
               select(Timestamp).filter_by(
               year=year,
               month=month,
               day=day,
               hour=hour,
               minute=minute,
               second=second)
           ).scalar_one_or_none()
           if existing_timestamp:
               logging.info(f"{classname(self):s}.get_timestamp: ({str(existing_timestamp):s}) in database already")
               logging.info(f"{classname(self):s}.get_timestamp stop")
               return existing_timestamp
           new_timestamp = Timestamp(
               year=year,
               month=month,
               day=day,
               hour=hour,
               minute=minute,
               second=second
           )
           self.session.add(new_timestamp)
           self.session.commit()
           logging.info(f"{classname(self):s}.get_timestamp stop")
           return new_timestamp
       except Exception as panic:
           self.session.rollback()
           logging.error( "*** Error Timestamp")
           logging.error(f"    {year} {month} {day} {hour} {minute} {second}")
           message = f"*** Error {classname(self):s}.get_timestamp ({classname(panic):s}): {str(panic):s}"
           raise DatabaseException(message)

    def insert_states(
        self,
        dict_of_states: dict[str, str]
    ) -> None:
        logging.info(f"{classname(self):s}.insert_states start")
        try:
            bulk = [
                {"code": code,
                 "name": name
                }
                for code, name in dict_of_states.items()
            ]
            self.session.execute(insert(State), bulk)
            self.session.commit()
            self.get_all_the_states()
            logging.info(f"{classname(self):s}.insert_states stop")
        except Exception as panic:
            self.session.rollback()
            logging.error(f"*** Error {classname(self):s}.insert_states")
            logging.error(f"    states: {str(dict_of_states):s}")
            message = f"*** Error {classname(self):s}.insert_states ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def get_state(
        self,
        state_code: str,
    ) -> State:
        try:
            return self.all_the_states[state_code]
        except Exception as panic:
            logging.error( "*** Error State")
            logging.error(f"    state_code: {state_code:s}")
            for key, state in self.all_the_states.items():
                logging.error(f"    key: {key} - state {state.name}")
            message = f"*** Error {classname(self)}.get_state: {classname(panic)}"
            raise DatabaseException(message)

    def get_city(
        self,
        name: str,
        db_state: State
    ) -> City:
        logging.info(f"{classname(self):s}.get_city start")
        try:
            existing_city = self.session.execute(
                select(City).filter_by(name=name, state=db_state)
            ).scalar_one_or_none()
            if existing_city:
                logging.info(f"{classname(self):s}.get_city: {name:s} at {db_state.name:s} in database already")
                logging.info(f"{classname(self):s}.get_city stop")
                return existing_city
            new_city = City(
                name=name,
                state=db_state
            )
            self.session.add(new_city)
            self.session.commit()
            logging.info(f"new_city id: {new_city.id}")
            logging.info(f"{classname(self):s}.get_city stop")
            return new_city
        except Exception as panic:
            self.session.rollback()
            logging.error( "*** Error City")
            logging.error(f"   city name: {name:s}")
            message = f"*** Error {classname(self):s}.get_city ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def get_place(
        self,
        address: str,
        db_city: City
    ) -> Place:
        logging.info(f"{classname(self):s}.get_place start")
        try:
            existing_place = self.session.execute(
                select(Place).filter_by(address=address, city=db_city)
            ).scalar_one_or_none()
            if existing_place:
                logging.info(f"{classname(self):s}.get_place: {address:s} at {db_city.name:s} in database already")
                logging.info(f"{classname(self):s}.get_place stop")
                return existing_place
            new_place = Place(
                address=address,
                city=db_city
            )
            self.session.add(new_place)
            self.session.commit()
            logging.info(f"new_place id: {new_place.id}")
            logging.info(f"{classname(self):s}.get_place stop")
            return new_place
        except Exception as panic:
            self.session.rollback()
            logging.error( "*** Error Place")
            logging.error(f"    place address: {str(address)}")
            logging.error(f"             city: {str(db_city)}")

            message = f"*** Error {classname(self):s}.get_place ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def look_for_point_of_sale(
        self,
        code: str
    ) -> PointOfSale | None:
        logging.info(f"{classname(self)}.look_for_point_of_sale start")
        try:
            existing_point_of_sale = self.session.execute(
                select(PointOfSale).filter_by(code=code)
            ).scalar_one_or_none()
            logging.info(f"{classname(self)}.look_for_point_of_sale stop")
            return existing_point_of_sale
        except Exception as panic:
            self.session.rollback()
            logging.error(f"*** Error {classname(self)}.look_for_point_of_sale")
            logging.error(f"    code: {code}")
            message = f"*** Error {classname(self):s}.look_for_point_of_sale ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def get_point_of_sale(
        self,
        code: str,
        flag: str,
        business: str,
        branch: str,
        db_place: Place
    ) -> PointOfSale:
        logging.info(f"{classname(self)}.get_point_of_sale start")
        try:
            existing_point_of_sale = self.session.execute(
                select(PointOfSale).filter_by(code=code)
            ).scalar_one_or_none()
            if existing_point_of_sale:
                logging.info(f"{classname(self):s}.get_point_of_sale: {code:s}, at {db_place.address} at {db_place.city.name:s} in database already")
                logging.info(f"{classname(self):s}.get_point_of_sale stop")
                return existing_point_of_sale
            new_point_of_sale = PointOfSale(
                code=code,
                flag=flag,
                business=business,
                branch=branch,
                place=db_place,
            )
            self.session.add(new_point_of_sale)
            self.session.commit()
            logging.info(f"new_point_of_sale id: {new_point_of_sale.id}")
            logging.info(f"{classname(self)}.get_point_of_sale stop")
            return new_point_of_sale
        except Exception as panic:
            self.session.rollback()
            logging.error( "*** Error PointOfSale")
            logging.error(f"    code: {code}")
            logging.error(f"    flag: {flag}")
            logging.error(f"    business: {business}")
            logging.error(f"    branch: {branch}")
            message = f"*** Error {classname(self):s}.get_point_of_sale ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def get_article_code(
        self,
        code: str
    ) -> ArticleCode:
        logging.info(f"{classname(self)}.get_article_code start")
        try:
            existing_article_code = self.session.execute(
                select(ArticleCode).filter_by(code=code)
            ).scalar_one_or_none()
            if existing_article_code:
                logging.info(f"{classname(self):s}.get_article_code: code {code:s} in database already")
                logging.info(f"{classname(self)}.get_article_code stop")
                return existing_article_code
            new_article_code = ArticleCode(
                code=code
            )
            self.session.add(new_article_code)
            self.session.commit()
            logging.info(f"{classname(self)}.get_article_code stop")
            return new_article_code
        except Exception as panic:
            self.session.rollback()
            logging.error( "*** Error ArticleCode")
            logging.error(f"    code: {code}")
            message = f"*** Error {classname(self):s}.get_article_code ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def get_article_card(
        self,
        brand: str,
        description: str,
        package: str,
        db_article_code: ArticleCode
    ) -> ArticleCard:
        logging.info(f"{classname(self)}.get_article_card start")
        try:
            existing_article_card = self.session.execute(
                select(ArticleCard).filter_by(
                    brand=brand,
                    description=description,
                    package=package,
                )
            ).scalar_one_or_none()
            if existing_article_card:
                logging.info(f"{classname(self)}.get_article_card stop")
                return existing_article_card
            new_article_card = ArticleCard(
                brand=brand,
                description=description,
                package=package,
                article_code=db_article_code,
            )
            self.session.add(new_article_card)
            self.session.commit()
            logging.info(f"{classname(self)}.get_article_card stop")
            return new_article_card
        except Exception as panic:
            self.session.rollback()
            logging.error( "*** Error ArticleCard")
            logging.error(f"          brand: {brand:s}")
            logging.error(f"    description: {description:s}")
            logging.error(f"        package: {package:s}")
            message = f"*** Error {classname(self):s}.get_article_card ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def insert_price(
        self,
        amount: int,
        timestamp: Timestamp,
        article_code: ArticleCode,
        point_of_sale: PointOfSale
    ) -> None:
        logging.info(f"{classname(self)}.insert_price start")
        try:
            new_price = Price(
                amount=amount,
                timestamp=timestamp,
                article_code=article_code,
                point_of_sale=point_of_sale,
            )
            self.session.add(new_price)
            self.session.commit()
            logging.info(f"{classname(self)}.insert_price stop")
        except Exception as panic:
            message = f"*** Error {classname(self):s}.insert_price ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def get_all_the_states(self) -> None:
        statement = select(State)
        _all_the_states = list(self.session.scalars(statement).all())
        self.all_the_states.update({a_state.code: a_state for a_state in _all_the_states})

    def get_all_the_cities(self) -> None:
        statement = select(City)
        _all_the_cities = list(self.session.scalars(statement).all())
        self.all_the_cities.update({get_stringy([a_city.state.code, a_city.name]): a_city
                for a_city in _all_the_cities})

    def get_all_the_places(self) -> None:
        statement = select(Place)
        _all_the_places = list(self.session.scalars(statement).all())
        self.all_the_places.update({
            get_stringy([
                a_place.city.state.code,
                a_place.city.name,
                a_place.address]
            ): a_place for a_place in _all_the_places
        })

    def get_all_the_points_of_sale(self) -> None:
        statement = select(PointOfSale)
        _all_the_points_of_sale = list(self.session.scalars(statement).all())
        self.all_the_points_of_sale.update(
            {pos.code: pos for pos in _all_the_points_of_sale}
        )

    def get_all_the_timestamps(self) -> None:
        statement = select(Timestamp)
        _all_the_timestamps = list(self.session.scalars(statement).all())
        self.all_the_timestamps.update(
            {repr(ts): ts for ts in _all_the_timestamps}
        )

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
            {get_stringy([ac.article_code.code, ac.brand, ac.description, ac.package]): ac
             for ac in _all_the_article_cards}
        )



# import pdb

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
    ArticleCode,
    ArticleCard,
    State,
    City,
    Place,
    PointOfSale,
    Timestamp,
    Price
)

CODES_AND_STATES = {
  "ar-a": "Salta",
  "ar-b": "Buenos Aires",
  "ar-c": "CABA",
  "ar-d": "San Luis",
  "ar-e": "Entre Rios",
  "ar-f": "La Rioja",
  "ar-g": "Santiago del Estero",
  "ar-h": "Chaco",
  "ar-j": "San Juan",
  "ar-k": "Catamarca",
  "ar-l": "La Pampa",
  "ar-m": "Mendoza",
  "ar-n": "Misiones",
  "ar-p": "Formosa",
  "ar-q": "Neuquén",
  "ar-r": "Río Negro",
  "ar-s": "Santa Fé",
  "ar-t": "Tucumán",
  "ar-u": "Chubut",
  "ar-v": "Tierra del Fuego",
  "ar-w": "Corrientes",
  "ar-x": "Córdoba",
  "ar-y": "San Salvador de Jujuy",
  "ar-z": "Santa Cruz",
  "buenos aires": "Buenos Aires",
  "catamarca": "Catamarca",
  "chaco": "Chaco",
  "cordoba": "Córdoba",
  "corrientes": "Corrientes",
  "la pampa": "La Pampa",
  "la rioja": "La Rioja",
  "neuquen": "Neuquén",
  "rio negro": "Río Negro",
  "salta": "Salta",
  "san luis": "San Luis",
  "santa fe": "Santa Fe",
  "santiago del estero": "Santiago del Estero",
  "tucuman": "Tucumán",
  "caba": "CABA",
  "jujuy": "Jujuy",
  "formosa": "Formosa",
  "misiones": "Misiones",
  "capital federal": "CABA",
  "mendoza": "Mendoza"
}



class DBInterfaceWithCache:
    def __init__(self, session: Session) -> None:
        self._session = session

        self._map_of_points_of_sale_code_string: dict[str, str] = dict()
        # self._all_the_states: dict[str, State] = self.get_all_the_states()
        # self._all_the_timestamps: dict[str, Timestamp] = self.get_all_the_timestamps()
        # self._all_the_cities: dict[str, City] = self.get_all_the_cities()
        # self._all_the_places: dict[str, Place] = self.get_all_the_places()
        # self._all_the_article_codes: dict[str, ArticleCode] = self.get_all_the_article_codes()
        # self._all_the_article_cards: dict[str, ArticleCard] = self.get_all_the_article_cards()
        # self._all_the_points_of_sale: dict[str, PointOfSale] = self.get_all_the_points_of_sale()
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

    def update_cache(self) -> None:
        logging.info(f"{classname(self)}.update_cache start")
        self.all_the_states.update(self.get_all_the_states())
        logging.info(f"{classname(self)}.update_cache stop")


    def insert_timestamps(
        self,
        sample_key_generator: Callable[[], Generator[str, None, None]]
    ) -> None:
        logging.info(f"{classname(self):s}.insert_timestamps start")
        try:
            bulk = [ Timestamp(
                year=get_int(sample_key[0:4]),
                month=get_int(sample_key[4:6]),
                day=get_int(sample_key[6:8]),
                hour=get_int(sample_key[8:10]),
                minute=get_int(sample_key[10:12]),
                second=get_int(sample_key[10:14])
                ) for sample_key in sample_key_generator()
            ]
            self.session.execute(insert(Timestamp), bulk)
            self.session.commit()
            self.get_all_the_timestamps()
            logging.info(f"{classname(self):s}.insert_timestamps ({len(self.all_the_timestamps)}) stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_timestamps ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)
        logging.info(f"{classname(self):s}.insert_timestamps done")

    def query_timestamp(
        self,
        sample_key: str
    ) -> Timestamp | None:
        try:
            logging.info(f"{classname(self):s}.query_timestamp start")
            existing_timestamp = self.all_the_timestamps.get(sample_key, None)
            if existing_timestamp:
                logging.info(f"{classname(self):s}.query_timestamp: ({str(existing_timestamp):s}) in database already")
            logging.info(f"{classname(self):s}.query_timestamp stop")
            return existing_timestamp
       except Exception as panic:
            logging.error(f"*** Error {classname(self):s}.query_timestamp")
            logging.error(f"    {year} {month} {day} {hour} {minute} {second}")
            message = f"*** Error {classname(self):s}.query_timestamp  ({len(self.all_the_timestamps)})({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def insert_one_timestamp(
        self,
        sample_key: str
    ) -> Timestamp | None:
        try:
            year = get_int(sample_key[0:4])
            month = get_int(sample_key[4:6])
            day = get_int(sample_key[6:8])
            hour = get_int(sample_key[8:10])
            minute = get_int(sample_key[10:12])
            second = get_int(sample_key[10:14])
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
            self.all_the_timestamps[sample_key] = new_timestamp
            logging.info(f"{classname(self):s}.get_timestamp ({len(self._all_the_timestamps)}) stop")
            return new_timestamp
       except Exception as panic:
            self.session.rollback()
            logging.error( "*** Error Timestamp")
            logging.error(f"    {year} {month} {day} {hour} {minute} {second}")
            message = f"*** Error {classname(self):s}.get_timestamp  ({len(self.all_the_timestamps)})({classname(panic):s}): {str(panic):s}"
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
        except Exception as panic:
            self.session.rollback()
            logging.error( "*** Error State")
            logging.error(f"    states: {str(dict_of_states):s}")
            message = f"*** Error {classname(self):s}.insert_states ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)
        logging.info(f"{classname(self):s}.insert_states stop")

    # TODO: State with name="Error", all the bad states codes belongs to the Error State

    def query_state(
        self,
        state_code: str
    ) -> State:
        logging.info(f"{classname(self)}.query_state start")
        try:
            existing_state = self.all_the_states.get(state_code, None)
            logging.info(f"{classname(self)}.query_state stop")
            return existing_state
        except Exception as panic:
            logging.error(f"*** Error {classname(self)}.query_state")
            logging.error(f"    state_code: {state_code:s}")
            for key, state in self.all_the_states.items():
                logging.error(f"    key: {key} - state {state.name}")
            message = f"*** Error {classname(self)}.query_state: {classname(panic)}"
            raise DatabaseException(message)

    def insert_one_state(
        self,
        state_code: str,
        state_name: str
    ) -> None:
        try:
            new_state = State(code=state_code, name=state_name)
            self.session.insert(new_state)
            self.session.commit()
            self.all_the_states[new_state.code] = new_state
        except Exception as panic:
            self.session.rollback()
            logging.error(f"*** Error {classname(self)}.insert_one_state")
            logging.error(f"    state_code: {state_code:s}")
            logging.error(f"    state_name: {state_name:s}")
            for key, state in self.all_the_states.items():
                logging.error(f"    key: {key} - state {state.name}")
            message = f"*** Error {classname(self)}.query_state: {classname(panic)}"
            raise DatabaseException(message)

    def insert_cities(
        self,
        cities_generator: Callable[[], Generator[dict[str, str], None, None]
    ) -> None:
        logging.info(f"{classname(self):s}.insert_cities start")
        try:
            bulk = [
                {"name": record["city"],
                 "state": self.get_state(record["state"])
                } for record in cities_generator()]
            self.session.execute(insert(City), bulk)
            self.session.commit()
            self.get_all_the_cities()
            logging.info(f"{classname(self):s}.insert_cities ({len(self.all_the_cities)}) stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_cities ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)
        logging.info(f"{classname(self):s}.insert_cities done")


    def query_city(
        self,
        name: str,
        db_state: State
    ) -> City:
        logging.info(f"{classname(self):s}.query_city start")
        try:
            stringy_city = get_stringy([db_state.code, name])
            existing_city = self.all_the_cities.get(stringy_city, None)
            if existing_city:
                logging.info(f"{classname(self):s}.query_city: {name:s} at {db_state.name:s} in database already")
                logging.info(f"{classname(self):s}.query_city stop")
                return existing_city
        except Exception as panic:
            self.session.rollback()
            logging.error(f"*** Error {classname(self):s}.query_city")
            logging.error(f"   city name: {name:s}")
            logging.error(f"       state: {db_state.code} - {db_state.name}")
            message = f"*** Error {classname(self):s}.get_city ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def insert_one_city(
        self,
        name: str,
        db_state: State
    ) -> City:
        logging.info(f"{classname(self):s}.insert_one_city start")
        try:
            new_city = City(
                name=name,
                state=db_state
            )
            self.session.add(new_city)
            self.session.commit()
            self.all_the_cities[stringy_city] = new_city
            logging.info(f"new_city id: {new_city.id}")
            logging.info(f"{classname(self):s}.get_city ({len(self.all_the_cities)}) stop")
            return new_city
        except Exception as panic:
            self.session.rollback()
            logging.error( "*** Error City")
            logging.error(f"   city name: {name:s}")
            message = f"*** Error {classname(self):s}.get_city ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def insert_places(
        self,
        places_generator: Callable[[], Generator[dict[str, str], None, None]
    ) -> None:
        logging.info(f"{classname(self):s}.insert_places start")
        try:
            bulk = [
                {"address": record["address"],
                 "city": self.look_for_a_city(record["stringy_city"])
                } for record in cities_generator()
            ]
            self.session.execute(insert(Place), bulk)
            self.session.commit()
            self.get_all_the_places()
            logging.info(f"{classname(self):s}.insert_cities ({len(self.all_the_cities)}) stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_cities ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)
        logging.info(f"{classname(self):s}.insert_cities done")

    def query_place(
        self,
        address: str,
        db_city: City
    ) -> Place | None:
        logging.info(f"{classname(self):s}.query_place start")
        try:
            stringy_place = get_stringy([
                db_city.state.code,
                db_city.name,
                address]
            )
            existing_place = self.all_the_places.get(stringy_place, None)
            return existing_place
        except Exception as panic:
            logging.error(f"*** Error {classname(self):s}.query_place")
            logging.error(f"    place address: {str(address)}")
            logging.error(f"             city: {str(db_city)}")
            message = f"*** Error {classname(self):s}.query_place ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def insert_one_place(
        self,
        address: str,
        db_city: City
    ) -> Place:
        logging.info(f"{classname(self):s}.insert_one_place start")
        try:
            new_place = Place(
                address=address,
                city=db_city
            )
            self.session.add(new_place)
            self.session.commit()
            self.all_the_places[stringy_place] = new_place
            logging.info(f"{classname(self):s}.insert_one_place ({len(self.all_the_places)}) stop")
            return new_place
        except Exception as panic:
            self.session.rollback()
            logging.error( "*** Error Place")
            logging.error(f"    place address: {str(address)}")
            logging.error(f"             city: {str(db_city)}")
            message = f"*** Error {classname(self):s}.insert_one_place ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def insert_points_of_sale(
        self,
        points_of_sale_generator: Callable[[], Generator[dict[str, str], None, None]
    )
        logging.info(f"{classname(self):s}.insert_points_of_sale start")
        try:
            bulk = [
                {"code": code,
                 "flag": flag,
                 "business": business,
                 "branch": branch,
                 "place": self.look_for_a_place(stringy_place)
                } for code, flag, business, branch, stringy_place in points_of_sale_generator()
            ]
            self.session.execute(insert(PointOfSale), bulk)
            self.session.commit()
            self.get_all_the_points_of_sale()
            logging.info(f"{classname(self):s}.insert_points_of_sale ({len(self.all_the_points_of_sale)}) stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_points_of_sale ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)
        logging.info(f"{classname(self):s}.insert_points_of_sale done")

    def query_point_of_sale(
        self,
        code: str
    ) -> PointOfSale | None:
        logging.info(f"{classname(self):s}.query_point_of_sale start")
        try:
            existing_point_of_sale = self.all_the_points_of_sale.get(code, None)
            return existing_point_of_sale
        except Exception as panic:
            logging.error(f"*** Error {classname(self):s}.query_point_of_sale")
            logging.error(f"    code: {code}")
            message = f"*** Error {classname(self):s}.query_point_of_sale ({classname(panic):s}): {str(panic):s}"
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
            new_point_of_sale = PointOfSale(
                code=code,
                flag=flag,
                business=business,
                branch=branch,
                place=db_place,
            )
            self.session.add(new_point_of_sale)
            self.session.commit()
            self.all_the_points_of_sale[code] = new_point_of_sale
            logging.info(f"{classname(self)}.get_point_of_sale ({len(self.all_the_points_of_sale)}) stop")
            return new_point_of_sale
        except Exception as panic:
            self.session.rollback()
            logging.error(f"*** Error {classname(self)}.get_point_of_sale")
            logging.error(f"    code: {code}")
            logging.error(f"    flag: {flag}")
            logging.error(f"    business: {business}")
            logging.error(f"    branch: {branch}")
            logging.error(f"    place: {place.address} at {place.city}")
            message = f"*** Error {classname(self):s}.get_point_of_sale ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def insert_article_codes(
        self,
        article_codes_generator: Callable[[], Generator[dict[str, str], None, None]
    ) -> None:
        try:
            bulk = [
                {"code": code
                } for code in article_code_generator()
            ]
            self.session.execute(insert(ArticleCode), bulk)
            self.session.commit()
            self.get_all_the_article_codes()
        except Exception as panic:

    def query_article_code(
        self,
        code: str
    ) -> Place | None:
        logging.info(f"{classname(self):s}.query_article_code start")
        try:
            existing_article_code = self.all_the_article_codes.get(code, None)
            return existing_article_code
        except Exception as panic:
            logging.error(f"*** Error {classname(self):s}.query_article_code")
            logging.error(f"    code: {code}")
            message = f"*** Error {classname(self):s}.query_article_code ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def insert_one_article_code(
        self,
        code: str
    ) -> ArticleCode:
        logging.info(f"{classname(self)}.insert_one_article_code start")
        try:
            new_article_code = ArticleCode(
                code=code
            )
            self.session.add(new_article_code)
            self.session.commit()
            self.all_the_article_codes[code] = new_article_code
            logging.info(f"{classname(self)}.get_article_code ({len(self.all_the_article_codes)}) stop")
            return new_article_code
        except Exception as panic:
            self.session.rollback()
            logging.error(f"*** Error {classname(self):s}.get_article_code")
            logging.error(f"    code: {code}")
            message = f"*** Error {classname(self):s}.get_article_code ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def insert_article_cards(
        self,
        article_card_generator:  Callable[[], Generator[dict[str, str], None, None]
    ) -> None:
        logging.info(f"{classname(self)}.insert_article_cards start")
        try:
            bulk = [
                { "brand": brand,
                  "description": description,
                  "package": package,
                  "article_code": self.look_for_article_code(article_code_string)
                } for brand, description, package, article_code_string in article_card_generator()
            ]
            self.session.execute(insert(ArticleCard), bulk)
            self.session.commit()
            self.get_all_the_article_cards()
            logging.info(f"{classname(self)}.insert_article_cards ({len(all_the_article_cards)}) stop")
        except Exception as panic:
            self.session.rollback()
            message = f"*** Error {classname(self):s}.insert_article_cards ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)

    def insert_one_article_card(
        self,
        brand: str,
        description: str,
        package: str,
        db_article_code: ArticleCode
    ) -> ArticleCard:
        logging.info(f"{classname(self)}.insert_one_article_card start")
        try:
            stringy_card = get_stringy([db_article_code.code, brand, description, package])
            new_article_card = ArticleCard(
                brand=brand,
                description=description,
                package=package,
                article_code=db_article_code,
            )
            self.session.add(new_article_card)
            self.session.commit()
            self.all_the_article_cards[stringy_card] = new_article_card
            logging.info(f"{classname(self)}.insert_one_article_card ({len(self.all_the_article_cards)}) stop")
            return new_article_card
        except Exception as panic:
            self.session.rollback()
            logging.error(f"*** Error {classname(self):s}.get_article_card")
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

    def query_price(
        self,
        timestamp: Timestamp,
        article_code: ArticleCode,
        point_of_sale: PointOfSale
    ) -> Price | None:
        logging.info(f"{classname(self)}.query|_price start")
        try:
            existing_price = self.session.execute(
                select(Price).filter_by(
                    timestamp=timestamp,
                    article_code=article_code,
                    point_of_sale=point_of_sale,
                )
            ).scalar_one_or_none()
            return existing_price
        except Exception as panic:
            logging.error(f"*** Error {classname(self):s}.query_price")
            logging.error()
            message = f"*** Error {classname(self):s}.query_price ({classname(panic):s}): {str(panic):s}"
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



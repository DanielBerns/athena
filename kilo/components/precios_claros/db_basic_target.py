# import pdb
import logging
from pathlib import Path
from components.precios_claros.database import (
    Timestamp,
    Tag,
    State,
    City,
    Place,
    PointOfSale,
    ArticleCode,
    ArticleCard,
    Price,
    DatabaseException
)
from components.precios_claros.db_interface import DBInterface
from components.helpers.helpers import get_stringy, get_resource, read_json


def get_int(string: str) -> int:
    try:
        return int(string)
    except Exception as panic:
        logging.error(f"*** Error get_int")
        logging.error(f"    string: {str(panic)}")
        message = f"*** Error ({classname(panic)}): {str(panic)}"
        raise DatabaseException(message)


class DBBasicTarget:
    def __init__(self, db: DBInterface) -> None:
        self._db = db
        self._current_sample_home: Path | None = None
        self._current_timestamp: Timestamp | None = None
        self._map_of_points_of_sale: dict[str, str] = dict()
        self._all_the_states: dict[str, State] = self.db.all_the_states()
        self._all_the_cities: dict[str, City] = self.db.all_the_cities()
        self._all_the_places: dict[str, Place] = self.db.all_the_places()
        self._all_the_article_codes: dict[str, ArticleCode] = self.db.all_the_article_codes()
        self._all_the_article_cards: dict[str, ArticleCard] = self.db.all_the_article_cards()
        self._all_the_points_of_sale: dict[str, PointOfSale] = self.db.all_the_points_of_sale()


    @property
    def db(self) -> DBInterface:
        return self._db

    @property
    def current_sample_home(self) -> Path:
        return self._current_sample_home

    @current_sample_home.setter
    def current_sample_home(self, value: Path) -> None:
        self._current_sample_home = value
        try:
            resource = get_resource(self.current_sample_home, "metadata", ".json")
            metadata = read_json(resource)
            sample_key = metadata["sample_key"]
            self.current_timestamp = self.db.insert_timestamp(
                get_int(sample_key[0:4]),
                get_int(sample_key[4:6]),
                get_int(sample_key[6:8]),
                get_int(sample_key[8:10]),
                get_int(sample_key[10:12]),
                get_int(sample_key[10:14]),
            )
        except Exception as panic:
            self.current_timestamp = None
            message = f"*** Error -{classname(self):s}.current_sample_home: {str(panic):s}"
            raise DatabaseException(message)

    @property
    def current_timestamp(self) -> Timestamp | None:
        return self._current_timestamp

    @current_timestamp.setter
    def current_timestamp(self, value: Timestamp | None) -> None:
        self._current_timestamp = value

    def new_point_of_sale_code(self, point_of_sale_code: str, business: str) -> str:
        return f"[{point_of_sale_code:s}]--({business:s})"

    @property
    def map_of_points_of_sale_code(self) -> dict[str, str]:
        return self._map_of_points_of_sale

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

    def kilo_points_of_sale(self, event: dict[str, str]) -> None:
        state_code = event["state"]
        city_name = event["city"]
        address = event["address"]
        point_of_sale_code = event["point_of_sale_code"]
        flag = event["flag"]
        business = event["business"]
        branch = event["branch"]
        new_point_of_sale_code = self.new_point_of_sale_code(
            point_of_sale_code, business
        )
        self.map_of_points_of_sale_code[point_of_sale_code] = new_point_of_sale_code
        stringy_city = get_stringy([state_code, city_name])
        stringy_place = get_stringy([state_code, city_name, address])
        test_state = self.all_the_states.get(state_code, None)
        if test_state:
            state = test_state
        else:
            message = f"*** Error state_code: {state_code}"
            raise DatabaseException(message)

        test_city = self.all_the_cities.get(stringy_city, None)
        if test_city:
            db_city = test_city
        else:
            db_city = self.db.insert_city(city_name, state)
            self.all_the_cities[stringy_city] = db_city
        test_place = self.all_the_places.get(stringy_place, None)
        # pdb.set_trace()
        if test_place:
            db_place = test_place
        else:
            db_place = self.db.insert_place(address, db_city)
            self.all_the_places[stringy_place] = db_place
        test_point_of_sale = self.all_the_points_of_sale.get(new_point_of_sale_code, None)
        if test_point_of_sale:
            point_of_sale = test_point_of_sale
        else:
            db_point_of_sale = self.db.insert_point_of_sale(
                new_point_of_sale_code,
                flag,
                business,
                branch,
                db_place
            )
            self.all_the_points_of_sale[new_point_of_sale_code] = db_point_of_sale

    def kilo_articles_per_point_of_sale(self, event: dict[str, str]) -> None:
        # pdb.set_trace()
        ac = event["article_code"]
        brand = event["brand"]
        description = event["description"]
        package = event["package"]
        amount = event["price"]
        point_of_sale_code = event["point_of_sale_code"]
        test_article_code = self.all_the_article_codes.get(ac, None)
        if test_article_code:
            article_code = test_article_code
        else:
            article_code = self.db.insert_article_code(ac)
            self.all_the_article_codes[ac] = article_code
        stringy_article_card = get_stringy([ac, brand, description, package])
        test_article_card = self.all_the_article_cards.get(stringy_article_card, None)
        if test_article_card:
            article_card = test_article_card
        else:
            article_card = self.db.insert_article_card(
                brand,
                description,
                package,
                article_code
            )
            self.all_the_article_cards[stringy_article_card] = article_card
        test_posc = self.map_of_points_of_sale_code.get(point_of_sale_code, None)
        test_point_of_sale = self.all_the_points_of_sale.get(test_posc, None) if test_posc else None
        if test_point_of_sale is None:
            logging.error(f"*** Error ({classname(self):s}).kilo_articles_per_point_of_sale")
            logging.error(f"    test_posc is None. article_code is {ac:s}")
            logging.error(f"*** Error ({classname(self):s}).kilo_articles_per_point_of_sale")
            raise DatabaseException(message)
        point_of_sale = test_point_of_sale
        self.db.insert_price(amount, self.current_timestamp, article_code, point_of_sale)

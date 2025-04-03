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
    DatabaseException,
    get_int
)
from components.precios_claros.db_new_interface import DBNewInterface
from components.helpers.helpers import get_stringy, get_resource, read_json, classname



class DBPreciosClarosTarget:
    def __init__(self, db: DBNewInterface) -> None:
        self._db = db
        self._current_sample_home: Path | None = None
        self._current_timestamp: Timestamp | None = None
        self._map_of_points_of_sale: dict[str, str] = dict()

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
            self.current_timestamp = self.db.get_timestamp(sample_key)
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

    def new_point_of_sale_code_string(self, point_of_sale_code_string: str, business: str) -> str:
        return get_stringy([point_of_sale_code_string, business])

    def kilo_points_of_sale(self, event: dict[str, str]) -> None:
        state_code = event["state"]
        city_name = event["city"]
        address = event["address"]
        point_of_sale_code_string = event["point_of_sale_code"]
        flag = event["flag"]
        business = event["business"]
        branch = event["branch"]
        new_point_of_sale_code_string = self.new_point_of_sale_code_string(
            point_of_sale_code_string, business
        )
        self.db.map_of_points_of_sale_code_string[point_of_sale_code_string] = new_point_of_sale_code_string
        state = self.db.get_state(state_code)
        city = self.db.get_city(city_name, state)
        place = self.db.get_place(address, city)
        point_of_sale = self.db.get_point_of_sale(
            new_point_of_sale_code_string,
            flag,
            business,
            branch,
            place
        )

    def kilo_articles_per_point_of_sale(self, event: dict[str, str]) -> None:
        try:
            article_code_string = event["article_code"]
            brand = event["brand"]
            description = event["description"]
            package = event["package"]
            amount = event["price"]
            point_of_sale_code_string = event["point_of_sale_code"]
            article_code = self.db.get_article_code(article_code_string)
            article_card = self.db.get_article_card(brand, description, package, article_code)
            point_of_sale_code_string = self.db.map_of_points_of_sale_code_string.get(point_of_sale_code_string, None)
            point_of_sale = self.db.look_for_point_of_sale(point_of_sale_code_string)
            self.db.insert_price(amount, self.current_timestamp, article_code, point_of_sale)
        except Exception as panic:
            logging.error(f"*** Error ({classname(self):s}).kilo_articles_per_point_of_sale")
            logging.error(f"    event")
            for key, value in event.items():
                logging.error(f"    {key}: {value}")
            message = f"*** Error ({classname(self):s}).kilo_articles_per_point_of_sale: {classname(panic)} - {panic}"
            raise DatabaseException(message)

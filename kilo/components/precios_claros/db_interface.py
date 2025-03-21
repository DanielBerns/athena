# import pdb

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from sqlalchemy.orm import Session
from collections.abc import Callable

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
    Price,
    db_get_session
)

from components.helpers.helpers import get_container

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



class DBInterface:

    @property
    def session(self) -> Session:
        ...

    def new_point_of_sale_code_string(self, point_of_sale_code_string: str, business: str) -> str:
        ...

    @property
    def map_of_points_of_sale_code_string(self) -> dict[str, str]:
        ...

    @property
    def all_the_states(self) -> dict[str, State]:
        ...

    def update_cache(self) -> None:
        ...

    def get_timestamp(
        self,
        sample_key: str
    ) -> Timestamp:
        ...

    def insert_states(
        self,
        dict_of_states: dict[str, str]
    ) -> None:
        ...

    def get_state(
        self,
        state_code: str,
    ) -> State:
        ...

    def get_city(
        self,
        name: str,
        db_state: State
    ) -> City:
        ...

    def get_place(
        self,
        address: str,
        db_city: City
    ) -> Place:
        ...

    def get_point_of_sale(
        self,
        code: str,
        flag: str,
        business: str,
        branch: str,
        db_place: Place
    ) -> PointOfSale:
        ...

    def get_article_code(
        self,
        code: str
    ) -> ArticleCode:
        ...

    def get_article_card(
        self,
        brand: str,
        description: str,
        package: str,
        db_article_code: ArticleCode
    ) -> ArticleCard:
        ...

    def insert_price(
        self,
        amount: int,
        timestamp: Timestamp,
        article_code: ArticleCode,
        point_of_sale: PointOfSale
    ) -> None:
        ...

    def get_all_the_states(self) -> dict[str, State]:
        ...

    def get_all_the_cities(self) -> dict[str, City]:
        ...

    def get_all_the_places(self) -> dict[str, Place]:
        ...

    def get_all_the_points_of_sale(self) -> dict[str, PointOfSale]:
        ...

    def get_all_the_timestamps(self) -> dict[str, Timestamp]:
        ...

    def get_all_the_article_codes(self) -> dict[str, ArticleCode]:
        ...

    def get_all_the_article_cards(self) -> dict[int, ArticleCard]:
        ...


@contextmanager
def db_get_interface(
    storage_precios_claros: Path,
    db_create_interface: Callable[[Session], DBInterface]
) -> Generator[DBInterface, None, None]:
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    db_uri = Path(storage_precios_claros_sqlite, "mecon").with_suffix(".db")
    initialize_db = not db_uri.exists()
    with db_get_session(str(db_uri)) as session:
        try:
            db_interface = db_create_interface(session)
            if initialize_db:
               db_interface.insert_states(CODES_AND_STATES)
            db_interface.update_cache()
            yield db_interface
        except Exception as panic:
            logging.error(f"*** Error db_interface.db_get_interface {str(panic):s}")
            message = "*** Error db_get_interface: rollback and close!"
            raise DatabaseException(message)


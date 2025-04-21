import logging
from pathlib import Path
from typing import Protocol, Callable, Generator, Optional
from contextlib import contextmanager
from sqlalchemy.orm import Session

from components.core.logged_exception import LoggedException
from components.helpers.helpers import get_container, classname
from components.precios_claros.database import (
    ArticleCode,
    ArticleCard,
    State,
    City,
    Place,
    PointOfSale,
    Timestamp,
    Price,
    db_get_session
)


class DBNewInterface(Protocol):

    def new_point_of_sale_code_string(
        self,
        point_of_sale_code_string: str,
        flag: str
    ) -> str:
        ...

    @property
    def map_of_points_of_sale_code_string(self) -> dict[str, str]:
        ...

    def update_cache(self) -> None:
        ...

    def insert_timestamps(
        self,
        sample_key_generator: Callable[[], Generator[str, None, None]]
    ) -> None:
        ...

    def query_timestamp(
        self,
        sample_key: str
    ) -> Optional[Timestamp]:
        ...

    def insert_states(
        self,
        known_states: dict[str, str]
    ) -> None:
        ...

    def query_state(
        self,
        state_code: str
    ) -> Optional[State]:
        ...

    def insert_cities(
        self,
        cities_generator: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        ...

    def query_city(
        self,
        name: str,
        db_state: State
    ) -> Optional[City]:
        ...

    def insert_places(
        self,
        places_generator: Callable[[], Generator[dict[str, str], None, None]]
    ) -> None:
        ...

    def query_place(
        self,
        address: str,
        db_city: City
    ) -> Optional[Place]:
        ...

    def insert_points_of_sale(
        self,
        points_of_sale_generator: Callable[[], Generator[tuple[str, str, str, str, str], None, None]]
    ) -> None:
        ...

    def query_point_of_sale_by_code(
        self,
        code: str
    ) -> Optional[PointOfSale]:
        ...

    def query_point_of_sale(
        self,
        code: str,
        flag: str,
        business: str,
        branch: str,
        db_place: Place
    ) -> Optional[PointOfSale]:
        ...

    def insert_article_codes(
        self,
        article_codes_generator: Callable[[], Generator[str, None, None]]
    ) -> None:
        ...

    def query_article_code(
        self,
        code: str
    ) -> Optional[ArticleCode]:
        ...

    def insert_article_cards(
        self,
        article_card_generator: Callable[[], Generator[tuple[str, str, str, str], None, None]]
    ) -> None:
        ...

    def insert_price(
        self,
        amount: int,
        timestamp: Timestamp,
        article_code: ArticleCode,
        point_of_sale: PointOfSale
    ) -> None:
        ...

    def query_price(
        self,
        timestamp: Timestamp,
        article_code: ArticleCode,
        point_of_sale: PointOfSale
    ) -> Optional[Price]:
        ...

    def get_all_the_states(self) -> None:
        ...

    def get_all_the_cities(self) -> None:
        ...

    def get_all_the_places(self) -> None:
        ...

    def get_all_the_points_of_sale(self) -> None:
        ...

    def get_all_the_timestamps(self) -> None:
        ...

    def get_all_the_article_codes(self) -> None:
        ...

    def get_all_the_article_cards(self) -> None:
        ...

    def query_ordered_article_cards(
        self,
        batch_size: int = 100
    ) -> Generator[ArticleCard, None, None]:
        ...

    def query_ordered_article_codes(
        self,
        batch_size: int = 100
    ) -> Generator[ArticleCode, None, None]:
        ...

    def query_prices_by_article_code(
        self,
        article_code_value: str,
        batch_size: int = 100
    ) -> Generator[Price, None, None]:
      ...

    def query_prices_by_article_code_and_city(
        self,
        article_code_value: str,
        city_name: str,
        batch_size: int = 100
    ) -> Generator[Price, None, None]:
      ...

    def query_prices_by_article_code_city_and_timestamp(
        self,
        article_code_value: str,
        city_name: str,
        target_timestamp: str,
        batch_size: int = 100
    ) -> Generator[Price, None, None]:
        ...


@contextmanager
def db_get_new_interface(
    storage_precios_claros: Path,
    db_create_interface: Callable[[Session], DBNewInterface]
) -> Generator[DBNewInterface, None, None]:
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    db_uri = Path(storage_precios_claros_sqlite, "mecon").with_suffix(".db")
    with db_get_session(str(db_uri)) as session:
        try:
            db_interface = db_create_interface(session)
            db_interface.update_cache()
            yield db_interface
        except Exception as panic:
            message = f"*** Error db_interface.db_get_interface ({classname(panic)}) {str(panic):s}"
            raise LoggedException(message)


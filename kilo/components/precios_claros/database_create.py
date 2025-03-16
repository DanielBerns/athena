import pdb
import logging
from pathlib import Path 

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from components.helpers.helpers import get_container, get_stringy, classname
from components.dirty_events.dirty_events import DirtyEvents
from components.kilo.kilo_paths import KiloPaths

from components.precios_claros.database import (
    ArticleCode,
    ArticleCard,
    State, 
    City, 
    Place,
    PointOfSale,
    Timestamp, 
    Price,
    db_create_session
)


class DatabaseException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


def get_int(string: str) -> int:
    try:
        return int(string)
    except Exception as panic:
        logging.error(f"*** get_int error: {str(panic)}")
        return -1


def bulk_insert_timestamps(session: Session, dirty_timestamps: DirtyEvents) -> None:
    logging.info("bulk_insert_timestamps start")
    try:
        bulk = [
            {"year": get_int(event.get("year", "-1")),
             "month": get_int(event.get("month", "-1")),
             "day": get_int(event.get("day", "-1")),
             "hour": get_int(event.get("hour", "-1")),
             "minute": get_int(event.get("minute", "-1")),
             "second": get_int(event.get("second", "-1"))
            }
            for key, event in dirty_timestamps.table.items()
        ]
        session.execute(insert(Timestamp), bulk)
        session.commit()
    except Exception as panic:
        session.rollback()
        message = f"*** bulk_insert_timestamps error ({classname(panic):s}): {str(panic):s}"
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_timestamps stop")


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


def bulk_insert_states(session: Session, dirty_states: DirtyEvents) -> None:
    logging.info("bulk_insert_states start")
    try:
        bulk = [
            {"code": code,
             "name": name
            }
            for code, name in CODES_AND_STATES.items()
        ]
        session.execute(insert(State), bulk)
        session.commit()
    except Exception as panic:
        session.rollback()
        message = f"*** bulk_insert_states error ({classname(panic):s}): {str(panic):s}"
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_states stop")


def bulk_insert_cities(
    session: Session,
    dirty_cities: DirtyEvents,
    db_states: dict[str, State]
) -> None:
    logging.info("bulk_insert_cities start")
    for key, a_dirty_city in dirty_cities.table.items():
        try:
            a_state = db_states[a_dirty_city["state_code"]]
            new_city = City(
                name=a_dirty_city["city"],
                state=a_state
            )
            session.add(new_city)
        except Exception as panic:
            session.rollback()
            logging.error("*** Error")
            logging.error(f"   a_dirty_city: {str(a_dirty_city)}")
            expected_state_code = a_dirty_city.get("state_code", None)
            if expected_state_code:
                expected_state = db_states.get(expected_state_code, None)
                if expected_state:
                    logging.error(f"    expected_state: {str(expected_state):s}")
                else:
                    logging.error("    expected_state is None")
            else:
                logging.error("    no state_code in a_dirty_city")
            message = f"*** bulk_insert_cities error ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)
    session.commit()
    logging.info("bulk_insert_cities stop")


def bulk_insert_places(
    session: Session,
    dirty_places: DirtyEvents,
    db_cities: dict[str, City]
) -> None:
    logging.info("bulk_insert_places start")
    for key, a_dirty_place in dirty_places.table.items():
        try:
            a_city = db_cities[a_dirty_place["stringy_city"]]
            new_place = Place(
                address=a_dirty_place["address"],
                city=a_city
            )
            session.add(new_place)
        except Exception as panic:
            session.rollback()
            logging.error("*** Error")
            logging.error(f"             key: {key:s}")
            logging.error(f"   a_dirty_place: {str(a_dirty_place)}")
            expected_city_name = a_dirty_place.get("stringy_city", None)
            if expected_city_name:
                expected_city = db_cities.get(expected_city_name, None)
                if expected_city:
                    logging.error(f"    expected_city: {str(expected_city):s}")
                else:
                    logging.error("    expected_city is None")
            else:
                logging.error("    no city_name in a_dirty_place")
            message = f"*** bulk_insert_places error ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)
    session.commit()
    logging.info("bulk_insert_places stop")


def insert_point_of_sale(
    session: Session,
    code: str,
    flag: str,
    business: str,
    branch: str,
    place: Place
) -> None:
    """
    Inserts a PointOfSale into the database if one with the given code
    does not already exist.

    Args:
        session: The SQLAlchemy Session to use.
        code: The code of the point of sale.
        flag: The flag of the point of sale.
        business: The business of the point of sale.
        branch: The branch of the point of sale.
        place_id: The ID of the place associated with the point of sale.

    Returns: None
    """
    # Check if a PointOfSale with the given code already exists
    existing_point_of_sale = session.execute(
        select(PointOfSale).filter_by(code=code)
    ).scalar_one_or_none()

    if not existing_point_of_sale:
        # Create a new PointOfSale object
        new_point_of_sale = PointOfSale(
            code=code,
            flag=flag,
            business=business,
            branch=branch,
            place=place,
        )

        # Add the new PointOfSale to the session
        session.add(new_point_of_sale)


def bulk_insert_points_of_sale(
    session: Session,
    dirty_points_of_sale: DirtyEvents,
    all_the_places: dict[str, Place]
) -> None:
    logging.info("bulk_insert_points_of_sale start")
    for key, a_dirty_point_of_sale in dirty_points_of_sale.table.items():
        try:
            insert_point_of_sale(
                session,
                a_dirty_point_of_sale["point_of_sale_code"],
                a_dirty_point_of_sale["flag"],
                a_dirty_point_of_sale["business"],
                a_dirty_point_of_sale["branch"],
                all_the_places[a_dirty_point_of_sale["stringy_place"]]
            )
        except Exception as panic:
            session.rollback()
            logging.error(f"                      key: {key:s}")
            logging.error(f"    a_dirty_point_of_sale: {str(a_dirty_point_of_sale):s}")
            message = f"*** bulk_insert_points_of_sale error {classname(panic):s}: {str(panic):s}"
            raise DatabaseException(message)
    session.commit()
    logging.info("bulk_insert_points_of_sale stop")


def bulk_insert_article_codes(session: Session, dirty_article_codes: DirtyEvents) -> None:
    logging.info("bulk_insert_article_codes start")
    try:
        bulk = [{"code": a_dirty_article_code["article_code"]}
                for key, a_dirty_article_code in dirty_article_codes.table.items()
        ]
        session.execute(insert(ArticleCode), bulk)
        session.commit()
    except Exception as panic:
        session.rollback()
        message = f"*** bulk_insert_article_codes error ({classname(panic):s}): {str(panic):s}"
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_article_codes stop")


def bulk_insert_article_cards(
    session: Session,
    dirty_article_cards: DirtyEvents,
    all_the_article_codes: dict[str, ArticleCode]
) -> None:
    logging.info("bulk_insert_article_cards start")
    for key, a_dirty_article_card in dirty_article_cards.table.items():
        try:
            an_article_code = all_the_article_codes[a_dirty_article_card["article_code"]]
            new_article_card = ArticleCard(
                brand=a_dirty_article_card["brand"],
                description=a_dirty_article_card["description"],
                package=a_dirty_article_card["package"],
                article_code=an_article_code,
            )
            session.add(new_article_card)
        except Exception as panic:
            session.rollback()
            logging.error(f"                     key: {key:s}")
            logging.error(f"    a_dirty_article_card: {str(a_dirty_article_card):s}")
            message = f"*** bulk_insert_article_cards error ({classname(panic):s}): {str(panic):s}"
            raise DatabaseException(message)
    session.commit()
    logging.info("bulk_insert_article_cards stop")


def insert_price(
    session: Session,
    amount: int,
    timestamp: Timestamp,
    article_code: ArticleCode,
    point_of_sale: PointOfSale
) -> None:
    """
    Inserts a Price into the database if a price with the given attributes
    does not already exist.

    Args:
        session: The SQLAlchemy Session to use.
        amount: The amount of the price.
        timestamp: The the timestamp associated with the price.
        article_code: The article code associated with the price.
        point_of_sale: The point of sale associated with the price.

    Returns: None
    """

    # Check if a Price with the given attributes already exists
    existing_price = session.execute(
        select(Price).filter_by(
            timestamp=timestamp,
            article_code=article_code,
            point_of_sale=point_of_sale,
        )
    ).scalar_one_or_none()

    if existing_price:
        message = f"insert_price error: {timestamp} - {article_code} - {point_of_sale}"
        raise DatabaseException(message)
    else:
        # Create a new Price object
        new_price = Price(
            amount=amount,
            timestamp=timestamp,
            article_code=article_code,
            point_of_sale=point_of_sale,
        )

        # Add the new Price to the session
        session.add(new_price)


def bulk_insert_prices(
    session: Session,
    dirty_prices: DirtyEvents,
    all_the_timestamps: dict[str, Timestamp],
    all_the_article_codes: dict[str, ArticleCode],
    all_the_points_of_sale: dict[str, PointOfSale]
) -> None:
    logging.info("bulk_insert_prices start")
    for key, a_dirty_price in dirty_prices.table.items():
        try:
            timestamp = all_the_timestamps[a_dirty_price["timestamp"]]
            article_code = all_the_article_codes[a_dirty_price["article_code"]]
            point_of_sale = all_the_points_of_sale[a_dirty_price["point_of_sale_code"]]
            insert_price(
                session,
                a_dirty_price["amount"],
                timestamp,
                article_code,
                point_of_sale
            )
        except Exception as panic:
            session.rollback()
            message = f"*** bulk_insert_prices error: {str(panic):s}"
            raise DatabaseException(message)
    session.commit()
    logging.info("bulk_insert_prices stop")


def get_all_the_states(session: Session) -> dict[str, State]:
    # Create a select statement
    statement = select(State)
    # Execute the statement and fetch all results
    states = list(session.scalars(statement).all())
    return {a_state.code: a_state for a_state in states}


def get_all_the_cities(session: Session) -> dict[str, City]:
    # Create a select statement
    statement = select(City)
    # Execute the statement and fetch all results
    cities = list(session.scalars(statement).all())
    return {get_stringy([a_city.state.code, a_city.name]): a_city for a_city in cities}


def get_all_the_places(session: Session) -> dict[str, Place]:
    # Create a select statement
    statement = select(Place)
    # Execute the statement and fetch all results
    all_the_places = list(session.scalars(statement).all())
    return {
        get_stringy([
            a_place.city.state.code,
            a_place.city.name,
            a_place.address]
        ): a_place for a_place in all_the_places
    }


def get_all_the_points_of_sale(session: Session) -> dict[str, PointOfSale]:
    # Create a select statement
    statement = select(PointOfSale)
    # Execute the statement and fetch all results
    all_the_points_of_sale = list(session.scalars(statement).all())
    return {pos.code: pos for pos in all_the_points_of_sale}


def get_all_the_timestamps(session: Session) -> dict[str, Timestamp]:
    # Create a select statement
    statement = select(Timestamp)
    # Execute the statement and fetch all results
    timestamps = list(session.scalars(statement).all())
    return {repr(ts): ts for ts in timestamps}


def get_all_the_article_codes(session: Session) -> dict[str, ArticleCode]:
    # Create a select statement
    statement = select(ArticleCode)
    # Execute the statement and fetch all results
    article_codes = list(session.scalars(statement).all())
    return {ac.code: ac for ac in article_codes}


def database_create_sqlite(
    kilo_paths: KiloPaths,
    dirty_timestamps: DirtyEvents,
    dirty_states: DirtyEvents,
    dirty_cities: DirtyEvents,
    dirty_places: DirtyEvents,
    dirty_points_of_sale: DirtyEvents,
    dirty_article_codes: DirtyEvents,
    dirty_article_cards: DirtyEvents,
    dirty_prices: DirtyEvents
) -> None:
    storage = kilo_paths.storage
    results = kilo_paths.results
    precios_claros = "precios_claros"
    storage_precios_claros = get_container(storage, precios_claros)
    results_precios_claros = get_container(results, precios_claros)
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    db_uri = str(Path(storage_precios_claros_sqlite, "mecon").with_suffix(".db"))
    with db_create_session(db_uri) as session:
        bulk_insert_states(session, dirty_states)
        db_states = get_all_the_states(session)
        bulk_insert_cities(session, dirty_cities, db_states)
        db_cities = get_all_the_cities(session)
        bulk_insert_places(session, dirty_places, db_cities)
        db_places = get_all_the_places(session)
        bulk_insert_timestamps(session, dirty_timestamps)
        db_timestamps = get_all_the_timestamps(session)
        bulk_insert_points_of_sale(session, dirty_points_of_sale, db_places)
        db_points_of_sale = get_all_the_points_of_sale(session)
        bulk_insert_article_codes(session, dirty_article_codes)
        db_article_codes = get_all_the_article_codes(session)
        bulk_insert_article_cards(session, dirty_article_cards, db_article_codes)
        bulk_insert_prices(session, dirty_prices, db_timestamps, db_article_codes, db_points_of_sale)

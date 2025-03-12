import logging
from pathlib import Path 

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from components.helpers.helpers import get_container, get_stringy
from components.dirty_events.dirty_events import DirtyEvents
from components.kilo.kilo_paths import KiloPaths

from components.precios_claros.database import (
    ArticleCode,
    ArticleRepresentation,
    State, 
    City, 
    Place,
    PointOfSaleCode,
    PointOfSaleRepresentation,
    Timestamp, 
    Price,
    db_create_session, 
)

class DatabaseException(Exception):
    pass

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
        message = f"*** bulk_insert_timestamps error: {str(panic):s}"
        logging.error(message)
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
        message = f"*** bulk_insert_states error: {str(panic):s}"
        logging.error(message)
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_states stop")



def bulk_insert_cities(session: Session, dirty_cities: DirtyEvents, db_states: dict[str, State]) -> None:
    logging.info("bulk_insert_cities start")
    try:
        bulk = [{"name": a_dirty_city["name"],
                 "state_id": db_states[a_dirty_city["state_code"]].id
                 }
                for key, a_dirty_city in dirty_cities.table.items()
        ]
        session.execute(insert(City), bulk)
        session.commit()
    except Exception as panic:
        session.rollback()
        message = f"*** bulk_insert_cities error: {str(panic):s}"
        logging.error(message)
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_cities stop")


def bulk_insert_places(session: Session, dirty_places: DirtyEvents, db_cities: dict[str, City]) -> None:
    logging.info("bulk_insert_places start")
    try:
        bulk = [{"address": a_dirty_place["address"], "city_id": db_cities[a_dirty_place["stringy_city"]].id}
                for key, a_dirty_place in dirty_places.table.items()
        ]
        session.execute(insert(Place), bulk)
        session.commit()
    except Exception as panic:
        session.rollback()
        message = f"*** bulk_insert_places error: {str(panic):s}"
        logging.error(message)
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_places stop")


def bulk_insert_point_of_sale_codes(
    session: Session,
    dirty_point_of_sale_codes: DirtyEvents
) -> None:
    logging.info("bulk_insert_point_of_sale_codes start")
    try:
        bulk = [{"code": a_dirty_point_of_sale_code["point_of_sale_code"]}
                for key, a_dirty_point_of_sale_code in dirty_point_of_sale_codes.table.items()
        ]
        session.execute(insert(PointOfSaleCode), bulk)
        session.commit()
    except Exception as panic:
        session.rollback()
        message = f"*** bulk_insert_point_of_sale_codes error: {str(panic):s}"
        logging.error(message)
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_point_of_sale_codes stop")


def bulk_insert_point_of_sale_representations(
    session: Session,
    dirty_point_of_sale_representations: DirtyEvents,
    all_the_point_of_sale_codes: dict[str, PointOfSaleCode],
    all_the_places: dict[str, Place]
) -> None:
    logging.info("bulk_insert_point_of_sale_representations start")
    try:
        bulk = [{"flag": value["flag"],
                 "business": value["business"],
                 "branch": value["branch"],
                 "point_of_sale_code_id": all_the_point_of_sale_codes[value["point_of_sale_code"]].id,
                 "place_id": all_the_places[value["stringy_place"]].id
                 }
                for key, value in dirty_point_of_sale_representations.table.items()
        ]
        session.execute(insert(PointOfSaleRepresentation), bulk)
        session.commit()
    except Exception as panic:
        session.rollback()
        message = f"*** bulk_insert_point_of_sale_representations error: {str(panic):s}"
        logging.error(message)
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_point_of_sale_representations stop")


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
        message = f"*** bulk_insert_article_codes error: {str(panic):s}"
        logging.error(message)
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_article_codes stop")


def bulk_insert_article_representations(
    session: Session,
    dirty_article_representations: DirtyEvents,
    all_the_article_codes: dict[str, ArticleCode]
) -> None:
    logging.info("bulk_insert_article_representations start")
    try:
        bulk = [{"brand": a_dirty_article_representation["brand"],
                 "description": a_dirty_article_representation["description"],
                 "package": a_dirty_article_representation["package"],
                 "article_code_id": all_the_article_codes[a_dirty_article_representation["article_code"]].id,
                 }
                for key, a_dirty_article_representation in dirty_article_representations.table.items()
        ]
        session.execute(insert(ArticleRepresentation), bulk)
        session.commit()
    except Exception as panic:
        session.rollback()
        message = f"*** bulk_insert_article_representations error: {str(panic):s}"
        logging.error(message)
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_point_of_sale_representations stop")

def bulk_insert_prices(
    session: Session,
    dirty_prices: DirtyEvents,
    all_the_timestamps: dict[str, Timestamp],
    all_the_article_codes: dict[str, ArticleCode],
    all_the_point_of_sale_codes: dict[str, PointOfSaleCode]) -> None:
    logging.info("bulk_insert_prices start")
    try:
        bulk = [{"amount": a_dirty_price["amount"],
                 "timestamp_id": all_the_timestamps[a_dirty_price["timestamp"]].id,
                 "article_code_id": all_the_article_codes[a_dirty_price["article_code"]].id,
                 "point_of_sale_code_id": all_the_point_of_sale_codes[a_dirty_price["point_of_sale_code"]].id,
                 }
                for key, a_dirty_price in dirty_prices.table.items()
        ]
        session.execute(insert(Price), bulk)
        session.commit()
    except Exception as panic:
        session.rollback()
        message = f"*** bulk_insert_prices error: {str(panic):s}"
        logging.error(message)
        raise DatabaseException(message)
    else:
        logging.info("bulk_insert_prices stop")


def get_all_the_states(session: Session) -> dict[str, State]:
    # Create a select statement
    statement = select(State)
    # Execute the statement and fetch all results
    states = list(session.scalars(statement).all())
    return {s.code: s for s in states}


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
        get_stringy([place.city.state.code, place.city.name, place.address]): place for place in all_the_places
    }

def get_all_the_point_of_sale_codes(session: Session) -> dict[str, PointOfSaleCode]:
    # Create a select statement
    statement = select(PointOfSaleCode)
    # Execute the statement and fetch all results
    point_of_sale_codes = list(session.scalars(statement).all())
    return {pos.code: pos for pos in point_of_sale_codes}

def get_all_the_point_of_sale_representations(session: Session) -> dict[str, PointOfSaleRepresentation]:
    # Create a select statement
    statement = select(PointOfSaleRepresentation)
    # Execute the statement and fetch all results
    point_of_sale_representations = list(session.scalars(statement).all())
    return {pos.point_of_sale_code: pos for pos in point_of_sale_representations}

def get_all_the_timestamps(session: Session) -> dict[str, Timestamp]:
    # Create a select statement
    statement = select(Timestamp)
    # Execute the statement and fetch all results
    timestamps = list(session.scalars(statement).all())
    return {repr(tt): tt for tt in timestamps}

def get_all_the_article_codes(session: Session) -> dict[str, ArticleCode]:
    # Create a select statement
    statement = select(ArticleCode)
    # Execute the statement and fetch all results
    article_codes = list(session.scalars(statement).all())
    return {ac.code: ac for ac in article_codes}

def create_sqlite_database(
    kilo_paths: KiloPaths,
    dirty_timestamps: DirtyEvents,
    dirty_states: DirtyEvents,
    dirty_cities: DirtyEvents,
    dirty_places: DirtyEvents,
    dirty_point_of_sale_codes: DirtyEvents,
    dirty_point_of_sale_representations: DirtyEvents,
    dirty_article_codes: DirtyEvents,
    dirty_article_representations: DirtyEvents,
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
        bulk_insert_point_of_sale_codes(session, dirty_point_of_sale_codes)
        db_point_of_sale_codes = get_all_the_point_of_sale_codes(session)
        bulk_insert_point_of_sale_representations(
            session,
            dirty_point_of_sale_representations,
            db_point_of_sale_codes,
            db_places
        )
        db_points_of_sale_representations = get_all_the_point_of_sale_representations(session)
        bulk_insert_article_codes(session, dirty_article_codes)
        db_article_codes = get_all_the_article_codes(session)
        bulk_insert_article_representations(session, dirty_article_representations, db_article_codes)
        bulk_insert_prices(session, dirty_prices, db_timestamps, db_article_codes, db_point_of_sale_codes)

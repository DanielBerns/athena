import pdb
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import List, Optional, Generator
from pathlib import Path
import logging
import os
from collections import defaultdict, Counter

# Assuming the database models (Base, ArticleCard, etc.) are defined
# exactly as in the provided database.py file.
# Make sure database.py is in the same directory or accessible in the Python path.

from components.kilo.kilo_paths import KiloPaths

from components.precios_claros.database import db_get_session, ArticleCard
from components.precios_claros.db_interface_basic_queries import (
    DBInterfaceBasicQueries,
    geometric_mean_times_100
)
from components.helpers.helpers import get_container, get_resource, measure_execution_time


def get_article_cards_by_brand(db_uri: str) -> None:
    """
    Queries the database for all ArticleCard objects, ordered by brand.

    Args:
        db_uri: Optional; The database connection URI.
                If None, uses an in-memory SQLite database (as defined in db_get_session).
                Example for a file-based SQLite DB: "my_database.db"

    Returns:
        A list of ArticleCard objects ordered by brand.
    """
    # Use the context manager from database.py to handle the session
    with db_get_session(db_uri) as session:
        logging.info("Database session started.")

        # Build the query using SQLAlchemy ORM
        query = session.query(ArticleCard).order_by(ArticleCard.brand) #

        # Execute the query and fetch all results
        cards = query.all()
        logging.info(f"Fetched {len(cards)} ArticleCard(s).")

        if cards:
            logging.info("--- Article Cards by Brand ---")
            grouped_cards = defaultdict(list)
            packages = Counter()
            for a_card in cards:
                grouped_cards[a_card.brand].append((a_card.description, a_card.article_code.code))
                packages[a_card.package] += 1
            for brand, cards_by_brand in grouped_cards.items():
                logging.info(f"brand {brand}")
                for (description, code) in cards_by_brand:
                    logging.info(f"    {description:<70s}: {code}")
                logging.info("______________________________")
            logging.info("--- Article package count ---")
            for key, count in packages.items():
                logging.info(f"{key:>70s}: {count:>6d}")
            logging.info("______________________________")
        else:
            logging.info("No ArticleCard found in the database.")



def main() -> None:
    # script identifier,
    identifier = Path(__file__).stem
    print(f"{__file__}", " - ", identifier)
    log_level = logging.DEBUG
    mode = "live"

    kilo_paths = KiloPaths(mode)

    log_txt = str(get_resource(kilo_paths.logs, identifier, ".txt"))

    logging.basicConfig(
        filename=log_txt,
        filemode="w",
        level=log_level,
        format="%(levelname)s > %(message)s",
    )

    logging.info(f"{identifier} start")

    DB_NAME = os.environ.get("DB_NAME", "mecon_dev")
    logging.info(f"DB_NAME: {DB_NAME}")
    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")

    db_uri = str(get_resource(storage_precios_claros_sqlite, DB_NAME, ".db"))
    get_article_cards_by_brand(db_uri)

if __name__ == "__main__":
   main()

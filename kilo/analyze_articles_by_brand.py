import pdb
from typing import List, Generator, Tuple
from collections import defaultdict
import logging
import os
from pathlib import Path
from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_basic_reader import KiloPreciosClarosBasicReader
from components.precios_claros.db_kilo_precios_claros_reader import (
    DBKiloPreciosClarosReader,
    DBStatesGenerator,
    DBCitiesGenerator
)
from components.precios_claros.database import db_get_session
from components.precios_claros.db_interface_basic_queries import (
    DBInterfaceBasicQueries,
    geometric_mean_times_100
)
from components.helpers.helpers import get_container, get_resource, create_text_file, read_text_lines, measure_execution_time

logger = logging.getLogger(__file__)

class DatabaseQueriesException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logger.error(message)

DB_NAME = os.environ.get("DB_NAME", "mecon_dev")


def get_prices_by_city_time_brand(
    session: Session,
    city_name: str,
    timestamp_str: str,
    brand_name: str
) -> None:
    """
    Finds all prices for a given city, timestamp, and brand, sorted by description.
    """
    print(f"Querying for prices from brand '{brand_name}' in '{city_name}' at '{timestamp_str}'...")

    # 1. Find the target timestamp object from the database
    try:
        dt = Timestamp.from_string(timestamp_str).to_datetime()
        target_timestamp = session.scalar(sa.select(Timestamp).where(Timestamp.year == dt.year, Timestamp.month == dt.month, Timestamp.day == dt.day))
        if not target_timestamp:
            print(f"Error: Timestamp '{timestamp_str}' not found in the database.")
            return
    except Exception as e:
        print(f"Error parsing timestamp: {e}")
        return

def get_price(
    session: Session,
    city_name: str,
    target_timestamp: Timestamp,
    brand: str
) -> Generator[Price, None, None]:
    # 1. Build the query to select prices, joining all necessary tables
    #    and filtering by the three criteria.
    stmt = (
        sa.select(Price, ArticleCard, PointOfSale)
        # We start with Price and join outwards to all related tables
        .join(Price.timestamp)
        .join(Price.article_code).join(ArticleCode.cards)
        .join(Price.point_of_sale).join(PointOfSale.place).join(Place.city)
        # Add all three conditions to the WHERE clause
        .where(
            City.name == city_name,
            Timestamp.id == target_timestamp.id,
            ArticleCard.brand == brand_name
        )
        # Add the sorting logic
        .order_by(
            ArticleCard.description.asc(),
            PointOfSale.business.asc(),
            PointOfSale.branch.asc()
        )
    )

    # 3. Execute query and fetch all results
    results = session.execute(stmt).all()

    if not results:
        print("No prices found for the specified criteria.")
        return
    # 3. yield the sorted results
    print(f"\n--- Found {len(prices)} Prices for Brand '{brand_name}', Sorted by Description ---")
    for price in prices:
        # The relationship from ArticleCode to ArticleCard is one-to-many,
        # so we access the first card.
        card = price.article_code.cards[0]
        # Format the price amount as dollars and cents
        formatted_amount = f"${price.amount / 100:.2f}"
        print(f"- {card.description:<20} | {formatted_amount:>8}")
    print("-----------------------------------------------------------------")




def main() -> None:
    # script identifier,
    identifier = Path(__file__).stem
    print(f"{__file__}", " - ", identifier)
    log_level = logging.DEBUG
    mode = "live"

    kilo_paths = KiloPaths(mode)

    # log_txt = str(get_resource_with_timestamp(kilo_paths.logs, identifier, ".txt"))
    log_txt = str(get_resource(kilo_paths.logs, identifier, ".txt"))

    logging.basicConfig(
        filename=log_txt,
        filemode="w",
        level=log_level,
        format="%(levelname)s > %(message)s",
    )


    logging.info(f"{identifier} start")
    logging.info(f"DB_NAME: {DB_NAME}")
    logging.info("--------------------")
    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    reports_precios_claros = get_container(kilo_paths.reports, "precios_claros")
    descriptions_by_brand_resource = get_resource(reports_precios_claros, "descriptions_by_brand", ".md")
    code_and_description_by_brand_resource = get_resource(reports_precios_claros, "code_and_description_by_brand", ".md")

    check_this_resource = get_resource(reports_precios_claros, "check_this", ".txt")

    db_uri = str(get_resource(storage_precios_claros_sqlite, DB_NAME, ".db"))
    with db_get_session(db_uri) as session:
        db = DBInterfaceBasicQueries(session)
        db.get_all_the_states()
        db.get_all_the_cities()
        db.get_all_the_places()
        db.get_all_the_points_of_sale()
        db.get_all_the_article_codes()
        db.get_all_the_article_cards()
        db.get_all_the_timestamps()

        description_by_brands = defaultdict(list)
        article_code_by_brands = defaultdict(list)
        check_this = []

        for key, article_card in db.all_the_article_cards.items():
            description_0, brand_0 = article_card.description, article_card.brand
            description_1, brand_1 = description_0.strip(), brand_0.strip()
            parts = description_1.split(brand_1)
            if len(parts) == 2:
                clean_description = parts[0]
                clean_brand = brand_1
                description_by_brands[clean_brand].append(clean_description)
                article_code_by_brands[brand_1].append(
                    (article_card.article_code.code, clean_description)
                )
            else:
                check_this.append(f"{article_card.id} - {description_1} - {brand_1}")


        with create_text_file(descriptions_by_brand_resource) as text:
            text.write("# Descriptions by brand\n\n")
            brands = [bbb for bbb in description_by_brands.keys()]
            sorted_brands = sorted(brands)
            for brand in sorted_brands:
                text.write(f"## {brand}\n\n")
                descriptions = description_by_brands[brand]
                sorted_descriptions = sorted(descriptions)
                for number, this_description in enumerate(sorted_descriptions):
                    text.write(f"{number+1:>3d}. {this_description}\n")
                text.write("\n\n")

        with create_text_file(code_and_description_by_brand_resource) as text:
            text.write("# Article code and description by brand\n\n")
            brands = [bbb for bbb in article_code_by_brands.keys()]
            sorted_brands = sorted(brands)
            for brand in sorted_brands:
                text.write(f"## {brand}\n\n")
                tuples_code_and_description = article_code_by_brands[brand]
                for number, (code, description) in enumerate(tuples_code_and_description):
                    text.write(f"{number+1:>3d}. {code:>40s} - {description}\n")
                text.write("\n\n")


        with create_text_file(check_this_resource) as text:
            for message in check_this:
                text.write(f"{message}\n")

    logging.info(f"{identifier} stop")


if __name__ == "__main__":
    # 20250529
    main()


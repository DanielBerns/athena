# query_prices.py

import sqlalchemy as sa
from sqlalchemy.orm import Session
from collections import defaultdict
from datetime import datetime

from database import (
    db_get_session,
    Timestamp,
    City,
    State,
    Place,
    PointOfSale,
    ArticleCode,
    ArticleCard,
    Price
)

# --- Configuration ---
DATABASE_URI = "your_database.db"

# Define the City, Timestamp, and Brand you want to query.
TARGET_CITY_NAME = "Central City"
TARGET_TIMESTAMP_STR = "20250620100000"
TARGET_BRAND = "BrandX" # We've added a brand filter


def add_sample_data(session: Session):
    """
    Adds a set of sample data to the database for testing the query.
    This function can be safely run multiple times.
    NOTE: I've added a second PointOfSale to better demonstrate sorting.
    """
    print("--- Adding/Updating Sample Data for Demonstration ---")

    # Location Data
    state = session.scalar(sa.select(State).where(State.name == "CW"))
    if not state: state = State(code="CW", name="CW")
    city = session.scalar(sa.select(City).where(City.name == TARGET_CITY_NAME))
    if not city: city = City(name=TARGET_CITY_NAME, state=state)
    place1 = session.scalar(sa.select(Place).where(Place.address == "123 Main St"))
    if not place1: place1 = Place(address="123 Main St", city=city)
    place2 = session.scalar(sa.select(Place).where(Place.address == "456 Oak Ave"))
    if not place2: place2 = Place(address="456 Oak Ave", city=city)

    pos1 = session.scalar(sa.select(PointOfSale).where(PointOfSale.code == "POS001"))
    if not pos1: pos1 = PointOfSale(code="POS001", flag="FLAG-A", business="SuperMart", branch="Downtown", place=place1)
    pos2 = session.scalar(sa.select(PointOfSale).where(PointOfSale.code == "POS002"))
    if not pos2: pos2 = PointOfSale(code="POS002", flag="FLAG-B", business="GrocerPlus", branch="Westside", place=place2)



    # Article Data
    articles_to_add = [
        {"code": "A001", "brand": "BrandX", "desc": "Premium Soda", "pkg": "12oz Can"},
        {"code": "A002", "brand": "BrandX", "desc": "Diet Soda", "pkg": "12oz Can"},
        {"code": "B001", "brand": "BrandY", "desc": "Spring Water", "pkg": "16oz Bottle"},
    ]
    article_codes = {}
    for ad in articles_to_add:
        ac = session.scalar(sa.select(ArticleCode).where(ArticleCode.code == ad["code"]))
        if not ac:
            ac = ArticleCode(code=ad["code"])
            card = ArticleCard(brand=ad["brand"], description=ad["desc"], package=ad["pkg"], article_code=ac)
            session.add_all([ac, card])
        article_codes[ad["code"]] = ac

    # Timestamp and Price Data
    dt = Timestamp.from_string(TARGET_TIMESTAMP_STR).to_datetime()
    ts = session.scalar(sa.select(Timestamp).where(Timestamp.year == dt.year, Timestamp.month == dt.month, Timestamp.day == dt.day))
    if not ts: ts = Timestamp.from_datetime(dt)

    # Add prices for both points of sale
    session.merge(Price(amount=199, timestamp=ts, article_code=article_codes["A001"], point_of_sale=pos1))
    session.merge(Price(amount=189, timestamp=ts, article_code=article_codes["A002"], point_of_sale=pos1))
    session.merge(Price(amount=205, timestamp=ts, article_code=article_codes["A001"], point_of_sale=pos2))
    session.merge(Price(amount=179, timestamp=ts, article_code=article_codes["A002"], point_of_sale=pos2))
    session.merge(Price(amount=150, timestamp=ts, article_code=article_codes["B001"], point_of_sale=pos1))

    session.commit()
    print("--- Sample Data Setup Complete ---\n")


def query_prices_by_city_time_brand(session: Session, city_name: str, timestamp_str: str, brand_name: str):
    """
    Finds and sorts prices for a given city, timestamp, and brand.
    """
    print(f"Querying for Brand '{brand_name}' in '{city_name}' at '{timestamp_str}'...")

    # 1. Find the target timestamp object
    dt = Timestamp.from_string(timestamp_str).to_datetime()
    target_timestamp = session.scalar(sa.select(Timestamp).where(Timestamp.year == dt.year, Timestamp.month == dt.month))
    if not target_timestamp:
        print(f"Error: Timestamp '{timestamp_str}' not found.")
        return

    # 2. Build the query to select Price and related info
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

    # 4. Display the results in a formatted table
    print("\n--- Price Report ---")
    print(f"{'Description':<20} | {'Point of Sale':<25} | {'Price'}")
    print("-" * 58)
    for price, card, pos in results:
        # The price is an integer (e.g., 199), so we format it as dollars and cents
        formatted_price = f"${price.amount / 100:.2f}"
        pos_name = f"{pos.business} ({pos.branch})"
        print(f"{card.description:<20} | {pos_name:<25} | {formatted_price}")
    print("-" * 58)


def main():
    """Main function to connect to the DB and run the query."""
    with db_get_session(DATABASE_URI) as session:
        add_sample_data(session)
        query_prices_by_city_time_brand(session, TARGET_CITY_NAME, TARGET_TIMESTAMP_STR, TARGET_BRAND)


if __name__ == "__main__":
    main()

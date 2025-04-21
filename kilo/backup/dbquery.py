import sqlalchemy as sa
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple, Callable
from datetime import datetime

def get_prices_by_article_code_city_and_timestamp(
    session: Session,
    city_name: str,
    timestamp: datetime,
    aggregation_func: Callable[[sa.Column], sa.Function] = sa.func.avg
) -> List[Tuple[str, Optional[int], Optional[int], Optional[float]]]:
    """
    Retrieves the minimum, maximum, and a custom aggregated price for each article code
    within a specified city and at a given timestamp.

    Args:
        session: The SQLAlchemy session.
        city_name: The name of the city to filter by.
        timestamp: The datetime to filter by.
        aggregation_func: The SQLAlchemy function to use for aggregation
            (e.g., sa.func.avg, sa.func.min, sa.func.max, or a custom function).
            Defaults to sa.func.avg (arithmetic average).

    Returns:
        A list of tuples. Each tuple contains:
        - The article code (str).
        - The minimum price (int or None).
        - The maximum price (int or None).
        - The aggregated price, calculated using aggregation_func (float or None).
    """
    # Convert the datetime object into a Timestamp object using the from_datetime method.
    timestamp_obj = Timestamp.from_datetime(timestamp)

    # Construct the SQLAlchemy query.
    query = session.query(
        ArticleCode.code,
        sa.func.min(Price.amount).label("min_price"),
        sa.func.max(Price.amount).label("max_price"),
        aggregation_func(Price.amount).label("aggregated_price"),
    )\
    .join(Price, Price.article_code_id == ArticleCode.id)\
    .join(PointOfSale, Price.point_of_sale_id == PointOfSale.id)\
    .join(Place, PointOfSale.place_id == Place.id)\
    .join(City, Place.city_id == City.id)\
    .join(Timestamp, Price.timestamp_id == Timestamp.id)\
    .filter(City.name == city_name)\
    .filter(Timestamp.year == timestamp_obj.year,
            Timestamp.month == timestamp_obj.month,
            Timestamp.day == timestamp_obj.day,
            Timestamp.hour == timestamp_obj.hour,
            Timestamp.minute == timestamp_obj.minute,
            Timestamp.second == timestamp_obj.second)\
    .group_by(ArticleCode.code)

    # Execute the query.
    results = query.all()
    return results

def geometric_mean_times_100(column: sa.Column) -> sa.Function:
    """
    Calculates the geometric mean of a column, multiplies it by 100,
    and returns the integer part.  This is implemented using SQLAlchemy
    functions.

    Args:
        column: The SQLAlchemy column to calculate the geometric mean of.

    Returns:
        A SQLAlchemy function representing the calculated value.
    """
    return sa.cast(100 * sa.func.exp(sa.func.sum(sa.func.log(column)) / sa.func.count(column)), sa.Integer)

def main():
    """
    Main function to demonstrate the usage of get_prices_by_article_code_city_and_timestamp
    with a custom aggregation function (geometric mean).
    """
    # Example usage:
    city_name = "Some City"  # Replace with an actual city name from your database
    timestamp_str = "20230115120000" # Replace with an actual timestamp
    timestamp_dt = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")

    # Create a dummy database for testing
    engine = sa.create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    # Create a session
    with SessionLocal() as session:
        # Populate the database with dummy data
        city = City(name=city_name)
        session.add(city)
        timestamp_obj = Timestamp.from_datetime(timestamp_dt)
        session.add(timestamp_obj)
        article_code1 = ArticleCode(code="ABC")
        article_code2 = ArticleCode(code="XYZ")
        session.add_all([article_code1, article_code2])
        place = Place(city=city, address="123 Main St")
        session.add(place)
        pos1 = PointOfSale(place=place, code="POS1", flag="Flag1", business="Business1", branch="Branch1")
        pos2 = PointOfSale(place=place, code="POS2", flag="Flag2", business="Business2", branch="Branch2")
        session.add_all([pos1, pos2])
        session.flush() # Make sure to flush before adding prices, so POS ids are available.

        session.add_all([
            Price(amount=100, timestamp=timestamp_obj, article_code=article_code1, point_of_sale=pos1),
            Price(amount=200, timestamp=timestamp_obj, article_code=article_code1, point_of_sale=pos2),
            Price(amount=150, timestamp=timestamp_obj, article_code=article_code2, point_of_sale=pos1),
            Price(amount=250, timestamp=timestamp_obj, article_code=article_code2, point_of_sale=pos2),
        ])
        session.commit()

        # Call the function with the custom aggregation function
        results = get_prices_by_article_code_city_and_timestamp(
            session, city_name=city_name, timestamp=timestamp_dt, aggregation_func=geometric_mean_times_100
        )

        # Print the results
        print("Results with geometric mean * 100 (integer part):")
        for row in results:
            print(f"Article Code: {row[0]}, Min Price: {row[1]}, Max Price: {row[2]}, Aggregated Price: {row[3]}")

if __name__ == "__main__":
    main()



        # count = 0
        # logging.info("## ArticleCode")
        # for key, article_code in db.all_the_article_codes.items():
        #     if len(article_code.cards) == 0:
        #         logging.error(f"*** Error: article_code: {article_code.code} with no card.")
        #         continue
        #     ac = article_code.cards[0]
        #     logging.info(f"## {article_code.code:s} - {ac.brand} - {ac.description}")
        #
        #     article_code_prices = db.session.scalars(
        #         article_code.prices.select()
        #         # .limit(10)
        #     ).all()
        #     for a_price in article_code_prices:
        #         ts = a_price.timestamp
        #         pos = a_price.point_of_sale
        #         logging.info(
        #             f"   {str(ts):s} - {pos.flag:s} - {pos.place.city.name} - {pos.place.address} - ${a_price.amount/100:>6.2f}"
        #         )
        #     count += 1
        #     if count > 100:
        #        break



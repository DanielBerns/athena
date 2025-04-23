from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional, Any


def get_price_summary(
    session: Session,
    article_code_value: str,
    city_name: str,
    timestamp_value: str,
    custom_aggregation_func: Optional[Any] = None,
) -> dict:
    """
    Retrieves the minimum price, maximum price, and a custom aggregation of the price
    for a given article code, city, and timestamp.

    Args:
        session: The database session.
        article_code_value: The article code to filter by.
        city_name: The city name to filter by.
        timestamp_value: The timestamp string to filter by (format: YYYYMMDDHHMMSS).
        custom_aggregation_func: An optional SQLAlchemy function to use for custom aggregation.
                                 If None, no custom aggregation is performed.

    Returns:
        A dictionary containing the min_price, max_price, and the result of the
        custom aggregation (if provided). Returns None if no matching data is found.
    """

    query = session.query(
        func.min(Price.amount).label("min_price"),
        func.max(Price.amount).label("max_price"),
    )

    if custom_aggregation_func is not None:
        query = query.add_columns(custom_aggregation_func(Price.amount).label("custom_agg"))

    query = query.join(Price.article_code) \
                 .join(Price.point_of_sale) \
                 .join(PointOfSale.place) \
                 .join(Place.city) \
                 .join(Price.timestamp) \
                 .filter(ArticleCode.code == article_code_value) \
                 .filter(City.name == city_name) \
                 .filter(Timestamp.from_string(timestamp_value) == Price.timestamp)  # Assuming Timestamp.from_string exists

    result = query.one_or_none()

    if result:
        result_dict = {
            "min_price": result.min_price,
            "max_price": result.max_price,
        }
        if custom_aggregation_func is not None:
            result_dict["custom_agg"] = result.custom_agg
        return result_dict
    else:
        return None


if __name__ == "__main__":
    # Example Usage (replace with your actual database URI and data)
    db_uri = "your_database_uri.db"  # Replace with your database URI

    with db_get_session(db_uri) as session:
        # Assuming you have data in your database
        article_code = "12345"
        city = "SomeCity"
        timestamp = "20240120103000"

        # Example 1: Get min and max prices
        price_summary = get_price_summary(session, article_code, city, timestamp)
        print("Price Summary:", price_summary)

        # Example 2: Get min, max, and average price
        avg_price_summary = get_price_summary(session, article_code, city, timestamp, func.avg)
        print("Average Price Summary:", avg_price_summary)

        # Example 3: Get min, max, and sum of prices
        sum_price_summary = get_price_summary(session, article_code, city, timestamp, func.sum)
        print("Sum Price Summary:", sum_price_summary)


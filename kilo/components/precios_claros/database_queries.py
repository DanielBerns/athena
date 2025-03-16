import logging

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from components.helpers.helpers import get_stringy

from components.precios_claros.database import (
    Timestamp,
    Tag,
    State,
    City,
    Place,
    PointOfSale,
    ArticleCode,
    ArticleCard,
    Price
)

class DBGet:

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def all_the_states(self) -> dict[str, State]:
        statement = select(State)
        _all_the_states = list(self.session.scalars(statement).all())
        return {a_state.code: a_state for a_state in _all_the_states}

    def all_the_cities(self) -> dict[str, City]:
        statement = select(City)
        _all_the_cities = list(self.session.scalars(statement).all())
        return {get_stringy([a_city.state.code, a_city.name]): a_city
                for a_city in _all_the_cities}

    def all_the_places(self) -> dict[str, Place]:
        statement = select(Place)
        _all_the_places = list(self.session.scalars(statement).all())
        return {
            get_stringy([
                a_place.city.state.code,
                a_place.city.name,
                a_place.address]
            ): a_place for a_place in _all_the_places
        }

    def all_the_points_of_sale(self) -> dict[str, PointOfSale]:
        statement = select(PointOfSale)
        _all_the_points_of_sale = list(self.session.scalars(statement).all())
        return {pos.code: pos for pos in _all_the_points_of_sale}

    def all_the_timestamps(self) -> dict[str, Timestamp]:
        statement = select(Timestamp)
        _all_the_timestamps = list(self.session.scalars(statement).all())
        return {repr(ts): ts for ts in _all_the_timestamps}

    def all_the_article_codes(self) -> dict[str, ArticleCode]:
        statement = select(ArticleCode)
        _all_the_article_codes = list(self.session.scalars(statement).all())
        return {ac.code: ac for ac in _all_the_article_codes}

    def all_the_article_cards(self) -> dict[int, ArticleCard]:
        statement = select(ArticleCard)
        _all_the_article_cards = list(self.session.scalars(statement).all())
        return {ar.article_code_id: ar for ar in _all_the_article_cards}

    def all_the_prices(self) -> dict[int, Price]:
        statement = select(Price)
        _all_the_prices = list(self.session.scalars(statement).all())
        return {pp.article_code_id: pp for pp in _all_the_prices}

# def get_article_list(self) -> List[dict]:
#     """Retrieves a list of articles with code, brand, description, and package."""
#     articles = (
#         session.query(ArticleCode, ArticleCard)
#         .join(ArticleCard, ArticleCode.id == ArticleCard.article_code_id)
#         .all()
#     )
#     return [
#         {
#             "article_code": article_code.code,
#             "brand": article_representation.brand,
#             "description": article_representation.description,
#             "package": article_representation.package,
#         }
#         for article_code, article_representation in articles
#     ]
#
# def get_timestamp_list(self) -> List[dict]:
#     """Retrieves a list of timestamps."""
#     timestamps = session.query(Timestamp).all()
#     return [{"id": ts.id, "timestamp": str(ts)} for ts in timestamps]
#
# def get_point_of_sale_codes_by_city_state(self) -> List[dict]:
#     """Retrieves a list of point_of_sale_codes per city and state with their representations."""
#     point_of_sales = (
#         session.query(
#             State.name.label("state_name"),
#             City.name.label("city_name"),
#             PointOfSaleCode.code.label("point_of_sale_code"),
#             PointOfSaleRepresentation.flag,
#             PointOfSaleRepresentation.business,
#             PointOfSaleRepresentation.branch,
#         )
#         .join(City, State.id == City.state_id)
#         .join(Place, City.id == Place.city_id)
#         .join(PointOfSaleRepresentation, Place.id == PointOfSaleRepresentation.place_id)
#         .join(PointOfSaleCode, PointOfSaleRepresentation.point_of_sale_code_id == PointOfSaleCode.id)
#         .all()
#     )
#     return [
#         {
#             "state_name": state_name,
#             "city_name": city_name,
#             "point_of_sale_code": point_of_sale_code,
#             "flag": flag,
#             "business": business,
#             "branch": branch,
#         }
#         for state_name, city_name, point_of_sale_code, flag, business, branch in point_of_sales
#     ]
#
# def get_prices_by_timestamp_articles_pos(
#     session: Session,
#     timestamp_id: int,
#     article_codes: List[str],
#     point_of_sale_codes: List[str],
# ) -> List[dict]:
#     """Retrieves prices for selected article_codes and point_of_sale_codes at a given timestamp."""
#     article_code_objs = session.query(ArticleCode).filter(ArticleCode.code.in_(article_codes)).all()
#     point_of_sale_code_objs = session.query(PointOfSaleCode).filter(PointOfSaleCode.code.in_(point_of_sale_codes)).all()
#
#     article_ids = [ac.id for ac in article_code_objs]
#     point_of_sale_ids = [pos.id for pos in point_of_sale_code_objs]
#
#     prices = (
#         session.query(
#             Price.amount,
#             ArticleCode.code.label("article_code"),
#             PointOfSaleCode.code.label("point_of_sale_code"),
#             PointOfSaleRepresentation.flag,
#             PointOfSaleRepresentation.business,
#             PointOfSaleRepresentation.branch,
#         )
#         .join(ArticleCode, Price.article_code_id == ArticleCode.id)
#         .join(PointOfSaleCode, Price.point_of_sale_code_id == PointOfSaleCode.id)
#         .join(PointOfSaleRepresentation, PointOfSaleCode.id == PointOfSaleRepresentation.point_of_sale_code_id)
#         .filter(Price.timestamp_id == timestamp_id)
#         .filter(Price.article_code_id.in_(article_ids))
#         .filter(Price.point_of_sale_code_id.in_(point_of_sale_ids))
#         .all()
#     )
#     return [
#         {
#             "amount": amount,
#             "article_code": article_code,
#             "point_of_sale_code": point_of_sale_code,
#             "flag": flag,
#             "business": business,
#             "branch": branch,
#         }
#         for amount, article_code, point_of_sale_code, flag, business, branch in prices
#     ]

# Example Usage
# if __name__ == "__main__":
#     with db_create_session("my_database.db") as session:
#         # Assuming some data has been inserted
#
#         articles = get_article_list(session)
#         print("Articles:", articles)
#
#         timestamps = get_timestamp_list(session)
#         print("Timestamps:", timestamps)
#
#         pos_codes = get_point_of_sale_codes_by_city_state(session)
#         print("Point of Sale Codes:", pos_codes)
#
#         timestamp_id_to_query = 1  # Replace with a valid timestamp ID
#         article_codes_to_query = ["ART123", "ART789"]
#         pos_codes_to_query = ["POS456", "POS101"]
#
#         prices = get_prices_by_timestamp_articles_pos(
#             session, timestamp_id_to_query, article_codes_to_query, pos_codes_to_query
#         )
#         print("Prices:", prices)
#

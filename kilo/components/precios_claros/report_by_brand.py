import pdb
from math import log, pow
from typing import List, Tuple, Protocol
import logging

from components.precios_claros.database import db_get_session
from components.precios_claros.db_interface_basic_queries import DBInterfaceBasicQueries

import sqlalchemy as sa
from sqlalchemy.orm import Session

from components.precios_claros.database import (
    Timestamp,
    Tag,
    State,
    City,
    Place,
    PointOfSale,
    ArticleCode,
    ArticleCard,
    Price,
    db_get_session
)

logger = logging.getLogger(__name__)

class DatabaseQueriesException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logger.error(message)


class Report:
    def __init__(
        self,
        this_timestamp: Timestamp,
        this_city: City,
        rows: List[Tuple[Price, PointOfSale]]
    ) -> None:
        self._timestamp = this_timestamp
        self._city = this_city
        self._rows = List[Tuple[Price, PointOfSale]]

    @property
    def date(self) -> str:
        full_value = repr(self._timestamp)
        return full_value[:8]

    @property
    def city_and_state(self) -> str:
        city_name = self._city.name
        state_name = self._city.state.name
        return f"{city_name} en {state_name}"

    @property
    def min_geomean_max(self) -> Tuple[int, int, int]:
        prices = [this_tuple[0].amount for this_tuple in self.rows]
        min_price = min(prices)
        max_price = max(prices)
        log_float_prices = [log(pp, 10) for pp in prices]
        log_prices_geomean = sum(log_float_prices) / len(log_float_prices) - 2
        geomean = int(10**log_prices_geomean)
        return min_price, geomean, max_price

    @staticmethod
    def cents_to_money(cents: int) -> str:
        return f"{cents/100:>12.2f}"


class Target(Protocol):
    def write(self, report: Report) -> None:
        ...

class ReportBuilder:
    def __init__(self) -> None:
        pass

    def get_report(
        self,
        session: Session,
        target_timestamp: Timestamp,
        this_city: City
    ) -> Report | None:
        # 1. Build the query to select prices, joining all necessary tables
        # #    and filtering by the three criteria.
        # stmt = (
        #     sa.select(Price, ArticleCard, PointOfSale)
        #     # We start with Price and join outwards to all related tables
        #     .join(Price.timestamp)
        #     .join(Price.article_code).join(ArticleCode.cards)
        #     .join(Price.point_of_sale).join(PointOfSale.place).join(Place.city)
        #     # Add all three conditions to the WHERE clause
        #     .where(
        #         City == this_city,
        #         Timestamp.id == target_timestamp.id,
        #         ArticleCard.brand == brand
        #     )
        #     # Add the sorting logic
        #     .order_by(
        #         ArticleCard.description.asc(),
        #         PointOfSale.business.asc(),
        #         PointOfSale.branch.asc()
        #     )
        # )

        stmt = (
            sa.select(Price, PointOfSale)
            # We start with Price and join outwards to all related tables
            .join(Price.timestamp)
            .join(Price.point_of_sale).join(PointOfSale.place).join(Place.city)
            # Add all conditions to the WHERE clause
            .where(
                City == this_city,
                Timestamp.id == target_timestamp.id,
            )
            # Add the sorting logic
            .order_by(
                PointOfSale.business.asc(),
                PointOfSale.branch.asc()
            )
        )

        # 3. Execute query and fetch all results
        results = session.execute(stmt).all()

        if not results:
            logger.warning("No prices found for the specified criteria.")
            return None
        else:
            report = Report(this_timestamp, this_city, results)
            return results

    def execute(
        self,
        db_uri: str,
        timestamp_str: str,
        state_code: str,
        target: Target
    ) -> None:
        with db_get_session(db_uri) as session:
            db = DBInterfaceBasicQueries(session)
            db.get_all_the_states()
            db.get_all_the_cities()
            db.get_all_the_places()
            db.get_all_the_points_of_sale()
            db.get_all_the_article_codes()
            db.get_all_the_article_cards()
            db.get_all_the_timestamps()

            this_state = db.query_state(state_code)
            this_timestamp = db.query_timestamp(timestamp_str)

            all_the_brands: dict[str, bool] = {}
            for key, this_article_code in db.all_the_article_codes.items():
                this_article_card = this_article_code.cards[0]
                brand_0 = this_article_card.brand
                brand_1 = brand_0.strip()
                all_the_brands[brand_1] = True

            for this_city in this_state.cities:
                print(f"{this_city.name}")
                report = self.get_report(session, this_timestamp, this_city)
                if report:
                    target.write(report)
                else:
                    print("null report {this_city.name}")



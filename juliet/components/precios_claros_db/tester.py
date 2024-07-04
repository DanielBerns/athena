# import pdb

from pathlib import Path 
from typing import Dict, Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from components.precios_claros.buckets import Bucket
from components.core import Application, register_error, show, FlatStore
from components.helpers import get_container, get_resource

from components.precios_claros_db.models import (
    Article, 
    State, 
    City, 
    PointOfSale, 
    Timestamp, 
    Price,
    db_create_session, 
    db_open_session
)


class Tester:
   
    @staticmethod
    def get_prices(
        session: Session, 
        points_of_sale_in_db: Dict[int, PointOfSale],
        description: str, 
        this_timestamp: Timestamp) -> None:
        articles_query_by_description = select(Article).where(Article.description == description)
        show(f"{this_timestamp.year:>5d} {this_timestamp.month:>2d} {this_timestamp.day:>2d}")
        result = session.execute(articles_query_by_description)
        for first_number, article in enumerate(result.scalars()):
            show(f"{first_number:d} - {article.code:s} _ {article.description:s} _ {article.brand:s}")
            prices_query_by_article_id = select(Price).where(
                and_(Price.article_id == article.id,
                     Price.timestamp_id == this_timestamp.id
                )
            )
            result = session.execute(prices_query_by_article_id)
            for second_number, price in enumerate(result.scalars()):
                amount = price.value / 100
                pos = points_of_sale_in_db[price.point_of_sale_id]
                show(f"  {second_number:>10d} - {amount:>14.2f} at {pos.code} _ {pos.name:s} {pos.city.name:s} {pos.address:s} _ {pos.city.state.name:s}")
    
    @staticmethod
    def execute(storage: Path, results: Path, reports: Path, alt_db_uri: Optional[str]=None) -> None:
        db_uri = alt_db_uri if alt_db_uri else str(Path(storage).with_suffix(".db")) 
        with db_open_session(db_uri) as session:
            articles_query = select(Article)
            result = session.execute(articles_query)
            for number, article in enumerate(result.scalars()):
                if number % 10000 == 0:
                    show(f"#{number:d} - {article.code:s} {article.description:s}")
            points_of_sale_query = select(PointOfSale)
            result  = session.execute(points_of_sale_query)
            points_of_sale_in_db = {}
            for number, point_of_sale in enumerate(result.scalars()):
                show(f"{number:d} - {point_of_sale.code:s} {point_of_sale.name:s} {point_of_sale.address:s}")
                show(f"  at {point_of_sale.city.name:s} - {point_of_sale.city.state.name:s}")
                points_of_sale_in_db[point_of_sale.id] = point_of_sale
            states_query = select(State)
            result  = session.execute(states_query)
            for number, state in enumerate(result.scalars()):
                show(f"{number:d} - {state.code:s} {state.name:s}")
                for city in state.cities:
                    show(f"  {city.name:s}")
                    for point_of_sale in city.points_of_sale:
                        show(f"    {point_of_sale.code:s}: {point_of_sale.name:s} {point_of_sale.address:s}")
            show("All the timestamps")
            timestamps_query = select(Timestamp)
            rows = session.execute(timestamps_query)
            for number, timestamp in enumerate(rows.scalars()):
                show(f"{number:>10d} - {timestamp.year:d} {timestamp.month:>2d} {timestamp.day:>2d} {timestamp.difference:d}")
            rows = session.execute(timestamps_query)
            for this_number, this_timestamp in enumerate(rows.scalars()):
                show(f"{this_number:d} {this_timestamp.year:d} {this_timestamp.month:>2d} {this_timestamp.day:>2d} {this_timestamp.difference:d}")
                result = session.execute(articles_query)
                count = 0
                for number, article in enumerate(result.scalars()):
                    if number % 10000 == 0:
                        count += 1
                        show(f"#{number:d} - {article.code:s} {article.description:s}")
                        Tester.get_prices(session, points_of_sale_in_db, article.description, this_timestamp)
                show(f"{number:d}: {count:d}")

            results_codes = get_resource(results, "codes", ".md")
            rows = session.execute(articles_query)
            with open(results_codes, 'w') as target:
                for number, article in enumerate(rows.scalars()):
                    target.write(f"{article.code:s}\n")
            

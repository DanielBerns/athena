# import pdb

from collections import Counter
from pathlib import Path 
from typing import Dict, Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from components.precios_claros.buckets import Bucket
from components.precios_claros.io import IO, Sample
from components.core import Application, show, register_error, FlatStore
from components.helpers import get_container

from components.precios_claros.models import Article as DataclassArticle
from components.precios_claros.models import PointOfSale as DataclassPointOfSale

from components.precios_claros_db.models import (
    Article, 
    State, 
    City, 
    Place,
    PointOfSale, 
    Timestamp, 
    Price,
    db_open_session
)


class Updater:
    
    @staticmethod
    def read_timestamp(sample_key: str, session: Session) -> Optional[Timestamp]:    
        _year = int(sample_key[:4])
        _month = int(sample_key[4:6])
        _day = int(sample_key[6:8])
        _difference = int(sample_key[8:])            
        show(f"sample_key {sample_key:s} ==  {_year:d}, {_month:d}, {_day:d}, {_difference:>06d}") 
        timestamp_query = select(Timestamp).where(
            and_(Timestamp.year == _year,
                 Timestamp.month == _month,
                 Timestamp.day == _day,
                 Timestamp.difference == _difference
            )
        )
        results = session.scalars(timestamp_query).all()
        return results[0] if len(results) else None

    @staticmethod
    def create_timestamp(sample_key: str, session: Session) -> Timestamp:    
        _year = int(sample_key[:4])
        _month = int(sample_key[4:6])
        _day = int(sample_key[6:8])
        _difference = int(sample_key[8:])            
        show(f"sample_key {sample_key:s} ==  {_year:d}, {_month:d}, {_day:d}, {_difference:>06d}")            
        timestamp = Timestamp(year=_year, month=_month, day=_day, difference=_difference)
        session.add(timestamp)
        session.commit()
        return timestamp

    @staticmethod
    def read_article(article_code: str, session: Session) -> Optional[Article]:
        articles_query = select(Article).where(
            Article.code == article_code
        )
        results = session.scalars(articles_query).all()
        return results[0] if len(results) else None

    @staticmethod
    def create_article(dataclass_article: DataclassArticle, session: Session) -> Article:    
        article = Article(
            code=dataclass_article.code,
            brand=dataclass_article.brand,
            description=dataclass_article.name,
            packaging=dataclass_article.package
        )
        session.add(article)
        session.commit()
        return article

    @staticmethod
    def read_states(session: Session) -> Dict[str, City]:
        states_query = select(State)
        results = session.scalars(states_query).all()
        return {value.name: value for value in results}

    @staticmethod
    def read_cities(session: Session) -> Dict[str, City]:
        cities_query = select(City)
        results = session.scalars(cities_query).all()
        return {value.name: value for value in results}

    @staticmethod
    def read_places(session: Session) -> Dict[str, Place]:
        places_query = select(Place)
        results = session.scalars(places_query).all()
        return {value.address: value for value in results}
        
    @staticmethod
    def read_points_of_sale(session: Session) -> Dict[str, PointOfSale]:
        points_of_sale_query = select(PointOfSale)
        results = session.scalars(points_of_sale_query).all()
        return {value.code: value for value in results}

    @staticmethod
    def create_point_of_sale(
        dataclass_point_of_sale: DataclassPointOfSale, 
        session: Session
    ) -> PointOfSale:    
        point_of_sale = PointOfSale(
            code=dataclass_point_of_sale.identifier,
            name=dataclass_point_of_sale.name
        )
        session.add(point_of_sale)
        session.commit()
        return point_of_sale
        
    @staticmethod
    def create_state(
        state_name: str,
        session: Session
    ) -> State:
        state = State(name=state_name)
        session.add(state)
        session.commit()
        return state

    @staticmethod
    def create_city(
        city_name: str,
        a_state: State,
        session: Session
    ) -> City:
        city = City(name=city_name, state=a_state)
        session.add(city)
        session.commit()
        return city
    
    @staticmethod
    def create_place(
        an_address: str,
        a_point_of_sale: PointOfSale,
        a_city: City,
        session: Session
    ) -> Place:    
        place = Place(
            address=an_address,
            city=a_city,
            point_of_sale=a_point_of_sale
        )
        session.add(place)
        session.commit()
        return place
    
    @staticmethod
    def execute(application: Application, sample_key: str) -> None:
        storage = application.file_system.storage        
        results = application.file_system.results   
        storage_precios_claros = get_container(storage, "precios_claros")
        results_precios_claros = get_container(results, "precios_claros")
        db_uri=str(Path(storage, "precios_claros").with_suffix(".db"))
        all_the_locations: Counter = Counter()
        all_the_points_of_sale: Counter = Counter()
        with db_open_session(db_uri) as session:
            store = FlatStore(storage_precios_claros, "flatstore")
            store.start()
            sample_home = store.sample_home(sample_key)
            sample = Sample(sample_home)
            sample_points_of_sale_table, sample_articles_reader = IO.read(sample)
            timestamp = Updater.read_timestamp(sample_key, session)
            if timestamp is None:
                timestamp = Updater.create_timestamp(sample_key, session)
            points_of_sale_in_db = Updater.read_points_of_sale(session)
            states_in_db = Updater.read_states(session)
            cities_in_db = Updater.read_cities(session)
            places_in_db = Updater.read_places(session)
            points_of_sale_table, articles_reader = IO.read(sample)
            # pdb.set_trace()
            for location, article_with_prices_table, points_of_sale in IO.iterate(
                sample,
                points_of_sale_table, 
                articles_reader
            ):
                print(location)
                all_the_locations[location] += 1
                _city = Updater.read_city(location)
                for pos in points_of_sale:
                    all_the_points_of_sale[pos.identifier] += 1
                    _point_of_sale = points_of_sale_in_db.get(pos.identifier, None)
                    _place = places_in_db.get(pos.address, None)
                    if _point_of_sale is None:
                        _point_of_sale = Updater.create_point_of_sale(pos, session)
                        points_of_sale_in_db[pos.identifier] = _point_of_sale
                    if _place is None:
                        _place = Updater.create_place(pos, _point_of_sale, _city)
                for awp_number, awp in enumerate(article_with_prices_table.values()):
                    article = Updater.read_article(awp.article.code, session)
                    if article is None:
                        article = Updater.create_article(awp.article, session)
                    else:
                        if article.code == awp.article.code:
                            pass
                        else:
                            show(f"fail code")
                            show(f"sql  {article.code:s} - {article.brand:s} - {article.description:s} - {article.packaging:s}")
                            show(f"json {awp.article.code:s} - {awp.article.brand:s} - {awp.article.name:s} - {awp.article.package:s}")
                            continue
                    _article_id = article.id                        
                    if awp_number % 10 == 0:
                        print(f"# {awp_number:d} from {place:s}")
                        print(f"## {article.code:s}")
                    for pos, _value in awp.prices_per_point_of_sale:
                        _point_of_sale = points_of_sale_in_db.get(pos.identifier, None)
                        if _point_of_sale:
                            _point_of_sale_id = _point_of_sale.id
                            db_price = Price(
                                value=_value, 
                                timestamp_id=timestamp.id,
                                article_id=_article_id,
                                point_of_sale_id=_point_of_sale_id
                            )
                            session.add(db_price)
                            # session.commit()                            
                        else:
                            show(f"Error: {pos.identifier:s} {pos.name:s}")
            session.commit()

            
            

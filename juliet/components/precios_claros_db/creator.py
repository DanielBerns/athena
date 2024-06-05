from pathlib import Path 

from sqlalchemy import select

from components.precios_claros.buckets import Bucket
from components.core import Application, register_error, FlatStore
from components.helpers import get_container



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

class Creator:

    @staticmethod
    def execute(application: Application) -> None:
        storage = application.file_system.storage        
        results = application.file_system.results   
        results_precios_claros = get_container(results, "precios_claros")
        db_uri=str(Path(storage, "precios_claros").with_suffix(".db"))
        with db_create_session(db_uri) as session:
            for number, (key, json_article) in enumerate(Bucket.read(results_precios_claros, "clean_articles", ".md")):
                try:
                    db_article = Article(
                        code=json_article.get('code', 'code_error'),
                        brand=json_article.get('brand', 'brand_error'),
                        description=json_article.get('name', 'name_error'),
                        packaging=json_article.get('package','package_error')
                    )
                    session.add(db_article)
                    if (number % 1000) == 0:
                        print("Articles", number)
                except Exception as panic:
                    register_error(f"Articles {number:d} {str(panic)}")
            session.commit()
            states = {
                "ar-u": "Chubut",
                "ar-z": "Santa Cruz",
                "ar-v": "Tierra del Fuego",
            }
            cities = {
                "comodoro rivadavia": ("Comodoro Rivadavia", "Chubut"),
                "esquel": ("Esquel", "Chubut"),
                "puerto madryn": ("Puerto Madryn", "Chubut"),
                "rada tilly": ("Rada Tilly", "Chubut"),
                "trelew": ("Trelew", "Chubut"),
                "caleta olivia": ("Caleta Olivia", "Santa Cruz"),
                "rio gallegos": ("Rio Gallegos", "Santa Cruz"),
                "puerto madryn": ("Puerto Madryn", "Chubut"),
                "rawson": ("Rawson", "Chubut"),
                "ushuaia": ("Ushuaia", "Tierra del Fuego")
            }
            for key, value in states.items():
                print(key, value)
                db_state = State(code=key, name=value)
                session.add(db_state)
            session.commit()
            for key, (city_name, state_name) in cities.items():
                print(city_name, 'at', state_name)
                state_query = select(State).where(State.name == state_name)
                db_state = session.scalars(state_query).one()
                db_city = City(name=city_name, state=db_state)
                session.add(db_city)
            session.commit()
            
            for number, (key, json_point_of_sale) in enumerate(Bucket.read(results_precios_claros, "clean_points_of_sale", ".md")):
                try:
                    json_city = json_point_of_sale['city']
                    (city_name, state_name) = cities[json_city]
                    city_query = select(City).where(City.name == city_name) 
                    db_city = session.scalars(city_query).one()
                    db_point_of_sale = PointOfSale(
                        code=json_point_of_sale['identifier'],
                        name=json_point_of_sale['name'],
                        address=json_point_of_sale['address'],
                        city=db_city
                    )
                    session.add(db_point_of_sale)
                    if (number % 10) == 0:
                        print("PointsfSale", number)
                except Exception as panic:
                    register_error(f"PointsOfSale {number:d} {str(panic)}")
            session.commit()        

            print("Timestamp")
            store = FlatStore(storage, "flatstore")
            store.start()
            for number, sample_key in enumerate(store.sorted_sample_keys()):
                try:
                    print("sample_key", sample_key, number)
                    _year = int(sample_key[:4])
                    _month = int(sample_key[4:6])
                    _day = int(sample_key[6:8])
                    _difference = int(sample_key[8:])
                    db_timestamp = Timestamp(year=_year, month=_month, day=_day, difference=_difference)
                    session.add(db_timestamp)
                except Exception as panic:
                    register_error(f"Timestamp: {number:d} {sample_key:s} {str(panic):s}")
            session.commit()
            store.stop()


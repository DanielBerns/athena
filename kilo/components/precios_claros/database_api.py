# import pdb

from pathlib import Path 

from sqlalchemy import select, insert

from components.precios_claros.buckets import Bucket
from components.core import Application, show, register_error, FlatStore
from components.helpers import get_container


from components.precios_claros_db.models import (
    Article, 
    State, 
    City, 
    Place,
    PointOfSale, 
    Timestamp, 
    Price,
    db_create_session, 
)

class CreatorException(Exception):
    pass

class Creator:
    
    @staticmethod
    def execute(kilo_paths: KiloPaths) -> None:
        storage = kilo_paths.storage
        results = kilo_paths.results
        precios_claros = "precios_claros"
        storage_precios_claros = get_container(storage, precios_claros)
        results_precios_claros = get_container(results, precios_claros)
        storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
        db_uri = str(Path(storage_precios_claros_sqlite, "mecon").with_suffix(".db"))
        with db_create_session(db_uri) as session:
            logging.info("Articles")
            try:
                bulk = [
                    {"code": article_json.get('code', 'error.code'),
                     "brand": article_json.get('brand', 'error.brand'),
                     "description": article_json.get('description', 'error.description'),
                     "packaging": article_json.get('package','error.package')
                    }
                    for key, article_json in reader.read_articles()
                ] 
                session.execute(insert(Article), bulk)
                session.commit()
            except Exception as panic:
                logging.error(f"Articles {str(panic)}")
                session.rollback()
                raise CreatorException("Articles")

            states = {
              "ar-a": "Salta",
              "ar-b": "Buenos Aires",
              "ar-c": "CABA",
              "ar-d": "San Luis",
              "ar-e": "Entre Rios",
              "ar-f": "La Rioja",
              "ar-g": "Santiago del Estero",
              "ar-h": "Chaco",
              "ar-j": "San Juan",
              "ar-k": "Catamarca",
              "ar-l": "La Pampa",
              "ar-m": "Mendoza",
              "ar-n": "Misiones",
              "ar-p": "Formosa",
              "ar-q": "Neuquén",
              "ar-r": "Río Negro",
              "ar-s": "Santa Fé",
              "ar-t": "Tucumán",
              "ar-u": "Chubut",
              "ar-v": "Tierra del Fuego",
              "ar-w": "Corrientes",
              "ar-x": "Córdoba",
              "ar-y": "San Salvador de Jujuy",
              "ar-z": "Santa Cruz",
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
            show("States")            
            try:
                bulk = [{"code": key, "name": value} for key, value in states.items()] 
                session.execute(insert(State), bulk)
            except Exception as panic:
                register_error(f"States {str(panic)}")
                session.rollback()
                raise CreatorException("States")
            else:
                session.commit()
            
            show("Cities")
            try:
                for key, (city_name, state_name) in cities.items():
                    print(city_name, 'at', state_name)
                    state_query = select(State).where(State.name == state_name)
                    db_state = session.scalars(state_query).one()
                    db_city = City(name=city_name, state=db_state)
                    session.add(db_city)
            except Exception as panic:
                register_error(f"Cities {str(panic)}")
                session.rollback()
                raise CreatorException("Cities")
            else:
                session.commit()

            show("PointOfSale")
            try:
                for number, (key, json_point_of_sale) in enumerate(Bucket.read(results_precios_claros, "clean_points_of_sale", ".md")):                    
                    json_city = json_point_of_sale['city']
                    (city_name, state_name) = cities[json_city]
                    city_query = select(City).where(City.name == city_name) 
                    db_city = session.scalars(city_query).one()
                    db_point_of_sale = PointOfSale(
                         code=json_point_of_sale['identifier'],
                         name=json_point_of_sale['name']
                    )
                    session.add(db_point_of_sale)
            except Exception as panic:
                register_error(f"PointOfSale {str(panic)}")
                session.rollback()
                raise CreatorException("PointOfSale")
            else:
                session.commit()

            show("Places")
            try:
                for key, json_point_of_sale in Bucket.read(results_precios_claros, "clean_points_of_sale", ".md"):
                    json_city = json_point_of_sale['city']
                    (city_name, state_name) = cities[json_city]
                    city_query = select(City).where(City.name == city_name) 
                    db_city = session.scalars(city_query).one()
                    point_of_sale_query = select(PointOfSale).where(PointOfSale.code == json_point_of_sale['identifier']) 
                    db_point_of_sale = session.scalars(point_of_sale_query).one()
                    db_place = Place(
                         address=json_point_of_sale['address'],
                         city=db_city,
                         point_of_sale=db_point_of_sale
                    )
                    session.add(db_place)
            except Exception as panic:
                register_error(f"Places {str(panic)}")
                session.rollback()
                raise CreatorException("Places")
            else:
                session.commit()        

            show("Timestamps")
            # pdb.set_trace()
            store = FlatStore(storage_precios_claros, "flatstore")
            store.start()
            try:
                bulk = [{"year": int(sample_key[:4]),
                         "month": int(sample_key[4:6]),
                         "day": int(sample_key[6:8]),
                         "difference": int(sample_key[8:])
                         } for sample_key in store.sorted_sample_keys()]
                session.execute(insert(Timestamp), bulk)
            except Exception as panic:
                register_error(f"Timestamps {str(panic):s}")
                session.rollback()
                raise CreatorException("Timestamps")                
            else:
                session.commit()
            store.stop()


# import pdb

from typing import Generator
from pathlib import Path
import logging
from components.helpers.helpers import classname, get_stringy
from components.precios_claros.kilo_precios_claros_reader import KiloPreciosClarosReader


class DBKiloPreciosClarosReader:
    def __init__(
        self,
        kilo_precios_claros_reader: KiloPreciosClarosReader
    ) -> None:
        self._reader = kilo_precios_claros_reader

    @property
    def reader(self) -> KiloPreciosClarosReader:
        return self._reader

    def sample_keys_generator(self) -> Generator[str, None, None]:
        for sample_home in self.reader.read_sample_home():
            metadata = self.reader.read_metadata()
            sample_key = metadata["sample_key"]
            yield sample_key

    def points_of_sale_generator(self) -> Generator[dict[str, str], None, None]:
        for sample_home in self.reader.read_sample_home():
            for kilo_json in self.reader.read_points_of_sale():
                yield kilo_json

    def articles_per_point_of_sale_generator(self) -> Generator[dict[str, str], None, None]:
        for sample_home in self.reader.read_sample_home():
            # pdb.set_trace()
            metadata = self.reader.read_metadata()
            sample_key = metadata["sample_key"]
            for kilo_json in self.reader.read_articles_per_point_of_sale():
                kilo_json["sample_key"] = sample_key
                yield kilo_json


class DBStatesGenerator:
    CODES_AND_STATES = {
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
      "buenos aires": "Buenos Aires",
      "catamarca": "Catamarca",
      "chaco": "Chaco",
      "cordoba": "Córdoba",
      "corrientes": "Corrientes",
      "la pampa": "La Pampa",
      "la rioja": "La Rioja",
      "neuquen": "Neuquén",
      "rio negro": "Río Negro",
      "salta": "Salta",
      "san luis": "San Luis",
      "santa fe": "Santa Fe",
      "santiago del estero": "Santiago del Estero",
      "tucuman": "Tucumán",
      "caba": "CABA",
      "jujuy": "Jujuy",
      "formosa": "Formosa",
      "misiones": "Misiones",
      "capital federal": "CABA",
      "mendoza": "Mendoza",
      "error": "Error"
    }

    def __init__(
        self,
        reader: DBKiloPreciosClarosReader
    ) -> None:
        self._reader = reader
        self._table: dict[str, dict[str, str]] = {}

    @property
    def reader(self) -> DBKiloPreciosClarosReader:
        return self._reader

    @property
    def table(self) -> dict[str, dict[str, str]]:
        return self._table

    def iterate(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.generate_states start")
        for record in self.reader.points_of_sale_generator():
            state_code = record["state"]
            state_name = DBStatesGenerator.CODES_AND_STATES.get(state_code, "Error")
            existing_state = self.table.get(state_code, None)
            if existing_state:
                continue
            else:
                self.table[state_code] = state = {"code": state_code, "name": state_name}
                yield state
        logging.info(f"{classname(self)}.generate_states ({len(self.table)}) stop")


class DBCitiesGenerator:
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader,
        known_states: dict[str, bool]
    ) -> None:
        self._reader = reader
        self._know_states = known_states
        self._table: dict[str, bool] = {}

    @property
    def reader(self) -> DBKiloPreciosClarosReader:
        return self._reader

    @property
    def known_states(self) -> dict[str, bool]:
        return self._know_states

    @property
    def table(self) -> dict[str, bool]:
       return  self._table

    def iterate(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.generate_cities start")
        for count, record in enumerate(self.reader.points_of_sale_generator()):
            state_code = record["state"]
            if self.known_states.get(state_code, False):
                stringy_city = get_stringy([record["state"], record["city"]])
                existing_city = self.table.get(stringy_city, False)
                if existing_city:
                    continue
                else:
                    self.table[stringy_city] = True
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.generate_cities; unknown state_code: {state_code} at {count} record")
                for key, value in record.items():
                    logging.error(f"    {key}: {value}")
                logging.error(f"*** Error {classname(self)}.generate_cities; unknown state_code")
        logging.info(f"{classname(self)}.generate_cities ({len(self.table)}) stop")


class DBPlacesGenerator:
    def __init__(self, reader: DBKiloPreciosClarosReader, known_cities: dict[str, bool]) -> None:
        self._reader = reader
        self._known_cities: dict[str, bool] = known_cities
        self._table: dict[str, bool] = {}

    @property
    def reader(self) -> DBKiloPreciosClarosReader:
        return self._reader

    @property
    def known_cities(self) -> dict[str, bool]:
        return self._known_cities

    @property
    def table(self) -> dict[str, bool]:
        return self._table

    def iterate(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.iterate start")
        for count, record in enumerate(self.reader.points_of_sale_generator()):
            a_stringy_city = get_stringy([record["state"], record["city"]])
            if self.known_cities.get(a_stringy_city, False):
                a_stringy_place = get_stringy([record["state"], record["city"], record["address"]])
                existing_place = self.table.get(a_stringy_place, False)
                if existing_place:
                    continue
                else:
                    self.table[a_stringy_place] = True
                    record["stringy_city"] = a_stringy_city
                    record["stringy_place"] = a_stringy_place
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.iterate")
                logging.error(f"{a_stringy_place} - {a_stringy_city} unknown at ({count}) record")
                for key, value in record.items():
                    logging.error(f"    {key}: {value}")
                logging.error(f"*** Error {classname(self)}.iterate")
        logging.info(f"{classname(self)}.iterate stop")


class DBPointsOfSalesGenerator:
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader,
        known_places: dict[str, bool]
    ) -> None:
        self._reader = reader
        self._known_places: dict[str, bool] = known_places
        self._table: dict[str, bool] = {}

    @property
    def reader(self) -> DBKiloPreciosClarosReader:
        return self._reader

    @property
    def known_places(self) -> dict[str, bool]:
        return self._known_places

    @property
    def table(self) -> dict[str, bool]:
        return self._table

    def iterate(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.generate_points_of_sale start")
        for count, record in enumerate(self.reader.points_of_sale_generator()):
            a_stringy_place = get_stringy([record["state"], record["city"], record["address"]])
            if self.known_places.get(a_stringy_place, False):
                new_point_of_sale_code_string = get_stringy([record["point_of_sale_code"], record["business"]])
                existing_point_of_sale = self.table.get(new_point_of_sale_code_string, False)
                if existing_point_of_sale:
                    continue
                else:
                    self.table[new_point_of_sale_code_string] = True
                    record["stringy_place"] = a_stringy_place
                    record["new_point_of_sale_code"] = new_point_of_sale_code_string
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.generate_points_of_sale: {a_stringy_city} unknown at ({count}) record")
                for key, value in record.items():
                    logging.error(f"    {key}: {value}")
                logging.error(f"*** Error {classname(self)}.generate_points_of_sale")
        logging.info(f"{classname(self)}.generate_points_of_sale stop")


class DBArticleCodesGenerator:
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader
    ) -> None:
        self._reader = reader
        self._table: dict[str, bool] = {}

    @property
    def reader(self) -> DBKiloPreciosClarosReader:
        return self._reader

    @property
    def table(self) -> dict[str, bool]:
        return self._table

    def iterate(self) -> Generator[dict[str, str], None, None]:
        # pdb.set_trace()
        logging.info(f"{classname(self)}.iterate start")
        for record in self.reader.articles_per_point_of_sale_generator():
            article_code_string = record["article_code"]
            existing_article_code = self.table.get(article_code_string, False)
            if existing_article_code:
                continue
            else:
                self.table[article_code_string] = True
                yield record
        logging.info(f"{classname(self)}.iterate ({len(self.table)}) stop")


class DBArticleCardsGenerator:
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader,
        article_codes: dict[str, bool]
    ) -> None:
        self._reader = reader
        self._article_codes = article_codes
        self._table: dict[str, bool] = {}

    @property
    def reader(self) -> DBKiloPreciosClarosReader:
        return self._reader

    @property
    def article_codes(self) -> dict[str, bool]:
        return self._article_codes

    @property
    def table(self) -> dict[str, bool]:
        return self._table

    def generate_article_cards(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.iterate start")
        for count, record in enumerate(self.reader.articles_per_point_of_sale_generator()):
            article_code_string = record["article_code"]
            if self.article_codes.get(article_code_string, False):
                brand = record["brand"]
                description = record["description"]
                package = record["package"]
                stringy_article_card = get_stringy([article_code_string, brand, description, package])
                existing_article_card = self.table.get(stringy_article_card, False)
                if existing_article_card:
                    continue
                else:
                    self.table[stringy_article_card] = True
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.generate_article_card: unknown article_code {article_code_string} at {count} record")
                for key, value in record.items():
                    logging.error(f"    {key}: {value}")
                logging.error(f"*** Error {classname(self)}.generate_article_card")
        logging.info(f"{classname(self)}.iterate stop")

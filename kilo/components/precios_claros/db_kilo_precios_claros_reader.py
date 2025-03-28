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
                city_key = record["city_key"]
                existing_city = self.table.get(city_key, False)
                if existing_city:
                    continue
                else:
                    self.table[city_key] = True
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
            a_city_key = record["city_key"]
            if self.known_cities.get(a_city_key, False):
                a_place_key = record["place_key"]
                existing_place = self.table.get(a_place_key, False)
                if existing_place:
                    continue
                else:
                    self.table[a_place_key] = True
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.iterate")
                logging.error(f"{a_place_key} - {a_city_key} unknown at ({count}) record")
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
            a_place_key = record["place_key"]
            if self.known_places.get(a_place_key, False):
                a_point_of_sale_key = record["point_of_sale_key"]
                existing_point_of_sale = self.table.get(a_point_of_sale_key, False)
                if existing_point_of_sale:
                    continue
                else:
                    self.table[a_point_of_sale_key] = True
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.generate_points_of_sale: {a_city_key} unknown at ({count}) record")
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

    def iterate(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.iterate start")
        for count, record in enumerate(self.reader.articles_per_point_of_sale_generator()):
            article_code_string = record["article_code"]
            if self.article_codes.get(article_code_string, False):
                brand = record["brand"]
                description = record["description"]
                package = record["package"]
                article_card_key = record["article_card_key"]
                existing_article_card = self.table.get(article_card_key, False)
                if existing_article_card:
                    continue
                else:
                    self.table[article_card_key] = True
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.generate_article_card: unknown article_code {article_code_string} at {count} record")
                for key, value in record.items():
                    logging.error(f"    {key}: {value}")
                logging.error(f"*** Error {classname(self)}.generate_article_card")
        logging.info(f"{classname(self)}.iterate stop")


class DBPricesGenerator:
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader,
        timestamps: dict[str, bool],
        article_codes: dict[str, bool],
        points_of_sale: dict[str, bool]
    ) -> None:
        self._reader = reader
        self._timestamps = timestamps
        self._article_codes = article_codes
        self._points_of_sale = points_of_sale
        self._table: dict[str, bool] = {}

    @property
    def reader(self) -> DBKiloPreciosClarosReader:
        return self._reader

    @property
    def timestamps(self) -> dict[str, bool]:
        return self._timestamps

    @property
    def article_codes(self) -> dict[str, bool]:
        return self._article_codes

    @property
    def points_of_sale(self) -> dict[str, bool]:
        return self._points_of_sale

    @property
    def table(self) -> dict[str, bool]:
        return self._table

    def iterate(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.iterate start")
        for count, record in enumerate(self.reader.articles_per_point_of_sale_generator()):
            timestamp_string = record["sample_key"]
            article_code_string = record["article_code"]
            point_of_sale_key = record["point_of_sale_key"]
            test = all((
                self.timestamps.get(timestamp_string, False),
                self.article_codes.get(article_code_string, False),
                self.points_of_sale.get(point_of_sale_code_string, False)
                )
            )
            if test:
                yield record
            else:
                logging.error(f"*** Error {classname(self)}.iterate: unknown values at {count} record")
                for key, value in record.items():
                    logging.error(f"    {key}: {value}")
                logging.error(f"*** Error {classname(self)}.iterate")
        logging.info(f"{classname(self)}.iterate stop")

from typing import Generator, Any, Tuple
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
        self._first_sample = 0
        self._top_sample = -1

    @property
    def reader(self) -> KiloPreciosClarosReader:
        return self._reader

    @property
    def first_sample(self) -> int:
        return self._first_sample

    @first_sample.setter
    def first_sample(self, value: int) -> None:
        self._first_sample = value

    @property
    def top_sample(self) -> int:
        return self._top_sample

    @top_sample.setter
    def top_sample(self, value: int) -> None:
        self._top_sample = value

    @property
    def current_sample_home(self) -> Path | None:
        return self.reader.current_sample_home

    @property
    def current_sample_key(self) -> str | None:
        return self.reader.current_sample_key

    def samples_generator(
        self
    ) -> Generator[Tuple[Path, str], None, None]:
        for sample_home, sample_key in self.reader.read_sample(self.first_sample, self.top_sample):
            logging.info(f"{classname(self)}.samples_generator: sample_home: {sample_home} - sample_key: {sample_key}")
            yield sample_home, sample_key

    def points_of_sale_generator(
        self
    ) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.points_of_sale_generator: {self.reader.current_sample_home} - {self.sample_key}")
        for kilo_json in self.reader.read_points_of_sale():
            yield kilo_json

    def articles_per_point_of_sale_generator(
        self
    ) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.articles_per_point_of_sale_generator: {self.reader.current_sample_home} - {self.reader.current_sample_key}")
        for kilo_json in self.reader.read_articles_per_point_of_sale():
            yield kilo_json


def log_error_record(record: dict[str, str]) -> None:
   for key, value in record.items():
       logging.error(f"    {key}: {value}")


class DBRecordGenerator:
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader
    ) -> None:
        self._reader = reader

    @property
    def reader(self) -> DBKiloPreciosClarosReader:
        return self._reader

    def generate_record(self) -> Generator[dict[str, str], None, None]:
        yield from ()

    def iterate(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.iterate start")
        for sample_home, sample_key in self.reader.samples_generator():
            try:
                yield from self.generate_record()
            except Exception as message:
                logging.error(f"{classname(self)}.iterate: {sample_home} {sample_key} - {str(message)}")
        logging.info(f"{classname(self)}.iterate stop")


class DBRecordGeneratorWithTable(DBRecordGenerator):
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader
    ) -> None:
        super().__init__(reader)
        self._table: dict[str, dict[str, str]] = {}

    @property
    def table(self) -> dict[str, dict[str, str]]:
        return self._table

    def load_table(self) -> None:
        for record in self.iterate():
            pass


class DBStatesGenerator(DBRecordGeneratorWithTable):
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
        super().__init__(reader)

    def generate_record(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.generate_record: open {self.reader.current_sample_key}")
        for count, record in enumerate(self.reader.points_of_sale_generator()):
            state_code = record.get("state", None)
            if state_code:
                state_name = DBStatesGenerator.CODES_AND_STATES.get(state_code, "Error")
                existing_state = self.table.get(state_code, None)
                if existing_state:
                    continue
                else:
                    self.table[state_code] = state = {"code": state_code, "name": state_name}
                    yield state
            else:
                logging.error(f"*** Error {classname(self)}.generate_record at {count} record")
                log_error_record(record)
                message = f"*** Error {classname(self)}.generate_record: state_code is None"
                raise LoggedException(message)
        logging.info(f"{classname(self)}.generate_record: close {self.reader.current_sample_key}")


class DBCitiesGenerator(DBRecordGeneratorWithTable):
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader,
        known_states: dict[str, dict[str, str]]
    ) -> None:
        super().__init__(reader)
        self._know_states = known_states

    @property
    def known_states(self) -> dict[str, bool]:
        return self._know_states

    def generate_record(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.generate_record: open {self.reader.current_sample_key}")
        for count, record in enumerate(self.reader.points_of_sale_generator()):
            state_code = record.get("state", None)
            city_key = record.get("city_key", None)
            if state_code and city_key and self.known_states.get(state_code, False):
                existing_city = self.table.get(city_key, False)
                if existing_city:
                    continue
                else:
                    self.table[city_key] = True
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.generate_record at {count} record")
                log_error_record(record)
                logging.error(f"*** Error {classname(self)}.generate_record: check state_code and city_key")
        logging.info(f"{classname(self)}.generate_record: close {self.reader.current_sample_key}")


class DBPlacesGenerator(DBRecordGeneratorWithTable):
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader,
        known_cities: dict[str, bool]
    ) -> None:
        super().__init__(reader)
        self._known_cities: dict[str, bool] = known_cities

    @property
    def known_cities(self) -> dict[str, bool]:
        return self._known_cities

    def generate_record(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.generate_record: open {self.reader.current_sample_key}")
        for count, record in enumerate(self.reader.points_of_sale_generator()):
            city_key = record["city_key"]
            if city_key and self.known_cities.get(city_key, False):
                place_key = record["place_key"]
                existing_place = self.table.get(place_key, False)
                if existing_place:
                    continue
                else:
                    self.table[place_key] = True
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.generate_record at {count} record")
                log_error_record(record)
                logging.error(f"*** Error {classname(self)}.generate_record: check city_key")
        logging.info(f"{classname(self)}.generate_record: close {self.reader.current_sample_key}")


class DBPointsOfSalesGenerator(DBRecordGeneratorWithTable):
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader,
        known_places: dict[str, bool]
    ) -> None:
        super().__init__(reader)
        self._known_places: dict[str, bool] = known_places

    @property
    def known_places(self) -> dict[str, bool]:
        return self._known_places

    def generate_record(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.generate_record: open {self.reader.current_sample_key}")
        for record in self.reader.points_of_sale_generator():
            point_of_sale_key = record.get("point_of_sale_key", None)
            if point_of_sale_key:
                existing_point_of_sale = self.table.get(point_of_sale_key, False)
                if existing_point_of_sale:
                    continue
                else:
                    self.table[point_of_sale_key] = True
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.generate_record at {count} record")
                log_error_record(record)
                message = f"*** Error {classname(self)}.generate_record: check point_of_sale_key"
                raise LoggedException(message)
        logging.info(f"{classname(self)}.iterate: close {self.reader.current_sample_key}")


class DBArticleCodesGenerator(DBRecordGeneratorWithTable):
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader
    ) -> None:
        super().__init__(reader)

    def generate_record(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.generate_record: open {self.reader.current_sample_key}")
        for record in self.reader.articles_per_point_of_sale_generator():
            article_code_string = record.get("article_code", None)
            if article_code_string:
                existing_article_code = self.table.get(article_code_string, False)
                if existing_article_code:
                    continue
                else:
                    self.table[article_code_string] = True
                    yield record
            else:
                logging.error(f"*** Error {classname(self)}.generate_record at {count} record")
                log_error_record(record)
                message = f"*** Error {classname(self)}.generate_record: check article_code_string"
                raise LoggedException(message)
        logging.info(f"{classname(self)}.generate_record: close {self.reader.current_sample_key}")


class DBArticleCardsGenerator(DBRecordGeneratorWithTable):
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader,
        article_codes: dict[str, bool]
    ) -> None:
        super().__init__(reader)
        self._article_codes = article_codes

    @property
    def article_codes(self) -> dict[str, bool]:
        return self._article_codes

    def generate_record(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.generate_record: open {self.reader.current_sample_key}")
        for count, record in enumerate(self.reader.articles_per_point_of_sale_generator()):
            article_code_string = record.get("article_code", None)
            if article_code_string and self.article_codes.get(article_code_string, False):
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
                logging.error(f"*** Error {classname(self)}.generate_record at {count} record")
                log_error_record(record)
                message = f"*** Error {classname(self)}.generate_record: check article_code_string"
                raise LoggedException(message)
        logging.info(f"{classname(self)}.generate_record: close {self.reader.current_sample_key}")


class DBTimestampsGenerator(DBRecordGeneratorWithTable):
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader
    ) -> None:
        super().__init__(reader)

    def generate_record(self) -> Generator[dict[str, str], None, None]:
        sample_key = self.reader.current_sample_key
        existing_timestamp = self.table.get(sample_key, False)
        if existing_timestamp:
            yield from ()
        else:
            self.table[sample_key] = True
            yield from ({"sample_key": sample_key})



class DBPricesGenerator:
    def __init__(
        self,
        reader: DBKiloPreciosClarosReader,
        timestamps: dict[str, Any],
        article_codes: dict[str, Any],
        points_of_sale: dict[str, Any]
    ) -> None:
        self._reader = reader
        self._timestamps = timestamps
        self._article_codes = article_codes
        self._points_of_sale = points_of_sale

    @property
    def reader(self) -> DBKiloPreciosClarosReader:
        return self._reader

    @property
    def timestamps(self) -> dict[str, Any]:
        return self._timestamps

    @property
    def article_codes(self) -> dict[str, Any]:
        return self._article_codes

    @property
    def points_of_sale(self) -> dict[str, Any]:
        return self._points_of_sale

    def iterate(
        self
    ) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self)}.generate_record start")
        for count, record in enumerate(self.reader.articles_per_point_of_sale_generator()):
            amount = record.get("price", None)
            timestamp_string = record.get("sample_key", None)
            article_code_string = record.get("article_code", None)
            point_of_sale_code_string = record.get("point_of_sale_code", None)
            test = all((
                amount,
                timestamp_string,
                article_code_string,
                article_code_string,
                self.timestamps.get(timestamp_string, None),
                self.article_codes.get(article_code_string, None),
                self.points_of_sale.get(point_of_sale_code_string, None),
                timestamp_string == self.reader.current_sample_key
                )
            )
            if test:
                yield record
            else:
                logging.error(f"*** Error {classname(self)}.generate_record: unknown values at {count} record")
                logging.error(f"    current_sample_home: {self.reader.current_sample_home}")
                logging.error(f"    current_sample_key: {self.reader.current_sample_key}")
                for key, value in record.items():
                    logging.error(f"    {key}: {value}")
                logging.error(f"*** Error {classname(self)}.generate_record: check sample_key, article_code, point_of_sale_code")
        logging.info(f"{classname(self)}.generate_record stop")

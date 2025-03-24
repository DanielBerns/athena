from typing import Generator
from pathlib import Path


class DBKiloPreciosClarosReader:
    def __init__(self, kilo_precios_claros_reader: KiloPreciosClarosReader) -> None:
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
            metadata = self.reader.read_metadata()
            sample_key = metadata["sample_key"]
            for kilo_json in self.reader.read_articles_per_point_of_sale():
                kilo_json["sample_key"] = sample_key
                yield kilo_json


class DBCitiesGenerator:
    def __init__(self, reader: DBKiloPreciosClarosReader) -> None:
        self._reader = reader
        self._table: dict[str, dict[str, str]] = {}

    @property
    def reader(self) -> DBKiloPreciosClarosReader:
        return self._reader

    @property
    def table(self) -> dict[str, dict[str, str]]:
        self._table

    def generate_cities() -> Generator[dict[str, str], None, None]:
        for record in self.reader.points_of_sale_generator():
            stringy_city = get_stringy([record["state"], record["city"]])
            existing_city = self.table.get(stringy_city, False)
            if existing_city:
                continue
            else:
                self.table[stringy_city] = True
                yield record

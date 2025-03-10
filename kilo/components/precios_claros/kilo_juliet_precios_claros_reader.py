import logging
from typing import Generator
from pathlib import Path

from components.precios_claros.juliet_precios_claros_reader import JulietPreciosClarosReader
from components.precios_claros.kilo_precios_claros_io import KiloPreciosClarosIO
from components.helpers.helpers import as_jsonl

class KiloJulietPreciosClarosReader:
    def __init__(
        self,
        reader: JulietPreciosClarosReader
    ):
        self._reader = reader

    @property
    def reader(self) -> JulietPreciosClarosReader:
        return self._reader

    def read_sample_home(self) -> Generator[Path, None, None]:
        for juliet_sample_home in self.reader.read_sample_home():
            self.current_sample_home = juliet_sample_home
            yield juliet_sample_home

    def read_metadata(self) -> dict[str, str]:
        sample_key = self.current_sample_home.stem
        return {"sample_key": sample_key}

    def read_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.reader.read_points_of_sale():
            yield KiloPreciosClarosIO.get_point_of_sale_juliet_to_kilo(juliet_json)

    def read_selected_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.reader.read_selected_points_of_sale():
            yield KiloPreciosClarosIO.get_point_of_sale_juliet_to_kilo(juliet_json)

    def read_articles_per_point_of_sale(self) -> Generator[dict[str, str], None, None]:
        for juliet_json in self.reader.read_articles_per_point_of_sale():
            yield KiloPreciosClarosIO.get_article_per_point_of_sale_juliet_to_kilo(juliet_json)

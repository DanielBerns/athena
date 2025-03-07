import logging
from pathlib import Path
from components.juliet.juliet_paths import JulietPaths
from components.precios_claros.juliet_precios_claros_reader import JulietPreciosClarosReader
from components.precios_claros.juliet_precios_claros_target import JulietPreciosClarosTarget
from components.core.stats import Stats
from components.helpers import get_container


class JulietPreciosClarosProcessor:
    def __init__(
        self,
        juliet_paths: JulietPaths
    ) -> None:
        self._juliet_paths = juliet_paths

    @property
    def juliet_paths(self) -> JulietPaths:
        return self._juliet_paths

    @property
    def juliet_store_home(self) -> Path:
        container = get_container(self.juliet_paths.storage, "precios_claros")
        return get_container(container, "flatstore")

    def execute(
        self,
        reader: JulietPreciosClarosReader,
        target: JulietPreciosClarosTarget
    ) -> None:
        for juliet_sample_home in reader.read_sample_home():
            try:
                logging.info(f"{juliet_sample_home}")
                target.current_sample_home = juliet_sample_home
                target.juliet_points_of_sale(reader.read_points_of_sale)
                target.juliet_selected_points_of_sale(reader.read_selected_points_of_sale)
                target.juliet_articles_per_point_of_sale(reader.read_articles_per_point_of_sale)
            except Exception as message:
                logging.error(f"*** Error: {str(juliet_sample_home)} - {str(message):s}")

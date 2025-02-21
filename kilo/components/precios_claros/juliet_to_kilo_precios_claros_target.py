from pathlib import Path

from components.kilo.kilo_paths import KiloPaths


class JulietToKiloPreciosClarosTarget:
    def __init__(self, kilo_paths: KiloPaths) -> None:
        self._kilo_paths = kilo_paths

        # kilo_precios_claros = get_container(self.kilo_paths.storage, "precios_claros")
        # kilo_treestore = TreeStore(kilo_precios_claros, "treestore")
        # kilo_treestore.start()

    @property
    def kilo_paths(self) -> KiloPaths:
        return self._kilo_paths

    def juliet_sample_home(self, juliet_sample_home: Path) -> None:
        pass

    def juliet_point_of_sale_start(self) -> None:
        pass

    def juliet_point_of_sale(self, a_json_line: dict[str, str]) -> None:
        pass

    def juliet_point_of_sale_stop(self) -> None:
        pass

    def juliet_selected_point_of_sale_start(self) -> None:
        pass

    def juliet_selected_point_of_sale(self, a_json_line: dict[str, str]) -> None:
        pass

    def juliet_selected_point_of_sale_stop(self) -> None:
        pass

    def juliet_articles_per_point_of_sale_start(self) -> None:
        pass

    def juliet_articles_per_point_of_sale(self, a_json_line: dict[str, str]) -> None:
        pass

    def juliet_articles_per_point_of_sale_stop(self) -> None:
        pass

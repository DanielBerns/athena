from components.juliet.juliet_paths import JulietPaths
from components.juliet.juliet_io import juliet_precios_claros_update
from components.juliet.juliet_precios_claros_target import JulietPreciosClarosTarget
from components.kilo.kilo_paths import KiloPaths
from components.core.stats import Stats
from components.precios_claros.juliet_to_kilo_precios_claros_target import JulietToKiloPreciosClarosTarget

class JulietToKiloPreciosClaros:

    def __init__(self, juliet_paths: JulietPaths, kilo_paths: KiloPaths) -> None:
        self._juliet_paths = juliet_paths
        self._kilo_paths = kilo_paths

    @property
    def juliet_paths(self) -> JulietPaths:
        return self._juliet_paths

    @property
    def kilo_paths(self) -> KiloPaths:
        return self._kilo_paths

    def update_storage(self) -> None:
        target = JulietToKiloPreciosClarosTarget(self.kilo_paths)
        juliet_precios_claros_update(self.juliet_paths, target)
        Stats.write_stats("points_of_sale", target.points_of_sale_stats, self.kilo_paths.reports)
        Stats.write_stats("selected_points_of_sale", target.selected_points_of_sale_stats, self.kilo_paths.reports)
        Stats.write_stats("articles_per_point_of_sale", target.articles_per_point_of_sale_stats, self.kilo_paths.reports)
        print(f"Total counter             points_of_sale: {target.total_counter_points_of_sale:d}")
        print(f"Total counter    selected_points_of_sale: {target.total_counter_selected_points_of_sale:d}")
        print(f"Total counter articles_per_point_of_sale: {target.total_counter_articles_per_point_of_sale:d}")


def create_juliet_to_kilo_precios_claros(mode: str) -> JulietToKiloPreciosClaros:
    juliet_paths = JulietPaths(mode)
    kilo_paths = KiloPaths(mode)
    return JulietToKiloPreciosClaros(juliet_paths, kilo_paths)

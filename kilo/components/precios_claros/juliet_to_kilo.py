from components.juliet.juliet_paths import JulietPaths
from components.juliet.juliet_io import juliet_precios_claros_process
from components.juliet.juliet_precios_claros_target import JulietPreciosClarosTarget
from components.precios_claros.juliet_to_kilo_precios_claros_target import JulietToKiloPreciosClarosTarget

from components.kilo.kilo_paths import KiloPaths
from components.core.stats import Stats


def juliet_to_kilo_precios_claros_process_storage(juliet_paths: JulietPaths, kilo_paths: KiloPaths) -> None:
    target = JulietToKiloPreciosClarosTarget(kilo_paths)
    for juliet_sample_home in juliet_precios_claros_sample(juliet_paths):
        try:
            target.juliet_sample_home(juliet_sample_home)
            target.juliet_points_of_sale(juliet_precios_claros_points_of_sale)
            target.juliet_selected_point_of_sale(juliet_precios_claros_selected_points_of_sale)
            target.juliet_articles_per_point_of_sale(juliet_precios_claros_articles_per_point_of_sale)
        except Exception as message:
            print(f"*** Error: {str(message):s}")
    # Stats.write_stats("points_of_sale", target.points_of_sale_stats, self.kilo_paths.reports)
    # Stats.write_stats("selected_points_of_sale", target.selected_points_of_sale_stats, self.kilo_paths.reports)
    # Stats.write_stats("articles_per_point_of_sale", target.articles_per_point_of_sale_stats, self.kilo_paths.reports)
    # Stats.write_stats("dataset", target.dataset_stats, self.kilo_paths.reports)

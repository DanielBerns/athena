from typing import Generator
from components.core.flatstore import FlatStore
from components.helpers import get_json_lines, get_container
from components.juliet.juliet_paths import JulietPaths
from components.juliet.juliet_precios_claros_target import JulietPreciosClarosTarget


def juliet_precios_claros_update(juliet_paths: JulietPaths, target: JulietPreciosClarosTarget) -> None:
    precios_claros = get_container(juliet_paths.storage, "precios_claros")
    flatstore = FlatStore(precios_claros, "flatstore")

    for juliet_sample_home in flatstore.iterate():
        target.juliet_sample_home(juliet_sample_home)

        target.juliet_point_of_sale_start()
        for a_json_line in get_json_lines(juliet_sample_home, "points_of_sale", "messages"):
            target.juliet_point_of_sale(a_json_line)
        target.juliet_point_of_sale_stop()

        target.juliet_selected_point_of_sale_start()
        for a_json_line in get_json_lines(juliet_sample_home, "selected_points_of_sale", "messages"):
            target.juliet_selected_point_of_sale(a_json_line)
        target.juliet_selected_point_of_sale_stop()

        target.juliet_articles_per_point_of_sale_start()
        for a_json_line in get_json_lines(juliet_sample_home, "articles_per_point_of_sale", "messages"):
            target.juliet_articles_per_point_of_sale(a_json_line)
        target.juliet_articles_per_point_of_sale_stop()

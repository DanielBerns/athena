from typing import Generator
from components.core.flatstore import FlatStore
from components.helpers import get_json_lines, get_container

# I have a python function with this signature. I want to pass this function as argument of another function. How to type hint them?
def juliet_precios_claros_sample_home(precios_claros_flatstore: Path) -> Generator[Path, None, None]:
    # precios_claros = get_container(juliet_paths.storage, "precios_claros")
    # precios_claros_flatstore = get_container(precios_claros, "flatstore")
    flatstore = FlatStore(precios_claros_flatstore, "samples")
    for juliet_sample_home in flatstore.iterate():
        yield juliet_sample_home


def juliet_precios_claros_points_of_sale(juliet_sample_home: Path) -> Generator[dict[str, str], None, None]:
    for juliet_json in get_json_lines(juliet_sample_home, "points_of_sale", "messages"):
        yield juliet_json


def juliet_precios_claros_selected_points_of_sale(juliet_sample_home: Path) -> Generator[dict[str, str], None, None]:
    for juliet_json in get_json_lines(juliet_sample_home, "selected_points_of_sale", "messages"):
        yield juliet_json


def juliet_precios_claros_articles_per_points_of_sale(juliet_sample_home: Path) -> Generator[dict[str, str], None, None]:
    for juliet_json in get_json_lines(juliet_sample_home, "articles_per_point_of_sale", "messages"):
        yield juliet_json

#         try:
#             target.juliet_sample_home(juliet_sample_home)
#
#             target.juliet_point_of_sale_start()
#             for json_from_juliet in get_json_lines(juliet_sample_home, "points_of_sale", "messages"):
#                 target.juliet_point_of_sale(json_from_juliet)
#             target.juliet_point_of_sale_stop()
#
#             target.juliet_selected_point_of_sale_start()
#             for json_from_juliet in get_json_lines(juliet_sample_home, "selected_points_of_sale", "messages"):
#                 target.juliet_selected_point_of_sale(json_from_juliet)
#             target.juliet_selected_point_of_sale_stop()
#
#             target.juliet_articles_per_point_of_sale_start()
#             for json_from_juliet in get_json_lines(juliet_sample_home, "articles_per_point_of_sale", "messages"):
#                 target.juliet_articles_per_point_of_sale(json_from_juliet)
#             target.juliet_articles_per_point_of_sale_stop()
#         except Exception as message:
#             print(f"*** Error: {str(message):s}")
#

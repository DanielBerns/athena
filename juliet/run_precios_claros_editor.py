from typing import Dict, Tuple, Generator
from pathlib import Path
import time

from components.configuration import CLI
from components.core import create_application, show
from components.precios_claros import Editor


def get_arguments() -> Dict[str, str]:
    cli = CLI()
    cli.add_arguments(
        "-d",
        "--dotenv",
        type=str,
        default=".env",
        required=False,
        help="name of dotenv file",
    )
    cli.add_arguments(
        "-m",
        "--mode",
        choices=["dev", "test", "live"],
        type=str,
        default="live",
        required=False,
        help="how to run? dev, test or live",
    )
    return cli.arguments


def main() -> None:
    application_name: str = "run_precios_claros_editor"
    arguments = get_arguments()

    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1: start")
        Editor.execute(application)
        show(f"{application_name:s} 2: end")


if __name__ == "__main__":
    main()



#             articles_editor = Editor()
#             articles_editor.load_record_rules(reports_precios_claros, "articles", ".md")
#             modified_articles_collector = Collector()
#             for number, article in enumerate(Collector.read_table(reports_precios_claros, "articles", ".md")):
#                 articles_editor.edit(article['code'], article)
#                 modified_articles_collector.insert(article['code'], article)
#                 print(number, str(article))
#                 
#             points_of_sale_editor = Editor()
#             points_of_sale_editor.load_record_rules(reports_precios_claros, "points_of_sale", ".md")
#             modified_points_of_sale_collector = Collector()
#             for number, point_of_sale in enumerate(Collector.read_table(reports_precios_claros, "points_of_sale", ".md")):
#                 points_of_sale_editor.edit(point_of_sale['identifier'], point_of_sale)
#                 modified_points_of_sale_collector.insert(point_of_sale['identifier'], point_of_sale)
#                 print(number, str(point_of_sale))                
#         except Exception as panic:
#             show(f"{application_name:s} panic: {str(panic):s}")
#         modified_articles_collector.write_table(reports_precios_claros, "modified_articles", ".md")
#         modified_articles_collector.write_differences(reports_precios_claros, "modified_articles", ".md")
#         modified_points_of_sale_collector.write_table(reports_precios_claros, "modified_points_of_sale", ".md")
#         modified_points_of_sale_collector.write_differences(reports_precios_claros, "modified_points_of_sale", ".md")                    
























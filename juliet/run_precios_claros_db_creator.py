from typing import Dict, Tuple, Generator
from pathlib import Path
import time

from components.configuration import CLI
from components.core import create_application, show
from components.precios_claros import Analysis
from components.precios_claros_db import Actions 


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
    application_name: str = "run_precios_claros_db_creator"
    arguments = get_arguments()

    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1: begin")
        try:
            (   storage_precios_claros,
                results_precios_claros,
                reports_precios_claros,
            ) = Analysis.start(application)
            Actions.create_db(
                storage_precios_claros,
                reports_precios_claros
            )
        except Exception as panic:
            show(f"{application_name:s} panic: {str(panic):s}")
        show(f"{application_name:s} 2: end")


if __name__ == "__main__":
    main()



























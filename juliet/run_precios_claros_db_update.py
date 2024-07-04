from typing import Dict, Tuple, Generator
from pathlib import Path
import time

from components.configuration import CLI
from components.core import create_application, show
from components.precios_claros import PreciosClaros
from components.precios_claros_db import Updater 

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
    cli.add_arguments(
        "-s",
        "--sample",
        type=str,
        required=True,
        help="precios_claros sample identifier",
    )
    return cli.arguments

def main() -> None:
    application_name: str = "run_precios_claros_db_update"
    arguments = get_arguments()

    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1: begin")
        try:
            # alpha: Updater.execute(application, "20201028183600")
            
            Updater.execute(application, arguments["sample"])
        except Exception as panic:
            show(f"{application_name:s} panic: {str(panic):s}")
        show(f"{application_name:s} 2: end")


if __name__ == "__main__":
    main()



























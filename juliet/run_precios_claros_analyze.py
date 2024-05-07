from typing import Dict, Tuple, Generator
from pathlib import Path
import time

from components.configuration import CLI
from components.core import create_application, show
from components.precios_claros import Analysis

# import pdb

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


def clean_string(string: str) -> str:
    return string.strip()


def get_sample_keys(reports_list: Path) -> Generator[Tuple[str, str, str], None, None]:
    if reports_list.exists():
        with open(reports_list, "r") as source:
            for line in source:
                parts = line.split(",")
                yield clean_string(parts[0]), clean_string(parts[1]), clean_string(
                    parts[2]
                )


def main() -> None:
    application_name: str = "run_precios_claros_analysis"
    arguments = get_arguments()

    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1")
        try:
            Analysis.execute(application)
        except Exception as panic:
            show(f"{application_name:s} panic: {str(panic):s}")
        show(f"{application_name:s} 2: end")


if __name__ == "__main__":
    main()

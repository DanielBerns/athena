from typing import Dict, Tuple, Generator
from pathlib import Path
import time

from components.configuration import CLI
from components.core import create_application, show
from components.precios_claros import Actions


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
        "-r",
        "--reports_list",
        type=str,
        required=True,
        help="text file with a list of samples",
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

import pdb

def main() -> None:
    pdb.set_trace()
    application_name: str = "run_precios_claros_report_sample"
    arguments = get_arguments()

    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1")
        reports_list = Path(arguments["reports_list"]).expanduser()
        show(f"{application_name:s} 2: reports_list {str(reports_list):s}")
        try:
            for bravo_key, alpha_key, current_key in get_sample_keys(reports_list):
                show(
                    f"{application_name:s} Actions.report_delta start: {bravo_key:s} - {alpha_key:s} - {bravo_key:s}"
                )
                Actions.report_delta(application, bravo_key, alpha_key, current_key)
                show(
                    f"{application_name:s} Actions.report_delta stop: {bravo_key:s} - {alpha_key:s} - {bravo_key:s}"
                )
                # time.sleep(30)
        except Exception as panic:
            show(f"{application_name:s} panic: {str(panic):s}")
        show(f"{application_name:s} 3: end")


if __name__ == "__main__":
    main()

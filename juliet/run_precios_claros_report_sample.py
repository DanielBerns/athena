from typing import Dict
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
    
def main() -> None:
    application_name: str = "run_precios_claros_report_sample"
    arguments = get_arguments()

    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1")
        reports_list = Path(arguments["reports_list"]).expanduser()
        show(f"{application_name:s} 2: reports_list {str(reports_list):s}")
        if reports_list.exists():
            with open(reports_list, 'r') as source:
                for line in source:
                    parts = line.split(',')
                    try:
                        a_month_ago_key, a_week_ago_key, now_key = clean_string(parts[0]), clean_string(parts[1]), clean_string(parts[2])
                        Actions.report_delta(application, a_month_ago_key, a_week_ago_key, now_key)
                        time.sleep(10)
                    except Exception as panic:
                        show(f"{application_name:s} 3: {str(panic):s}")
                        show(f"{application_name:s} 3: {str(sample_key):s}")                        
        show(f"{application_name:s} 2")


if __name__ == "__main__":
    main()

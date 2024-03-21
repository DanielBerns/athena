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
        "-s",
        "--samplelist",
        type=str,
        required=True,
        help="text file with a list of sample_key",
    )
    return cli.arguments

def main() -> None:
    application_name: str = "run_precios_claros_report_sample"
    arguments = get_arguments()

    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1")
        samplelist = Path(arguments["samplelist"]).expanduser()
        show(f"{application_name:s} 2: samplelist {str(samplelist):s}")
        if samplelist.exists():
            with open(samplelist, 'r') as source:
                for sample_key in source:
                    try:
                        Actions.report_sample(application, sample_key[:-1])
                        time.sleep(10)
                    except Exception as panic:
                        show(f"{application_name:s} 3: {str(panic):s}")
                        show(f"{application_name:s} 3: {str(sample_key):s}")                        
        show(f"{application_name:s} 2")


if __name__ == "__main__":
    main()

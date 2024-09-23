from pathlib import Path
from typing import Dict

from components.automatization import update_crontab
from components.configuration import CLI
from components.core import create_application, show


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
    application_name: str = "run_automatization_update_crontab"
    arguments = get_arguments()

    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1")
        container = Path("~", "Commands").expanduser()
        commands_txt =  Path(container, "crontab").with_suffix('.txt')
        commands = {"grab_news": ("~/Commands/run_news_grab.sh", "20 * * * *"),
                    "download": ("~/Commands/run_precios_claros_download.sh", "30 18 * * 3")}
        update_crontab(commands_txt, commands)
        show(f"{application_name:s} 2")

if __name__ == "__main__":
    main()
 

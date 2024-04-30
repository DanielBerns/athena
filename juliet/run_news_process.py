from typing import Dict

from components.configuration import CLI
from components.core import create_application, show
from components.news import Actions, ADNSUR, RSS

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
    application_name: str = "run_news_process"
    arguments = get_arguments()

    processors = [
        ADNSUR(),
        RSS("clarin_lo_ultimo",        "info", ".xml"),
        RSS("clarin_politica",         "info", ".xml"),
        RSS("clarin_economia",         "info", ".xml"),
        RSS("clarin_internacional",    "info", ".xml"),
        RSS("ambito_ultimas_noticias", "info", ".xml"),
        RSS("ambito_economia",         "info", ".xml"),
        RSS("ambito_finanzas",         "info", ".xml"),
        RSS("ambito_politica",         "info", ".xml"),        
    ]
    
    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1")
        Actions.process(application, processors)
        show(f"{application_name:s} 2")

if __name__ == "__main__":
    main()

from typing import Dict

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
    return cli.arguments


def main() -> None:
    application_name: str = "run_precios_claros_download"
    arguments = get_arguments()

    selection_patterns = [
        {"provincia": "ar-z", "localidad": "caleta olivia"},
        {"provincia": "ar-z", "localidad": "rio gallegos"},
        {"provincia": "ar-u", "localidad": "comodoro rivadavia"},
        {"provincia": "ar-u", "localidad": "rada tilly"},
        {"provincia": "ar-u", "localidad": "trelew"},
        {"provincia": "ar-u", "localidad": "esquel"},
        {"provincia": "ar-u", "localidad": "puerto madryn"},
        {"provincia": "ar-u", "localidad": "rawson"},
        {"provincia": "ar-v", "localidad": "ushuaia"},
    ]

    def select(message: Dict[str, str]) -> bool:
        return any(
            all(message[key] == pattern[key] for key in pattern.keys())
            for pattern in selection_patterns
        )

    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1")
        sample = Actions.create_sample(application, select)
        show(f"{application_name:s} 2")


if __name__ == "__main__":
    main()

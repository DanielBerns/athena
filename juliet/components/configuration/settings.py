import os

from pathlib import Path
from typing import Dict, Tuple, Callable

# https://pypi.org/project/python-dotenv/
from dotenv import load_dotenv


from components.helpers import get_directory


class Constants:
    INFO: str = str(Path("~", "Info").expanduser())
    SOFTWARE: str = str(Path("~", "Apps").expanduser())
    PROJECT: str = "athena"
    VERSION: str = "juliet"


class Settings:
    @staticmethod
    def write_dotenv(resource: Path, parameters: Dict[str, str]) -> None:
        """Write an example dotenv file, with expected keys.
        User may modify the values, and add explanations.
        See https://pypi.org/project/python-dotenv/
        """
        with open(resource, "w") as target:
            target.write("# settings\n")
            for key, value in parameters.items():
                target.write(f"{key:s}={value:s}\n")

    @staticmethod
    def read_dotenv(
        home: Path,
        identifier: str,
        dotenv: str,
        default_dotenv_content: Callable[[], Dict[str, str]],
    ) -> None:
        """Load key value pairs from a text file
        and set some environment variables.
        If dotenv_resource doesnt exists,
           create it with default values from a callable
        """
        resource = Path(home, dotenv)
        if not resource.exists():
            Settings.write_dotenv(resource, default_dotenv_content())
        load_dotenv(resource)

    @staticmethod
    def build(identifier: str, mode: str, dotenv: str) -> Dict[str, str]:
        log_level_key: str = f"{identifier.upper():s}_LOG_LEVEL"
        get_default_dotenv_content = lambda: {log_level_key: "DEBUG"}

        info_home = get_directory(
            Path(Constants.INFO, Constants.PROJECT, Constants.VERSION, mode)
        )

        software_home = get_directory(
            Path(Constants.SOFTWARE, Constants.PROJECT, Constants.VERSION)
        )

        Settings.read_dotenv(info_home, identifier, dotenv, get_default_dotenv_content)

        log_level: str = os.environ.get(log_level_key) or "DEBUG"

        return {
            "mode": mode,
            "identifier": identifier,
            "info_home": str(info_home),
            "software_home": str(software_home),
            "log_level_key": log_level_key,
            log_level_key: log_level,
        }

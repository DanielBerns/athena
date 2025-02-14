# Complete docstrings and generate a test using the module unittest
from pathlib import Path
from components.core.helpers import get_directory, get_container


class JulietPaths:
    """
    Manages file and directory paths for the Juliet application.

    Args:
        application (str): The name of the application.
        mode (str, optional): The operating mode (e.g., 'live', 'test'). Defaults to 'live'.
    """

    def __init__(self, application: str, mode: str = "live") -> None:
        user_home = Path("~").expanduser()
        self._apps = get_directory(Path(user_home, "Apps", application, "juliet"))
        self._info = get_directory(Path(user_home, "Info", application, "juliet", mode))
        self._backup = get_container(self.info, "Backup")
        self._cli = get_container(self.info, "cli")
        self._commands = get_container(self.info, "Commands")
        self._logs = get_container(self.info, "Logs")
        self._reports = get_container(self.info, "Reports")
        self._results = get_container(self.info, "Results")
        self._secrets = get_container(self.info, "Secrets")
        self._storage = get_container(self.info, "Storage")

    @property
    def apps(self) -> Path:
        """The path to the application's main directory."""
        return self._apps

    @property
    def info(self) -> Path:
        """The path to the info processed by the app"""
        return self._info

    @property
    def backup(self) -> Path:
        return self._backup

    @property
    def cli(self) -> Path:
        return self._cli

    @property
    def commands(self) -> Path:
        return self._commands

    @property
    def logs(self) -> Path:
        return self._logs

    @property
    def reports(self) -> Path:
        return self._reports

    @property
    def results(self) -> Path:
        return self._results

    @property
    def secrets(self) -> Path:
        return self._secrets

    @property
    def storage(self) -> Path:
        return self._storage

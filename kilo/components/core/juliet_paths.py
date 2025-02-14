from pathlib import Path
from components.helpers.helpers import get_directory, get_container


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
        """The path to the backup directory."""
        return self._backup

    @property
    def cli(self) -> Path:
        """The path to the CLI directory."""
        return self._cli

    @property
    def commands(self) -> Path:
        """The path to the commands directory."""
        return self._commands

    @property
    def logs(self) -> Path:
        """The path to the logs directory."""
        return self._logs

    @property
    def reports(self) -> Path:
        """The path to the reports directory."""
        return self._reports

    @property
    def results(self) -> Path:
        """The path to the results directory."""
        return self._results

    @property
    def secrets(self) -> Path:
        """The path to the secrets directory."""
        return self._secrets

    @property
    def storage(self) -> Path:
        """The path to the storage directory."""
        return self._storage

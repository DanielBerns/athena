from pathlib import Path
from components.helpers.helpers import get_directory, get_container


class KiloPaths:
    """
    Manages file and directory paths for Juliet version.

    Args:
        mode (str, optional): The operating mode (e.g., 'live', 'test'). Defaults to 'live'.
    """

    def __init__(self, mode: str = "live") -> None:
        user_home = Path("~").expanduser()
        library = "athena"
        version = "kilo"
        self._apps = get_directory(Path(user_home, "Apps", libray, version))
        self._info = get_directory(Path(user_home, "Info", libray, version, mode))
        self._backup = get_container(self.info, "Backup")
        self._commands = get_container(self.info, "Commands")
        self._logs = get_container(self.info, "Logs")
        self._reports = get_container(self.info, "Reports")
        self._results = get_container(self.info, "Results")
        self._secrets = get_container(self.info, "Secrets")
        self._storage = get_container(self.info, "Storage")

    @property
    def apps(self) -> Path:
        """The path to the version's main directory."""
        return self._apps

    @property
    def info(self) -> Path:
        """The path to the info processed by this version apps"""
        return self._info

    @property
    def backup(self) -> Path:
        """The path to the backup directory.
           We must save and protect all the info in this directory.
        """
        return self._backup

    @property
    def cli(self) -> Path:
        """The path to the CLI directory.
           Files in this directory are inputs for command line applications
        """
        return self._cli

    @property
    def commands(self) -> Path:
        """The path to the commands directory.
           Perhaps this is same as cli.
        """
        return self._commands

    @property
    def logs(self) -> Path:
        """The path to the logs directory.
           There are dragons here. Please, no backup, and clean it periodically.
        """
        return self._logs

    @property
    def reports(self) -> Path:
        """The path to the reports directory.
           Applications generate reports here.
        """
        return self._reports

    @property
    def results(self) -> Path:
        """The path to the results directory.
           Applications store results from lengthy computations here.
           Backup
        """
        return self._results

    @property
    def secrets(self) -> Path:
        """The path to the secrets directory.
           No backup, no git
        """
        return self._secrets

    @property
    def storage(self) -> Path:
        """The path to the storage directory.
           Applications store their databases here
        """
        return self._storage

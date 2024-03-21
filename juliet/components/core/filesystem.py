from pathlib import Path
import sys
from typing import Optional, Dict

from components.helpers import (
    get_directory,
    remove_directory,
    get_container,
    get_resource,
    get_timestamp,
)

from components.core.metadata import Metadata
from components.core.catalog import Catalog


class FileSystem:
    def __init__(self, settings: Dict[str, str]) -> None:
        info_home = get_directory(Path(settings["info_home"]))
        software_home = get_directory(Path(settings["software_home"]))
        self._templates = get_container(software_home, "templates")
        self._commands = get_container(info_home, "Commands")
        self._storage = get_container(info_home, "Storage")
        self._secrets = get_container(info_home, "Secrets")
        self._results = get_container(info_home, "Results")
        self._reports = get_container(info_home, "Reports")
        self._logs = get_container(info_home, "Logs")
        self._metadata = Metadata(get_container(info_home, "metadata"))
        self._catalog: Catalog[Path] = Catalog()

        self._info_home: Path = info_home
        self._software_home: Path = software_home

    @property
    def info_home(self) -> Path:
        return self._info_home

    @property
    def software_home(self) -> Path:
        return self._software_home

    @property
    def templates(self) -> Path:
        return self._templates

    @property
    def commands(self) -> Path:
        return self._commands

    @property
    def storage(self) -> Path:
        return self._storage

    @property
    def secrets(self) -> Path:
        return self._secrets

    @property
    def results(self) -> Path:
        return self._results

    @property
    def reports(self) -> Path:
        return self._reports

    @property
    def logs(self) -> Path:
        return self._logs

    @property
    def metadata(self) -> Metadata:
        return self._metadata

    @property
    def catalog(self) -> Catalog[Path]:
        return self._catalog

    def start(self) -> None:
        self.metadata.start()

    def stop(self) -> None:
        self.metadata.stop()

    def clear(self) -> None:
        if self.info_home.exists():
            remove_directory(self.info_home)

import logging
from pathlib import Path
from typing import Generator, Tuple, Dict, Protocol
import json

from components.core.metadata import Metadata
from components.helpers import get_container, get_resource, classname


class Store:
    def __init__(self, container: Path, identifier: str) -> None:
        self._home = get_container(container, identifier)

    @property
    def home(self) -> Path:
        return self._home

    def start(self) -> None:
        logging.info(f"{classname(self):s}.start()")

    def stop(self) -> None:
        logging.info(f"{classname(self):s}.stop()")


HOME = Path("~").expanduser()


class SampleTask:
    def __init__(self, identifier: str):
        self._sample_home = HOME
        self._identifier = identifier

    @property
    def sample_home(self) -> Path:
        return self._sample_home

    @sample_home.setter
    def sample_home(self, value: Path) -> None:
        self._sample_home = value

    @property
    def identifier(self) -> str:
        return self._identifier

    def start(self) -> None:
        print(
            f"{classname(self):s}.start {self.identifier:s} - sample_home: {str(self.sample_home):s}"
        )

    def execute(self) -> None:
        print(
            f"{classname(self):s}.execute {self.identifier:s} - sample_home: {str(self.sample_home):s}"
        )

    def stop(self, target: Path) -> None:
        print(
            f"{classname(self):s}.stop {self.identifier:s} - sample_home: {str(self.sample_home):s}"
        )


class EmptySampleTask(SampleTask):
    def __init__(self):
        super().__init__("EmptySampleTask")


class SampleTaskPipeline:
    def __init__(self) -> None:
        self._tasks: Dict[str, SampleTask] = {}

    def add(self, task: SampleTask) -> None:
        self._tasks[task.identifier] = task

    def tasks(self) -> Generator[SampleTask, None, None]:
        for identifier, task in self._tasks.items():
            yield task

    def remove(self, identifier: str) -> None:
        try:
            del self._tasks[identifier]
        except KeyError:
            pass

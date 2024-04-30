import json
from pathlib import Path
from shutil import rmtree
import logging
from typing import Tuple, Dict, Generator

from components.core.store import Store
from components.core.application import register_error
from components.helpers import get_container, get_resource, classname


class TreeStoreError(Exception):
    def __init__(self, explanation: str) -> None:
        logging.error(explanation)
        super().__init__(explanation)


def base_256(number: int) -> Tuple[int, int, int]:
    assert 0 <= number < 16777216
    third_digit = number % 256
    number >>= 8
    second_digit = number % 256
    first_digit = number >> 8
    return first_digit, second_digit, third_digit


def base_10(first_digit: int, second_digit: int, third_digit: int) -> int:
    return (((first_digit << 8) + second_digit) << 8) + third_digit


def erase_directory(base: Path) -> None:
    rmtree(base, ignore_errors=True)


def _get_sample_home(samples: Path, number: int) -> Path:
    first_digit, second_digit, third_digit = base_256(number)
    sample_home = Path(
        samples, f"{first_digit:>03d}", f"{second_digit:>03d}", f"{third_digit:>03d}"
    )
    return sample_home


class Index:
    def __init__(self, resource: Path) -> None:
        self._resource: Path = resource
        if self.resource.exists():
            # restarting Index
            value = self.read()
            self._value = int(value["index"])
        else:
            # initialize Index
            self._value = 0
            self.write()

    @property
    def resource(self) -> Path:
        return self._resource

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, update: int) -> None:
        self._value = update
        self.write()

    def write(self) -> None:
        value = {"index": str(self.value)}
        with open(self.resource, "w") as target:
            json.dump(value, target)

    def read(self) -> Dict[str, str]:
        with open(self.resource, "r") as source:
            values = json.load(source)
        return values


class TreeStore(Store):
    def __init__(self, container: Path, identifier: str) -> None:
        """
        home: path where TreeStore lives
        identifier: the name of the TreeStore
        """
        super().__init__(container, identifier)
        self._samples = get_container(self.home, "samples")
        resource = get_resource(self.home, "index", ".json")
        self._index = Index(resource)

    @property
    def samples(self) -> Path:
        return self._samples

    @property
    def index(self) -> int:
        return self._index.value

    def update_index(self) -> None:
        self._index.value += 1

    def create_sample_home(self) -> Path:
        sample_home = _get_sample_home(self.samples, self.index)
        sample_home.mkdir(mode=0o700, parents=True, exist_ok=False)
        self.update_index()
        return sample_home

    def start(self):
        logging.info(f"treestore.start() with index {self.index:d}")

    def stop(self):
        logging.info(f"treestore.stop() with index {self.index:d}")

    def iterate(self, top: int = -1) -> Generator[Path, None, None]:
        if top == -1:
            top = self.index
        elif 0 <= top <= self.index:
            pass
        else:
            explanation = (
                f"{classname(self):s}.samples:"
                f"top {top:d} out of range (-1, {self.index:d})"
            )
            register_error(explanation)
            raise TreeStoreError(explanation)
        for k in range(top):
            yield _get_sample_home(self.samples, k)

    def get_sample_home(self, k: int) -> Path:
        return _get_sample_home(self.samples, k)

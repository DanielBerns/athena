from logging import error
import os
from pathlib import Path
from typing import Generator, Optional

from components.core.store import Store
from components.helpers import get_timestamp, get_container, classname


def _get_sample_home(samples: Path, identifier: str) -> Path:
    return get_container(samples, identifier)


class FlatStore(Store):
    def __init__(self, container: Path, identifier: str) -> None:
        super().__init__(container, identifier)
        self._samples = get_container(self.home, "samples")

    @property
    def samples(self) -> Path:
        return self._samples

    def iterate(self) -> Generator[Path, None, None]:
        for root, dirs, files in os.walk(self.samples):
            for dd in dirs:
                yield Path(self.samples, dd)

    def sample_home(self, key: str) -> Path:
        return get_container(self.samples, key)

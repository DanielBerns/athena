from logging import error
import glob
from pathlib import Path
from typing import Generator, Optional, List

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

    def sorted_sample_keys(self) -> List[str]:
        alpha = [dd for dd in glob.glob(f"{str(self.samples):s}/*")]
        bravo = sorted(alpha)
        charlie = [Path(dd).stem for dd in bravo]
        return charlie
    
    def iterate(self) -> Generator[Path, None, None]:
        for dd in glob.glob(f"{str(self.samples):s}/*"):
            yield Path(dd)

    def sample_home(self, key: str) -> Path:
        return get_container(self.samples, key)

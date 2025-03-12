from typing import Tuple, DefaultDict
from pathlib import Path
from collections import Counter, defaultdict

from components.helpers.helpers import get_resource, create_text_file



class DirtyEvents:
    def __init__(self, identifier: str):
        self._identifier: str = identifier
        self._counters: Counter[str] = Counter()
        self._table: DefaultDict[str, dict[str, str]] = defaultdict(dict)

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def counters(self) -> Counter[str]:
        return self._counters

    @property
    def table(self) -> DefaultDict[str, dict[str, str]]:
        return self._table

    def add(self, key: str, event: dict[str, str]) -> None:
        value = event[key]
        self.counters[value] += 1
        if self.counters[value] == 1:
            self.table[value] = event

    def write(self, container: Path) -> None:
        resource = get_resource(container, self.identifier, '.md')
        with create_text_file(resource) as target:
            target.write(f"# {self.identifier}\n")
            for key, event in self.table.items():
                target.write(f"## {key:s}: {self.counters[key]:d}\n")
                for kk, vv in event.items():
                    target.write(f"    {kk:s}: {vv:s}\n")
            target.write("\n")

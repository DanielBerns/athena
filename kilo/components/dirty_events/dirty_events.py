from typing import Tuple, DefaultDict
from pathlib import Path
from collections import Counter, defaultdict

from components.helpers.helpers import get_resource, create_text_file


def transform(key: str, event: dict[str, str]) -> Tuple[str, str]:
    key_value = event[key]
    dirty_event = "]-[".join(v for k, v in event.items() if k != key)
    return (key_value, f"[{dirty_event:s}]")


class DirtyEvents:
    def __init__(self, identifier: str):
        self._identifier: str = identifier
        self._table: DefaultDict[str, Counter[str]] = defaultdict(Counter)

    @property
    def identifier(self) -> dict[str, str]:
        return self._identifier

    @property
    def table(self) -> dict[str, str]:
        return self._table

    def add(self, key: str, event: dict[str, str]) -> None:
        (table_key, table_value) = transform(key, event)
        self.table[table_key][table_value] += 1

    def write(self, container: Path) -> None:
        resource = get_resource(container, self.identifier, '.md')
        with create_text_file(resource) as target:
            target.write(f"# {self.identifier}\n")
            for key, counter in self.table.items():
                target.write(f"## {key:s}\n")
                for number, (dirty_event, count) in enumerate(counter.items()):
                    target.write(f"{number:d}. ({count:>3d}) :: {dirty_event:s}\n")
            target.write("\n")




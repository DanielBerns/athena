from collections import Counter, defaultdict
import datetime
import json
from pathlib import Path
from typing import DefaultDict, Dict, Tuple, Generator

from components.helpers import write_json, get_directory, get_timestamp, get_resource


class Metadata:
    def __init__(self, directory: Path) -> None:
        self._directory: Path = get_directory(directory)
        self._store: Path = get_resource(self.directory, "store", ".json")
        self._records: DefaultDict[str, DefaultDict[str, Dict[str, str]]] = defaultdict(
            lambda: defaultdict(dict)
        )
        if self.store.exists():
            self.read_records()
        else:
            self.create_records()

    @property
    def directory(self) -> Path:
        return self._directory

    @property
    def store(self) -> Path:
        return self._store

    @property
    def records(self) -> DefaultDict[str, DefaultDict[str, Dict[str, str]]]:
        return self._records

    def create_records(self) -> None:
        self.add_item(".", "creation", {"timestamp": get_timestamp()})
        write_json(self.store, self.records)

    def read_records(self) -> None:
        with open(self.store, "r", encoding="utf-8") as source:
            for line in source:
                record = json.loads(line)
                self.add_item(
                    record["identifier"], record["attribute"], record["value"]
                )

    def write_records(self) -> None:
        with open(self.store, "w", encoding="utf-8") as target:
            for identifier, attribute, value in self.items():
                record = {
                    "identifier": identifier,
                    "attribute": attribute,
                    "value": value,
                }
                target.write(f"{json.dumps(record):s}\n")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        self.write_records()

    def items(self) -> Generator[Tuple[str, str, Dict], None, None]:
        for identifier, table in self.records.items():
            for attribute, value in table.items():
                yield identifier, attribute, value

    def add_item(self, identifier: str, attribute: str, value: Dict) -> None:
        self.records[identifier][attribute] = value

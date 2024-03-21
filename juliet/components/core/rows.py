from collections import defaultdict, Counter
import json
import os
from pathlib import Path
from typing import List, Dict, Protocol, DefaultDict, Any, Callable, Generator

from components.helpers import get_directory, get_resource

from components.core.messages import MessageDocument


class DictStatsError(Exception):
    pass


class DictStats:
    def __init__(self) -> None:
        self._counters: DefaultDict[Any, Counter] = defaultdict(Counter)

    @property
    def counters(self) -> DefaultDict[Any, Counter]:
        return self._counters

    def update(self, message: Dict[Any, Any]) -> None:
        for key, value in message.items():
            self.counters[key]["total"] += 1
            value_type = type(value).__name__
            self.counters[key][value_type] += 1

    def keys(self) -> List[str]:
        p = [count["total"] for key, count in self.counters.items()]
        test_p = all([v == p[0] for v in p])
        if not test_p:
            raise DictStatsError("EventStats.keys: bad stats messages (not p).")
        q = [len(count.keys()) == 2 for key, count in self.counters.items()]
        test_q = all(q)
        if not test_q:
            raise DictStatsError("EventStats.keys: bad stats messages (not q).")
        return [str(key) for key in self.counters.keys()]


class RowDocument:
    def __init__(self, directory: Path) -> None:
        self._directory: Path = get_directory(directory)
        self._resource: Path = get_resource(self.directory, "rows", ".csv")

    @property
    def directory(self) -> Path:
        return self._directory

    @property
    def resource(self) -> Path:
        return self._resource

    def start(self) -> None:
        """Placeholder for operations to perform before using self.rows()."""
        pass

    def rows(self) -> Generator[str, None, None]:
        with open(self.resource, "r", encoding="utf-8") as origin:
            for line in origin:
                yield line

    def stop(self) -> None:
        """Placeholder for operations to perform after using self.rows()."""
        pass

    def where(self, select: Callable[[str, int], bool]) -> Generator[str, None, None]:
        self.start()
        for number, row in enumerate(self.rows()):
            if select(row, number):
                yield row
        self.stop()

    def write(self, origin: MessageDocument) -> None:
        dict_stats = DictStats()
        for message in origin.messages():
            dict_stats.update(message)
        keys = dict_stats.keys()
        header = "|".join([str(k) for k in keys])
        with open(self.resource, "w", encoding="utf-8") as target:
            target.write(header + "\n")
            for message in origin.messages():
                row = "|".join(str(message[k]) for k in keys)
                target.write(row + "\n")

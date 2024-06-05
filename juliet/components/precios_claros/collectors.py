import logging

from typing import Dict, DefaultDict, List, Generator, Tuple
from collections import Counter, defaultdict
from pathlib import Path

from components.core import show, register_error
from components.helpers import classname
from components.precios_claros.record_editor_rules import RecordRule, FieldRule, ChangeFieldRule, NoChangeFieldRule


class CollectorsException(Exception):
    pass


def clean_dict(event: Dict[str, str]) -> Dict[str, str]:
    result = {pp.strip():qq.strip() for pp, qq in event.items()}
    return result


class CollectorField:
    def __init__(self, value: Dict[str, str]) -> None:
        self._counter: int = 0
        self._table: DefaultDict[str, List[Tuple[int, str]]] = defaultdict(list)
        self.add(value)
    
    @property
    def counter(self) -> int:
        return self._counter
    
    @counter.setter
    def counter(self, value: int) -> None:
        self._counter = value

    @property
    def table(self) -> DefaultDict[str, List[Tuple[int, str]]]:
        return self._table

    def add(self, value: Dict[str, str]) -> None:
        for key, value in value.items():
            self.table[key].append((self.counter, value))
        self.counter += 1


class Collector:
    def __init__(self) -> None:
        self._counter: Counter = Counter()
        self._table: Dict[str, CollectorField] = {}

    def insert(self, key: str, value: Dict[str, str]) -> None:
        self.counter[key] += 1
        collector_field = self.table.get(key, None)
        if collector_field is None:
            self.table[key] = CollectorField(value)
        else:
            collector_field.add(value)
            
    def write(self, container: Path, name: str, suffix: str) -> None:
        resource = Path(container, name).with_suffix(suffix)
        with open(resource, 'w') as target:
            target.write(f"# {name:s}\n")
            for major_index, (major_key, count) in enumerate(self.counter.items()):
                collector_field = self.table.get(major_key, None)
                if collector_field:
                    target.write(f"## {major_index:d} - {major_key:s} - {count:d}\n")
                    for minor_index, (minor_key, instances) in enumerate(collector_field.table.items()):
                        if len(instances) != count:
                            show(f"{classname(self):s}.write_table error {major_index:d} - {major_key:s} - {minor_index} - {minor_key:s} - {len(instances)} != {count:d}")
                        else:
                            unique_values = set([vv for cc, vv in instances])
                            check = ": X" if len(unique_values) > 1 else ": A"                            
                            target.write(f"### {minor_index} - {minor_key:s}\n")                            
                            for value_index, value in enumerate(unique_values):
                                target.write(f"{value_index:d}. {value:s}{check:s}\n")
                            target.write(f"\n")               
                else:
                    show(f"{classname(self):s}.write_table error {number:d} - {major_key:s}\n")

    @property
    def counter(self) -> Counter:
        return self._counter
   
    @property
    def table(self) -> Dict[str, CollectorField]:
        return self._table

    @staticmethod
    def read(
        container: Path, 
        name: str, 
        suffix: str
    ) -> Generator[Tuple[int, str, int, str, int, str, str, str], None, None]:
        resource = Path(container, name).with_suffix(suffix)
        with open(resource, 'r') as origin:
            title = origin.readline()
            state = 1
            for line in origin:
                print("state", state)
                try:
                    if state == 1:
                        prefix, info = line[:3], line[3:]
                        assert(prefix == "## ")
                        (_major_index, _major_key, _count) = info.split(" - ")
                        major_index = int(_major_index)
                        major_key = _major_key.strip()
                        count = int(_count)
                        yield major_index, major_key, -1, "", -1, "", "", "new_record"                                                                        
                        state = 2
                    elif state == 2:
                        prefix, info = line[:4], line[4:]
                        assert(prefix == "### ")
                        (_minor_index, _minor_key) = info.split(" - ")
                        minor_index = int(_minor_index.strip())
                        minor_key = _minor_key.strip()
                        yield major_index, major_key, minor_index, minor_key, -1, "", "", "new_field"                        
                        state = 3
                    elif state == 3:
                        if line == "\n":
                            yield major_index, major_key, minor_index, minor_key, -1, "", "", "end_of_field"                            
                            state = 4
                        else:
                            (_value_index, info) = line.split('.')
                            value_index = int(_value_index)
                            (_value, _check) = info.split(':')
                            value = _value.strip()
                            check = _check.strip()
                            yield major_index, major_key, minor_index, minor_key, value_index, value, check, "new_value"
                    elif state == 4:
                        if line.startswith("## "):
                            yield major_index, major_key, -1, "", -1, "", "", "end_of_record"
                            prefix, info = line[:3], line[3:]
                            assert(prefix == "## ")
                            (_major_index, _major_key, _count) = info.split(" - ")
                            major_index = int(_major_index.strip())
                            major_key = _major_key.strip()
                            count = int(_count.strip())
                            yield major_index, major_key, -1, "", -1, "", "", "new_record"                                                                                                   
                            state = 2                            
                        elif line.startswith("### "):
                            prefix, info = line[:4], line[4:]
                            assert(prefix == "### ")
                            (_minor_index, _minor_key) = info.split(" - ")
                            minor_index = int(_minor_index.strip())
                            minor_key = _minor_key.strip()
                            yield major_index, major_key, minor_index, minor_key, -1, "", "", "new_field"                        
                            state = 3
                        else:
                            raise CollectorsException(f"Collector.read_table error state 4")
                    else:
                        raise CollectorsException(f"Collector.read_table error wrong state")                        
                except Exception as panic:
                    pass
                    

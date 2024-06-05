from typing import Dict, List, Generator, Tuple, DefaultDict
from collections import Counter, defaultdict
from pathlib import Path

from components.core import show
from components.helpers import get_resource

def to_string(value: Dict[str, str]) -> str:
    return "][".join([f"{kk:s}:{vv:s}" for kk, vv in value])

def to_event(string: str) -> Dict[str, str]:
    return {kk: vv for (kk, vv) in (pp.split(":") for pp in string.split("]["))}

class Bucket:
    def __init__(self) -> None:
        self._table: DefaultDict[str, Counter] = defaultdict(Counter)
        
    def insert(self, key: str, event: Dict[str, str]) -> None:
        content: str = to_string(event)
        self._table[key][content] += 1
    
    def write(self, container: Path, name: str, suffix: str) -> None:
        resource = get_resource(container, name, suffix)
        with open(resource, "w") as target:
            target.write(f"# {title:s}\n")
            for major_number, (major_key, counter) in enumerate(self._table.items()):
                check = "X" if len(counter) > 1 else "A"
                target.write(f"## {major_number:d} - {major_key:s} - {check:s}\n")
                for string_number, (string_key, frequency) in enumerate(counter.items()):
                    event = to_event(string_key)
                    for minor_number, (minor_key, minor_value) in enumerate(event.items()):
                        target.write(f"{minor_number:d}. {minor_key:s}: {minor_value:s}\n")
                    target.write("\n")
       
    @staticmethod
    def read(container: Path, name: str, suffix: str) -> Generator[Tuple[str, Dict[str, str]], None, None]:
        resource: Path = get_resource(container, name, suffix)
        with open(resource, "r") as origin:
            line: str = origin.readline()
            assert(line.startswith("# "))
            title: str = line[3:]
            assert(len(title) > 0)
            state: int = 1
            event: Dict[str, str] = {}
            for number, line in enumerate(origin):
                try:
                    if state == 1:
                        prefix, info = line[:3], line[3:]
                        assert(prefix == "## ")
                        (_major_number, _major_key, _accept) = info.split(' - ')
                        major_number: int = int(_major_number.strip())
                        major_key: str = _major_key.strip()
                        accept: str = _accept.strip()
                        state = 2
                    elif state == 2:
                        if line == "\n":
                            yield major_key, event
                            event = {}
                            state = 1
                        else:
                            (_minor_number, info) = line.split(". ")
                            minor_number = int(_minor_number.strip())
                            (_minor_key, _value) = info.split(":")
                            minor_key: int = _minor_key.strip()
                            value: str = _value.strip()
                            event[minor_key] = value
                except Exception as panic:
                      remark = f"error at {number:d} - {line:s} - {str(panic):s}"
                      show(remark)
            
                          
                          

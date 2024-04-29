from typing import Dict, List, Generator
from pathlib import Path
from components.core import register_error
from components.helpers import classname

# import pdb


class FieldRule:
    def __init__(self, key: str) -> None:
        self._key: str = key
        
    @property
    def key(self) -> str:
        return self._key
    
    def execute(self, record: Dict[str, str]) -> None:
        try:
            actual_value = record[self.key]
            if self.match(actual_value):
                record[self.key] = self.new_value()
        except KeyError:
            explanation = f"{classname(self):s}.execute: bad key {self.key:s} - {str(record):s}"
            register_error(explanation)

    def match(self, value: str) -> bool:
        return False
    
    def new_value(self) -> str:
        return ""


class ABFieldRule(FieldRule):
    def __init__(self, key: str, a: str, b: str) -> None:
        super().__init__(key)
        self._a: str = a
        self._b: str = b
    
    @property
    def a(self) -> str:
        return self._a
    
    @property
    def b(self) -> str:
        return self._b
    
    def match(self, value: str) -> bool:
        return value == self.a  
    
    def new_value(self) -> str:
        return self.b

    
class RecordRule:
    def __init__(self, key: str) -> None:
        self._key: str = key
        self._field_rules: List[FieldRule] = []
        
    @property
    def key(self) -> str:
        return self._key
    
    @property
    def field_rules(self) -> List[FieldRule]:
        return self._field_rules

    def edit(self, record: Dict[str, str]) -> None:
        for rule in self.field_rules:
            rule.execute(record)


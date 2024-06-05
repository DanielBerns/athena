from typing import Dict, List, Generator, Protocol, Optional
from pathlib import Path
from components.core import register_error
from components.helpers import classname


class RecordEditorRuleException(Exception):
    pass


class FieldRule(Protocol):
    @property
    def key(self) -> str:
        ...

    @property
    def good_value(self) -> str:
        ...

    @property
    def match(self, value: str) -> bool:
        ...
    
    def execute(self, record: Dict[str, str]) -> bool:
        ...

    @property
    def is_ok(self) -> bool:
        ...
        

class ChangeFieldRule:
    def __init__(
        self, 
        key: str, 
        good_value: Optional[str] = None,
        wrong_values: Optional[List[str]] = None,
    ) -> None:
        self._key: str = key
        self._good_value: str = good_value if good_value else ""
        self._wrong_values: Dict[str, bool] = {value: True for value in wrong_values} if wrong_values else {}

    @property
    def key(self) -> str:
        return self._key

    @property
    def good_value(self) -> str:
        return self._good_value
    
    @property    
    def match(self, value: str) -> bool:
        return False if value == self.good_value else self._wrong_values.get(value, False)

    def execute(self, record: Dict[str, str]) -> bool:
        done = False
        try:
            actual_value = record[self.key]
            if self.match(actual_value):
                record[self.key] = self.good_value()
                done = True
        except KeyError:
            explanation = f"{classname(self):s}.execute: bad key {self.key:s} - {str(record):s}"
            register_error(explanation)
        return done
    @property
    def is_ok(self) -> bool:
        return self.good_value is not None 
        
        
        
class NoChangeFieldRule:
    def __init__(
        self, 
        key: str, 
        good_value: Optional[str] = None
    ) -> None:
        self._key: str = key
        self._good_value: str = good_value if good_value else ""

    @property
    def key(self) -> str:
        return self._key

    @property
    def good_value(self) -> str:
        return self._good_value
   
    @property   
    def match(self, value: str) -> bool:
        return value == self.good_value  
    
    def execute(self, record: Dict[str, str]) -> bool:
        done = False
        try:
            actual_value = record[self.key]
            if self.match(actual_value):
                pass
            else:
                raise RecordEditorRuleException(
                    f"{classname(self):s}.execute: unexpected value: {actual_value:s} != {self.good_value:s}"
                )
        except KeyError:
            explanation = f"{classname(self):s}.execute: bad key {self.key:s} - {str(record):s}"
            register_error(explanation)
        return done        

    @property
    def is_ok(self) -> bool:
        return self.good_value is not None 


class RecordRule:
    def __init__(self, key: str) -> None:
        self._key: str = key
        self._rules: List[FieldRule] = []
        
    @property
    def key(self) -> str:
        return self._key
    
    @property
    def rules(self) -> List[FieldRule]:
        return self._rules

    def edit(self, record: Dict[str, str]) -> bool:
        results = [rule.execute(record) for rule in self.rules]
        return all(results)
    
    @property            
    def is_ok(self) -> bool:
        return all(rule.is_ok for rule in self.rules)
    
    def get_record(self) -> Dict[str, str]:
        return {rule.key: rule.good_value for rule in self.rules if rule.is_ok}
            
            

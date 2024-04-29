from typing import Dict, List, Generator
from pathlib import Path
from components.core import register_error
from components.helpers import classname
from components.precios_claros.edit_rules import RecordRule
from components.precios_claros.collectors import Collector


class RecordEditor:
    def __init__(self) -> None:
        self._rules: Dict[str, RecordRule] = {}
        
    @property
    def rules(self) -> None:
        return self._rules
    
    def edit(self, key: str, record: Dict[str, str]) -> None:
        record_rule = self.rules.get(key, None)
        if record_rule:
           record_rule.edit(record)

    def load(self, container: Path, name: str, suffix: str) -> None:
        for record_rule in Collector.read_differences(container, name, suffix):
            self.rules[record_rule.key] = record_rule
            

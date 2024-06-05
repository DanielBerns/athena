from typing import Dict, List, Generator
from pathlib import Path
from components.core import register_error, show
from components.helpers import classname, get_resource
from components.precios_claros.record_editor_rules import RecordRule, FieldRule, ChangeFieldRule, NoChangeFieldRule
from components.precios_claros.collectors import Collector


class RecordEditor:
    def __init__(self) -> None:
        self._rules: Dict[str, RecordRule] = {}
        
    @property
    def rules(self) -> None:
        return self._rules
    
    def edit(self, key: str, record: Dict[str, str]) -> bool:
        record_rule = self.rules.get(key, None)
        return record_rule.edit(record) if record_rule else False

    def load_record_rules(self, container: Path, name: str, suffix: str) -> None:
        record_rule: Optional[RecordRule] = None
        good_value: Optional[str] = None
        wrong_values: Optional[List[str]] = None
        for major_index, major_key, minor_index, minor_key, value_index, value, check, state in Collector.read(container, name, suffix):
            remark = f"{major_index:d} {major_key:s} {minor_index:d} {minor_key:s} {value_index:d} {value:s} {check:s} {state:s}"
            show(remark)
            if state == "new_value":
                if check == "X":
                    wrong_values.append(value)
                elif check == "A":
                    good_value = value
                else:
                    pass
            elif state == "new_field":
                wrong_values = []
            elif state == "new_record":
                record_rule = RecordRule(major_key)
                self.rules[major_key] = record_rule
                wrong_values = None
                good_value = None
            elif state == "end_of_field":
                if len(wrong_values):
                    change_field = ChangeFieldRule(minor_key, good_value, wrong_values)
                    record_rule.rules.append(change_field)
                elif good_value:
                    no_change_field = NoChangeFieldRule(minor_key, good_value)
                    record_rule.rules.append(no_change_field)
                else:
                    pass
            elif state == "end_of_record":
                record_rule = None
                wrong_values = None
                good_value = None
            else:
                pass


    def write_clean_records(
         self, 
         container: Path, 
         name: str, 
         suffix: str,
         minor_keys: List[str]
    ) -> None:
         resource = get_resource(container, name, suffix)
         with open(resource, "w") as target:
             target.write(f"# {name:s}\n")
             major_keys = sorted([key for key in self.rules.keys()])
             for a_major_index, a_major_key in enumerate(major_keys):
                 record_rule = self.rules[a_major_key]
                 if record_rule.is_ok:
                     record = record_rule.get_record()
                     check = "A"
                     target.write(f"## {a_major_index:d} - {a_major_key:s} - {check:s}\n")
                     for a_minor_index, a_minor_key in enumerate(minor_keys):
                         value = record.get(a_minor_key, "error")
                         target.write(f"{a_minor_index:d}. {a_minor_key:s}:{value:s}\n")
                     target.write("\n")
                 else:
                     print(f"bad record: {major_key:s}")
                

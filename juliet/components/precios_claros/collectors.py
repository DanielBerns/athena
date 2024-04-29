import logging

from typing import Dict, DefaultDict, List, Generator
from collections import Counter, defaultdict
from pathlib import Path

from components.core import show, register_error
from components.precios_claros.edit_rules import RecordRule, ABFieldRule

class CollectorsException(Exception):
    pass

def clean_dict(event: Dict[str, str]) -> Dict[str, str]:
    result = {pp.strip():qq.strip() for pp, qq in event.items()}
    return result

class Collector:
    CUT_1 = 3        
    CUT_2 = 2

    def __init__(self) -> None:
        self._counter: Counter = Counter()
        self._table: Dict[str, Dict[str, str]] = {}
        self._differences: Counter = Counter()

    
    def insert(self, key: str, value: Dict[str, str]) -> None:
        self._counter[key] += 1
        if self._counter[key] == 1:
            self._table[key] = clean_dict(value)
        else:
            try:
                test = self._table[key]
                self.check(key, clean_dict(value), test)
            except Exception as message:
                explanation = f"Collector.insert error: key {key:s} -> {str(message):s}"
                show(explanation)

    def check(
        self, 
        key: str, 
        value: Dict[str, str], 
        test: Dict[str, str]
    ) -> None:
        auxiliar = [(test[pp] == qq, pp, test[pp], qq) for pp, qq in value.items()]
        result = all(aa for aa, bb, cc, dd in auxiliar)
        if not result:
            explanation = []
            explanation.append(f"## {key:s}\n")
            for aa, bb, cc, dd in auxiliar:
                if not aa:
                    explanation.append(f'"{key:s}" -: "{bb:s}" -: "{cc:s}" -: "{dd:s}" -: AB\n')
            difference = '= '.join(explanation) + '-'
            show(difference)
            self._differences[difference] += 1
            
    def write_table(self, container: Path, name: str, suffix: str) -> None:
        empty: Dict[str, str] = {}
        resource = Path(container, name).with_suffix(suffix)
        with open(resource, 'w') as target:
            target.write(f"# {name:s}\n")
            for number, (key, count) in enumerate(self._counter.items()):
                value = self._table.get(key, empty)
                target.write(f"## {number:d}: {key:s}\n")
                for pp, qq in value.items():
                    target.write(f"    {pp:s}: {qq:s}\n")
                target.write(f"--\n")                

    def write_differences(self, container: Path, name: str, suffix: str) -> None:    
        differences_name = name + "_differences"
        resource = Path(container, differences_name).with_suffix(suffix)
        with open(resource, 'w') as target:
            target.write(f"# {differences_name:s}\n")
            for kk, vv in self._differences.items():
                target.write(f"{kk:s} = {vv}\n")

    @staticmethod
    def read_table(container: Path, name: str, suffix: str) -> Generator[Dict[str, str], None, None]:
        resource = Path(container, name).with_suffix(suffix)        
        with open(resource, 'r') as origin:
            title = origin.readline()
            state = 1
            event: Dict[str, str]
            for number, line in enumerate(origin):
                try:
                    if state == 1:
                        tag, value = line[:Collector.CUT_1], line[Collector.CUT_1:-1]
                        assert(tag == "## ") 
                        event = {}
                        (identifier, article_code) = value.split(": ")
                        state = 2
                    elif state == 2:
                        if line[0] == '-':
                            state = 1
                            yield event
                        else:
                            try:
                                (kk, vv) = line.split(":")
                                key = kk.strip()
                                value = vv.strip()
                                event[key] = value
                            except Exception as panic:
                                register_error(str(panic))
                                register_error(f"{number:d} - {value:s}")
                    else:
                        raise CollectorsException("invalid state: {state:d} - {number:d} - {line:s}")
                except Exception as panic:
                    explanation = f"{classname(self):s}.read_table: {str(panic):s}"
                    register_error(explanation)
                    break

    @staticmethod
    def read_differences(container: Path, name: str, suffix: str) -> Generator[RecordRule, None, None]:
        differences_name = name + "_differences"        
        resource = Path(container, differences_name).with_suffix(suffix)        
        with open(resource, 'r') as origin:
            title = origin.readline()
            state = 1
            for number, line in enumerate(origin):
                try:
                    if state == 1:
                        tag, value = line[:Collector.CUT_1], line[Collector.CUT_1:-1]
                        assert(tag == "## ") 
                        code_1 = value
                        record_rule = RecordRule(code_1)
                        state = 2
                    elif state == 2:
                        if line[0] == '=':
                            tag, value = line[:Collector.CUT_2], line[Collector.CUT_2:-1]
                            try:
                                assert(tag == "= ")
                                (cc, kk, aa, bb, mm) = value.split(" -: ")
                                code_2 = cc[1:-1]    # scrap delimiters "
                                key = kk[1:-1]       # scrap delimiters "
                                value_a = aa[1:-1]   # scrap delimiters "
                                value_b = bb[1:-1]   # scrap delimiters "
                                method = mm
                                assert(code_1 == code_2)
                            except Exception as panic:
                                register_error(str(panic))
                                register_error(f"{number:d} - {value:s}")
                                continue
                            if method == "AB":
                                record_rule.field_rules.append(
                                    ABFieldRule(key, value_a, value_b)
                                )
                            elif method == "BA":
                                record_rule.field_rules.append(
                                    ABFieldRule(key, value_b, value_a)
                                )
                            elif method == "XX":
                                register_error(line)
                                continue
                        elif line[0] == '-':
                            state = 1
                            yield record_rule
                    else:
                        raise CollectorsException("invalid state: {state:d} - {number:d} - {line:s}")
                except Exception as panic:
                    explanation = f"{classname(self):s}.load_rules: {str(panic):s}"
                    register_error(explanation)
                    break

    

import logging
from typing import Dict


class TextLinesWithKeys:
    def __init__(self) -> None:
        self._lines_with_keys: Dict[str, str] = dict()

    @property
    def lines_with_keys(self) -> Dict[str, str]:
        return self._lines_with_keys

    def add(self, key: str, line: str) -> None:
        self.lines_with_keys[key] = line

    def remove(self, key: str) -> None:
        try:
            del self.lines_with_keys[key]
        except KeyError as message:
            logging.info(f"{str(message):s}")

    def content(self):
        return "\n".join(line for line in self.lines_with_keys.values())

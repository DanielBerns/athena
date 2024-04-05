import logging
from typing import Dict


class TextLinesWithKeys:
    def __init__(self) -> None:
        self._lines: Dict[str, str] = dict()

    @property
    def lines(self) -> Dict[str, str]:
        return self._lines

    def content(self):
        return "\n".join(line.strip() for line in self.lines.values())

    def add(self, key: str, line: str) -> None:
        self.lines[key] = line

    def remove(self, key: str) -> None:
        try:
            del self.lines[key]
        except KeyError as message:
            logging.info(f"{str(message):s}")


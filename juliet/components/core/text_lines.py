from typing import List, TextIO


class Text:
    def __init__(self) -> None:
        self._lines: List[str] = []

    @property
    def lines(self) -> List[str]:
        return self._lines

    def write(self, target: TextIO) -> None:
        for a_line in self.lines:
            target.write(f"{a_line.strip():s}\n")

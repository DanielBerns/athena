from typing import List


class TextLines:
    def __init__(self) -> None:
        self._lines: List[str] = []

    @property
    def lines(self) -> List[str]:
        return self._lines

    def content(self):
        return "\n".join(line.strip() for line in self.lines)
    

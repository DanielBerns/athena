from typing import Protocol


class Task(Protocol):
    def execute(self) -> None:
        ...

from typing import (List, Protocol)
from collections import Counter


UNK: str = "<|unk|>"
BOT: str = "<|bot|>"
EOT: str = "<|eot|>"
UNK_CODE: int = -1


class Scanner(Protocol):
    @property
    def separators(self) -> str:
        ...

    def words(self, text: str) -> Generator[str, None, None]:
        ...


class Tokenizer(Protocol):
    @property
    def str_to_int(self) -> dict[str, int]:
        ...

    @property
    def int_to_str(self) -> dict[int, str]:
        ...

    @property
    def histogram(self) -> Counter:
        ...

    def update(self, raw_text: str) -> None:
        ...

    def evaluate(self) -> None:
        ...

    def encode(self, raw_text: str) -> List[int]:
        ...

    def decode(self, coded_text: List[int]) -> str:
        ...



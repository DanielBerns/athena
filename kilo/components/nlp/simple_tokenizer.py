from typing import List, Tuple, dict, Optional, Generator, Protocol
from collections import Counter

from components.nlp import Scanner


UNK = "<|unk|>"
BOT = "<|bot|>"
EOT = "<|eot|>"
UNK_CODE = -1


class SimpleTokenizer:
    def __init__(self, scanner: Scanner) -> None:
        self._scanner = scanner
        self._str_to_int: dict[str, int] = {}
        self._int_to_str: dict[int, str] = {}
        self._histogram: Counter = Counter()
        self._number_of_sentences: int = 0

    @property
    def scanner(self) -> Scanner:
        return self._scanner

    @property
    def str_to_int(self) -> dict[str, int]:
        return self._str_to_int

    @property
    def int_to_str(self) -> dict[int, str]:
        return self._int_to_str

    @property
    def histogram(self) -> Counter:
        return self._histogram

    @property
    def number_of_sentences(self) -> int:
        return self._number_of_sentences

    @number_of_sentences.setter
    def number_of_sentences(self, value: int) -> None:
        self._number_of_sentences = value

    def update(self, raw_text: str) -> None:
        self.histogram.update(word for word in self.scanner.words(raw_text))
        self.number_of_sentences += 1

    def evaluate(self) -> None:
        all_words = sorted(self.histogram.keys())
        for code, token in enumerate(all_words):
            self.str_to_int[token] = code
            self.int_to_str[code] = token
        self.str_to_int[UNK] = UNK_CODE
        self.int_to_str[UNK_CODE] = UNK

    def encode(self, raw_text: str) -> List[int]:
        return [self.str_to_int.get(word, UNK_CODE) for word in self.scanner.words(raw_text)]

    def decode(self, coded_text: List[int]) -> str:
        return "".join([self.int_to_str[code] for code in coded_text])

    def useful_words(self) -> List[Tuple[int, str]]:
        def get_frequency_and_word() -> Generator[Tuple[int, int], None, None]:
            limit = self.number_of_sentences
            for word, frequency in self.histogram.items():
                if frequency < limit:
                    yield frequency, word
        return sorted((frequency, word) for frequency, word in get_frequency_and_word())

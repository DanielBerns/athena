from typing import List, Tuple, Dict, Optional, Generator, Protocol
from collections import Counter


SEPARATORS = (
    10,
    13,
    32,
    33,
    34,
    36,
    37,
    39,
    40,
    41,
    43,
    44,
    45,
    46,
    47,
    58,
    59,
    63,
    91,
    93,
    96,
    124,
    160,
    161,
    170,
    171,
    176,
    180,
    186,
    187,
    191,
    8203,
    8205,
    8211,
    8216,
    8217,
    8220,
    8221,
    8230,
    9729,
    9925,
    9928,
    10052,
    10060,
    10084,
    65039,
    127780,
    127781,
    127783,
    127784,
    127867,
    127891,
    127938,
    127968,
    128051,
    128105,
    128116,
    128161,
    128168,
    128218,
    128241,
    128250,
    128308,
    128309,
    128499,
    128514,
    128562,
    128563,
    128652,
    128663,
    128680,
    128760,
    128993,
    129398,
    129490,
)


class Parser(Protocol):
    @property
    def separators(self) -> str:
        ...

    def words(self, text: str) -> Generator[str, None, None]:
        ...

class Tokenizer(Protocol):
    @property
    def str_to_int(self) -> Dict[str, int]:
        ...
    
    @property
    def int_to_str(self) -> Dict[int, str]:
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

    
class SimpleParser:
    def __init__(self, separators: Optional[str] = None) -> None:
        if separators is None:
            separators = "".join([chr(v) for v in SEPARATORS])
        self._separators = separators

    @property
    def separators(self) -> str:
        return self._separators

    def words(self, text: str) -> Generator[str, None, None]:
        word_start = -1
        yield "<|bot|>"
        # iterate over each character in the text
        for cursor, character in enumerate(text):
            if character in self.separators:
                if -1 < word_start < cursor:
                    word = text[word_start:cursor]
                    yield word
                    word_start = -1
                yield character
            elif word_start == -1:
                word_start = cursor
            else:
                continue
        # add the last word (if any)
        if -1 < word_start < cursor:
            word = text[word_start:cursor+1]
            yield word
        yield "<|eot|>"


UNK = "<|unk|>"
BOT = "<|bot|>"
EOT = "<|eot|>"
UNK_CODE = -1


class SimpleTokenizer:
    def __init__(self, parser: Optional[Parser] = None) -> None:
        self._parser = parser if parser else SimpleParser()
        self._str_to_int: Dict[str, int] = {}
        self._int_to_str: Dict[int, str] = {}
        self._histogram: Counter = Counter()
        self._number_of_sentences: int = 0

    @property
    def parser(self) -> Parser:
        return self._parser

    @property
    def str_to_int(self) -> Dict[str, int]:
        return self._str_to_int
    
    @property
    def int_to_str(self) -> Dict[int, str]:
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
        self.histogram.update(word for word in self.parser.words(raw_text))
        self.number_of_sentences += 1

    def evaluate(self) -> None:        
        all_words = sorted(self.histogram.keys())
        for code, token in enumerate(all_words):
            self.str_to_int[token] = code
            self.int_to_str[code] = token
        self.str_to_int[UNK] = UNK_CODE
        self.int_to_str[UNK_CODE] = UNK

    def encode(self, raw_text: str) -> List[int]:
        return [self.str_to_int.get(word, UNK_CODE) for word in self.parser.words(raw_text)]
        
    def decode(self, coded_text: List[int]) -> str:
        return "".join([self.int_to_str[code] for code in coded_text])

    def useful_words(self) -> List[Tuple[int, str]]:
        def get_frequency_and_word() -> Generator[Tuple[int, int], None, None]:
            limit = self.number_of_sentences        
            for word, frequency in self.histogram.items():
                if frequency < limit:
                    yield frequency, word
        return sorted((frequency, word) for frequency, word in get_frequency_and_word())

        

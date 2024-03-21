from typing import List, Optional, Generator

SEPARATORS = (
    10,
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


class Tokenizer:
    def __init__(self, separators: Optional[str] = None) -> None:
        if separators is None:
            separators = "".join([chr(v) for v in SEPARATORS])
        self._separators = separators

    @property
    def separators(self) -> str:
        return self._separators

    def read(self, text: str) -> Generator[str, None, None]:
        word_start = -1
        # iterate over each character in the text
        for cursor, character in enumerate(text):
            if character.isspace():
                if -1 < word_start < cursor:
                    this_token = "".join(text[word_start:cursor])
                    yield this_token.strip()
                    word_start = -1
            elif character in self.separators:
                if -1 < word_start < cursor:
                    this_token = "".join(text[word_start:cursor])
                    yield this_token.strip()
                    word_start = -1
                yield character
            elif word_start == -1:
                word_start = cursor
            else:
                continue

        # add the last token (if any)
        if -1 < word_start < cursor:
            this_token = "".join(text[word_start:cursor])
            yield this_token.strip()


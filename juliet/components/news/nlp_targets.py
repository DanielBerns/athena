from typing import List, Tuple, Dict
from pathlib import Path
from components.news.models import News
from components.nlp.tries import Trie
from components.nlp.tokenizer import Tokenizer, SimpleTokenizer


class TrieTarget:
    def __init__(self, tokenizer: Tokenizer) -> None:
        self._tokenizer = tokenizer
        self._trie = Trie(tokenizer.int_to_str)

    @property
    def tokenizer(self) -> Tokenizer:
        return self._tokenizer

    @property
    def trie(self) -> Trie:
        return self._trie

    def start(self) -> None:
        pass
    
    def add(self, news: News) -> None:
        plain_text = news.plain_text
        coded_text = self.tokenizer.encode(plain_text)
        self.trie.insert(coded_text)
    
    def stop(self) -> None:
        pass
        
    def sentence(self, sequence: List[Tuple[int, int, int]]) -> str:
        coded_text = [index for children, count, index in sequence]
        return "".join(
            self.tokenizer.decode(coded_text)
        )

    def write(self, resource: Path) -> None:
        with open(resource, "w") as target:
            for a_sequence in self.trie.traverse():
                a_sentence = self.sentence(a_sequence)
                target.write(a_sentence + "\n")
    
    def show(self, resource: Path) -> None:
        self.trie.show(resource)

                     
class TokenizerTarget:
    def __init__(self) -> None:
        self._tokenizer = SimpleTokenizer()
  
    @property
    def tokenizer(self) -> Tokenizer:
        return self._tokenizer

    def start(self) -> None:
        pass
    
    def add(self, news: News) -> None:
        self.tokenizer.update(news.plain_text)
    
    def stop(self) -> None:
        self.tokenizer.evaluate()
    
    def get_trie_target(self) -> TrieTarget:
        return TrieTarget(self.tokenizer)

    def write(self, resource: Path) -> None:
        with open(resource, "w") as target:
            for key, value in self.tokenizer.histogram.items():
                target.write(f"{key:s} --> {value:d}\n")

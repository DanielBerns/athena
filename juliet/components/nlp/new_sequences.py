from components.nlp.new_tokenizer import Tokenizer
from typing import Dict, Tuple, Generator, List, TextIO, Callable, Optional
from pathlib import Path


class TrieNode:
    def __init__(self) -> None:
        self._children: Dict[int, "TrieNode"] = {}
        self._count: int = 0

    @property
    def children(self) -> Dict[int, "TrieNode"]:
        return self._children

    @property
    def count(self) -> int:
        return self._count

    @count.setter
    def count(self, value: int) -> None:
        self._count = value


class Trie:
    def __init__(self) -> None:
        self._root: TrieNode = TrieNode()

    @property
    def root(self) -> TrieNode:
        return self._root

    def insert(self, sequence: List[int]) -> None:
        node = self.root
        for index in sequence:
            node.count += 1
            try:
                node = node.children[index]
            except KeyError:
                node.children[index] = auxiliar = TrieNode()
                node = auxiliar

    def sequences(
        self, 
        node: TrieNode, 
        stack: List[Tuple[int, int, int]]
    ) -> Generator[List[Tuple[int, int, int]], None, None]:
        count = node.count        
        children = len(node.children)
        if children == 0 and count == 0:
            yield stack
        for index, child in node.children.items():
            stack.append((children, count, index))
            for next_level_stack in self.sequences(child, stack):
                yield next_level_stack
            stack.pop()

    def show(
        self, 
        node: TrieNode, 
        stack: List[Tuple[int, int, int]], 
        target: TextIO
    ) -> None:
        target.write("  " * len(stack))
        target.write(f"{len(stack):d} - ")
        children = len(node.children)
        count = node.count
        target.write(f"({children:d}-{count:d})\n\n")
        for number, (index, child) in enumerate(node.children.items()):
            stack.append((children, count, index))
            target.write(f"  " * len(stack))
            target.write(f"[{number+1:d} of {children:d}] {index:d}\n")
            self.show(child, stack, target)
            stack.pop()


class NLP:
    def __init__(
        self,
        tokenizer: Tokenizer,
        tokens_trie: Trie,
    ) -> None:
        self._tokenizer: Tokenizer = tokenizer
        self._tokens_trie: Trie = tokens_trie

    @property
    def tokenizer(self) -> Tokenizer:
        return self._tokenizer

    @property
    def tokens_trie(self) -> Trie:
        return self._tokens_trie

    def traverse(self) -> Generator[List[Tuple[int, int, int]], None, None]:
        for current in self.tokens_trie.sequences(self.tokens_trie.root, []):
            yield current

    def sentence(self, sequence: List[Tuple[int, int, int]]) -> str:
        return " ".join(
            self.tokenizer.decode([index for children, count, index in sequence])
        )



# def get_patterns(origin_name: Path, max_length: int = 2) -> Generator[str, None, None]:
#     get_text_lines = build_text_lines_generator(origin_name)
#     sorted_tokens, indexed_tokens = get_tokens(get_text_lines)
#     tokens_trie: Trie = Trie()
#     for tokens, indexes in get_tokens_and_indexes(origin_name, indexed_tokens):
#         tokens_trie.insert(indexes)
#     nlp = NLP(sorted_tokens, indexed_tokens, tokens_trie)
#     for value in nlp.shortened_sequences(max_length=max_length):
#         yield value

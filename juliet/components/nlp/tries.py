from components.nlp.tokenizer import Tokenizer
from typing import Dict, Tuple, Generator, List, TextIO, Callable, Optional
from pathlib import Path
from collections import Counter


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
    def __init__(
        self, 
        int_to_str: Dict[int, str]
    ) -> None:
        self._root: TrieNode = TrieNode()
        self._int_to_str: Dict[int, str] = int_to_str

    @property
    def root(self) -> TrieNode:
        return self._root

    @property
    def int_to_str(self) -> Dict[int, str]:
        return self._int_to_str

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

    def traverse(self) -> Generator[List[Tuple[int, int, int]], None, None]:
        for current in self.sequences(self.root, []):
            yield current

    def generate_show(
        self, 
        node: TrieNode, 
        stack: List[Tuple[int, int, int]]
    ) -> Generator[str, None, None]:
        yield "  " * len(stack)
        yield f"{len(stack):d} - "
        children = len(node.children)
        count = node.count
        yield f"({children:d}-{count:d})\n\n"
        for number, (index, child) in enumerate(node.children.items()):
            stack.append((children, count, index))
            yield f"  " * len(stack)
            yield f"[{number+1:d} of {children:d}] {self.int_to_str[index]:s}\n"
            yield from self.generate_show(child, stack)
            stack.pop()

    def show(self, resource: Path) -> None:
        with open(resource, "w") as target:
            for line in self.generate_show(self.root, []):
                target.write(line)

    def pattern_frequencies(self, length: int) -> List[Tuple[Tuple[int,...], int]]:
        frequencies = Counter()
        for sequence in self.traverse():
            for start, stop in zip(range(len(sequence) - length), range(length, len(sequence))):
                subsequence = sequence[start:stop]
                indexes = tuple([index for children, count, index in subsequence])
                frequencies[indexes] += 1
        return sorted(frequencies.items(), key=lambda item: item[1])

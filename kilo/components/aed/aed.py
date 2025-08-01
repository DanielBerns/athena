# AdaptivE Document === AED
# https://typing.python.org/en/latest/reference/generics.html

from typing import TypeVar, Generic


class Formatter(Protocol):
    def int_value(key: str, value: int) -> str:
        ...

    def bool_value(key: str, value: bool) -> str:
        ...

    def float_value(key: str, value: float) -> str:
        ...

    def string_value(key: str, value: str) -> str:
        ...

    def json_value(key: str, value: dict[str, Any]) -> str:
        ...

    def sentence_value(key: str, value: str) -> str:
        ...

    def paragraph_value(key: str, value: str) -> str:
        ...


Part = TypeVar('Part')


class Composite(Generic[Part])
    def __init__(self) -> None:
        self._parts: dict[str, Part] = {}

    @property
    def parts(self) -> dict[str, Part]:
        return self._parts

    def add(self, key: str, this_part: Part) -> None:
        test = not self.parts.get(key, False)
        if test:
            self.parts[key] = this_part
        else:
            message = f"{self.__class__.__name__}.add({key}, {repr(this_part)}) fails."
            raise MineException(message)

    def get(self, key: str) -> Part:
        a_part = self.parts.get(key, False)
        if a_part:
            return a_part
        else:
            message = f"{self.__class__.__name__}.get({key}) fails."
            raise MineException(message)


class Node:
    def __init__(self) -> None:
        self._key: str = ""
        self._on_error: str = "error"
        self._assigned: bool = False

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, value: str) -> None:
        self._key = value

    @property
    def on_error(self) -> str:
        return self._on_error

    @key.setter
    def on_error(self, value: str) -> None:
        self._on_error = value

    @property
    def assigned(self) -> bool:
        return self._assigned

    @assigned.setter
    def assigned(self, value: bool) -> None:
        self._assigned = value

    def emit(self, formatter: Formatter) -> str:
        raise NotImplementedError(f"{self.__class__.__name__}.emit({formatter.__class__.__name__})")


class IntNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self._value: int = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, this_value: int) -> None:
        self._value = this_value
        self.assigned = True

    def emit(self, formatter: Formatter) -> str:
        try:
            value_string = formatter.int_value(self.key, self.value)
            return value_string
        except Exception as an_exception:
            return self.on_error


class BoolNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self._value: bool = False

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, next_value: bool) -> None:
        self._value = next_value
        self.assigned = True

    def emit(self, formatter: Formatter) -> str:
        try:
            value_string = formatter.bool_value(self.key, self.value)
            return value_string
        except Exception as an_exception:
            return self.on_error


class FloatNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self._value: float = 0.0

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, next_value: float) -> None:
        self._value = next_value
        self.assigned = True

    def emit(self, formatter: Formatter) -> str:
        try:
            value_string = formatter.float_value(self.key, self.value)
            return value_string
        except Exception as an_exception:
            return self.on_error


class StringNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self._value: str = ""

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, next_value: str) -> None:
        self._value = next_value
        self.assigned = True

    def emit(self, formatter: Formatter) -> str:
        try:
            value_string = formatter.string_value(self.key, self.value)
            return value_string
        except Exception as an_exception:
            return self.on_error


class JsonNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self._value: dict[str, Any] | None = None

    @property
    def value(self) -> dict[str, Any]:
        return self._value if self._value else {}

    @value.setter
    def value(self, next_value: dict[str, Any]) -> None:
        self._value = next_value
        self.assigned = True

    def emit(self, formatter: Formatter) -> str:
        try:
            value_string = formatter.json_value(self.key, self.value)
            return value_string
        except Exception as an_exception:
            return self.on_error

class Sentence(Protocol):
    def __init__(self, key: str = "", separator: str = " ", empty_sentence: str = "") -> None:
        self._composite: Composite[Node] = Composite[Node]()
        self._key = key
        self._separator = separator
        self._empty_sentence = empty_sentence

    @property
    def composite(self) -> Composite[Node]:
        return self._composite

    @property
    def key(self) -> str:
        return self._key

    @property
    def separator(self) -> str:
        return self._separator

    @property
    def empty_sentence(self) -> str:
        return self._empty_sentence

    def items(self) -> Generator[Tuple[key, Node], None, None]:
        parts = self.composite.parts
        yield from parts.items()

    def emit(self, formatter: Formatter) -> str:
        value_strings = [value.emit(formatter) for key, value in self.items()]
        sentence_string = self.separator.join(value_strings) if value_strings else self.empty_sentence
        result = formatter.sentence_value(self.key, sentence_string)
        return result


class Paragraph:
    def __init__(self, key: str = "", separator: str = "\n", empty_paragraph: str = "") -> None:
        self._composite: Composite[Sentence] = Composite[Sentence]()
        self._key = key
        self._separator = separator
        self._empty_paragraph = empty_paragraph

    @property
    def composite(self) -> Composite[Sentence]:
        return self._composite

    def items(self) -> Generator[Tuple[key, Sentence], None, None]:
        parts = self.composite.parts
        yield from parts.items()

    def emit(self, formatter: Formatter) -> str:
        sentence_strings = [value.emit(formatter) for key, value in self.items()]
        paragraph_string = self.separator.join(sentence_strings) if sentence_strings else self.empty_paragraph
        result = formatter.paragraph_value(self.key, paragraph_string)
        return result


class NumberedList:
    def __init__(self) -> None:
        self._composite: Composite[Paragraph] = Composite[Paragraph]()

    @property
    def composite(self) -> Composite[Paragraph]:
        return self._composite

    def items(self) -> Generator[Tuple[key, Paragraph], None, None]:
        parts = self.composite.parts
        yield from parts.items()

    def emit(self, formatter: Formatter) -> str:
        paragraph_strings = [value.emit(formatter) for key, value in self.items()]
        paragraph_string = self.separator.join(sentence_strings) if sentence_strings else self.empty_sentence
        result = formatter.str_value(self.key, paragraph_string)
        return result


class Section:
    def __init__(self) -> None:
        self._title: Sentence | None = None
        self._nodes:

class Doc:
    def __init__(self) -> None:
        self._sections = Composite[Section]()


class Collection:
    def __init__(self) -> None:
        self._root: Path | None = None
        self._title: str | None = None
        self._docs = Composite[Doc]()

    @property
    def root(self) -> Path:
        return self._root

    @root.setter
    def root(self, value: Path) -> None:
        self._root = value

    @property
    def identifier(self) -> str:
        return self._identifier

    @title.setter
    def identifier(self, value: str) -> None:
        self._identifier = value

    @property
    def docs(self) -> dict[str, Doc]:
        return self._docs

    def add(self, key: str, this_doc: Doc) -> None:
        test = not self.docs.get(key, False)
        if test:
            self.docs[key] = this_doc
        else:




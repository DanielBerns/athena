import json
from pathlib import Path
from typing import Dict, Protocol, Any, Generator, List, DefaultDict, Callable

from components.helpers import get_directory, get_resource
from collections import Counter


class MessageGenerator(Protocol):
    """Abstract protocol for message generator."""

    def messages(self) -> Generator[Dict[str, str], None, None]:
        """A message is dictionary with str keys and str values."""
        ...

    def start(self) -> None:
        """Placeholder for operations to perform before using the generator."""
        ...

    def stop(self) -> None:
        """Placeholder for operations to perform after using the generator."""
        ...


class MessageDocument:
    """messages in a file"""

    def __init__(self, directory: Path) -> None:
        """Initializes the document with its directory and store file path."""
        self._directory: Path = get_directory(directory)
        self._resource: Path = get_resource(self.directory, "messages", ".jsonl")

    @property
    def directory(self) -> Path:
        """Returns the document"s directory path."""
        return self._directory

    @property
    def resource(self) -> Path:
        """Returns the path to the document"s store file."""
        return self._resource

    def start(self) -> None:
        """Placeholder for operations to perform before using self.messages()."""
        pass

    def messages(self) -> Generator[Dict[str, str], None, None]:
        """Yields messages from the store file."""
        with open(self.resource, "r", encoding="utf-8") as origin:
            for line in origin:
                message = json.loads(line)
                yield {str(k): str(v) for k, v in message.items()}

    def stop(self) -> None:
        """Placeholder for operations to perform after using self.messages()."""
        pass

    def where(
        self, select: Callable[[Dict[str, str]], bool]
    ) -> Generator[Dict[str, str], None, None]:
        self.start()
        for this_message in self.messages():
            if select(this_message):
                yield this_message
        self.stop()

    def update(self, origin: MessageGenerator) -> None:
        """Appends messages to the document file."""
        origin.start()
        with open(self.resource, "a", encoding="utf-8") as target:
            for message in origin.messages():
                line = json.dumps(message)
                target.write(f"{line}\n")
        origin.stop()

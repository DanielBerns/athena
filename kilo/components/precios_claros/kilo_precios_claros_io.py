import logging
from pathlib import Path
from collections.abc import Callable
from typing import Generator


from components.helpers import (
    get_container,
    get_resource,
    write_json,
    as_jsonl,
    read_json,
    read_json_lines,
    create_text_file
)


def get_price_in_cents(price: str) -> str:
    return str(int(float(price) * 100))


class KiloPreciosClarosException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


class KiloPreciosClarosIO:
    def __init__(self) -> None:
        self._home: Path | None = None

    @property
    def home(self) -> Path | None:
        return self._home

    @home.setter
    def home(self, value: Path) -> None:
        self._home = value

    @property
    def key(self) -> str | None:
        return self._key

    @key.setter
    def key(self, value: str) -> None:
        self._key = value

    @property
    def metadata_resource(self) -> Path:
        return get_resource(self.home, "metadata", ".json")

    def update_metadata(self, value: dict[str, str] | None = None) -> None:
        update = value if value else {"sample_key": self.key}
        sample_key = update.get("sample_key", None)
        if sample_key:
            write_json(self.metadata_resource, update)
        else:
            message = f"KiloSample.update_metadata: null sample_key\n" \
                      f"  at {str(self.home):s}"
            raise KiloPreciosClarosException(message)

    def create_metadata(self, sample_key: str) -> None:
        self.key = sample_key
        self.update_metadata({"sample_key": self.key})

    def read_metadata(self) -> dict[str, str] | None:
        return read_json(self.metadata_resource())

    def create_events_file(
        self,
        name: str,
        get_events: Callable[[], Generator[dict[str, str] | None, None, None]]
    ) -> None:
        resource = get_resource(self.home, name, ".jsonl")
        with create_text_file(resource) as target:
            for event in get_events():
                target.write(as_jsonl(event))

    def read_events_file(
        self,
        name: str
    ) -> Generator[dict[str, str], None, None]:
        resource = get_resource(self.home, name, ".jsonl")
        for event in read_json_lines(resource):
            yield event


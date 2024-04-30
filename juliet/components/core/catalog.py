from typing import Dict, Optional, TypeVar, Generic


class CatalogException(Exception):
    pass


T = TypeVar("T")


class Catalog(Generic[T]):
    def __init__(self) -> None:
        self._table: Dict[str, T] = {}  # Internal table for storing data

    @property
    def table(self) -> Dict[str, T]:
        """Copy the internal table, preventing modifications"""
        return self._table.copy()

    def create(self, key: str, value: T) -> None:
        """Creates a new entry in the catalog."""
        try:
            _ = self._table[key]
            raise CatalogException(f"Entry with key '{key:s}' already exists.")
        except KeyError:
            self._table[key] = value

    def update(self, key: str, value: T) -> None:
        """Updates an existing entry in the catalog."""
        try:
            _ = self._table[key]
            self._table[key] = value
        except KeyError:
            raise CatalogException(f"Entry with key '{key:s}' not found.")

    def delete(self, key: str) -> None:
        """Deletes an entry from the catalog."""
        if key not in self._table:
            raise CatalogException(f"Entry with key '{key:s}' not found.")
        del self._table[key]

    def get(self, key: str, on_key_error: Optional[T] = None) -> Optional[T]:
        """Retrieves an entry from the catalog."""
        try:
            value: T = self._table[key]
            return value
        except KeyError:
            return on_key_error

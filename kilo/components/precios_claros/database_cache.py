import logging

class DatabaseCacheException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


class DatabaseCache:
    def __init__(self, table: dict(str, int)) -> None:
        self._table: dict(str, int) = table

    @property
    def table(self) -> dict[str, int]:
        return self._table

    def add(self, key: str, row_id: int) -> None:
        if row_id < 0:
            raise DatabaseCacheException(
                f"DatabaseCache.add: key {key:s} row_id {row_id: d} must be greater than 0"
            )
        try:
            _ = self.table[key]
        except KeyError:
            self.table[key] = row_id
        else:
            raise DatabaseCacheException(
                "DatabaseCache.add: the key '{key}' already exists in the cache."
            )

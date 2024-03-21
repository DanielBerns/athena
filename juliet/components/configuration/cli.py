import argparse
from typing import List, Dict, Any


class CLI:
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser()

    @property
    def parser(self) -> argparse.ArgumentParser:
        return self._parser

    @property
    def arguments(self) -> Dict[str, str]:
        return vars(self.parser.parse_args())

    def add_arguments(self, *args, **kwargs):
        # Todo: add type hint
        self.parser.add_argument(*args, **kwargs)

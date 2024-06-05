from typing import Dict, List
from pathlib import Path

class Tool:
    def insert(self, key: str, value: Dict[str, str]) -> None:
        ...
        
    def write(self, container: Path, name: str, suffix: str) -> None:
        ...

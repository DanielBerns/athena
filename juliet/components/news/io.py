"""
Bot to scrape websites 
"""
from pathlib import Path
from typing import Dict, Tuple
import json

from bs4 import BeautifulSoup

from components.core import show
from components.helpers import get_timestamp, get_resource


class IO:
    @staticmethod
    def read(container: Path, name: str, suffix: str) -> Tuple[str, Dict[str, str]]:
        origin = get_resource(container, name, suffix)
        with open(origin, "r") as source:
            content = source.read()
        attributes_json = get_resource(container, "attributes", ".json")
        with open(attributes_json, "r") as source:
            attributes = json.load(source)
        return content, attributes

    @staticmethod
    def write(container: Path, name: str, suffix: str, content: str, attributes: Dict[str, str], ) -> None:
        target = get_resource(container, name, suffix)
        with open(target, "w") as target:
            target.write(content)
        attributes_json = get_resource(container, "attributes", ".json")
        with open(attributes_json, "w") as source:
            json.dump(attributes, source)


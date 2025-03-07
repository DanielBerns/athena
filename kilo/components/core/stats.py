from collections import defaultdict, Counter
from pathlib import Path
from typing import DefaultDict

from components.helpers.helpers import get_resource

class Stats:
    @staticmethod
    def create() -> DefaultDict[str, Counter[str]]:
        return defaultdict(Counter)

    @staticmethod
    def write(identifier: str, stats: DefaultDict[str, Counter[str]], target_home: Path) -> None:
        target = get_resource(target_home, identifier, ".md")
        with open(target, "w") as t:
            # Iterating through the defaultdict and counters
            t.write(f"# {identifier} stats\n\n")
            for category, counter in stats.items():
                t.write(f"## Category: {category}\n")
                for item, count in counter.items():
                    t.write(f"  Item: {item}, Count: {count}\n")
                t.write("\n")

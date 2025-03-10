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
            for code, counter in stats.items():
                t.write(f"## Code: {code}\n")
                for item, count in counter.items():
                    t.write(f"  Item: {item}, Count: {count}\n")
                t.write("\n")

    @staticmethod
    def find_bad_codes(
        identifier: str,
        stats: DefaultDict[str, Counter[str]],
        target_home: Path
    ) -> None:
        target = get_resource(target_home, identifier, ".md")
        bad_categories: dict[str, int] = {}
        with open(target, "w") as t:
            # Iterating through the defaultdict and counters
            t.write(f"# {identifier} stats\n\n")
            for code, counter in stats.items():
                t.write(f"## Code: {code}\n")
                repetitions = 0
                for item, count in counter.items():
                    t.write(f"  Item: {item}, Count: {count}\n")
                    repetitions += 1
                if repetitions > 1:
                    bad_categories[code] = repetitions
                t.write("\n")
            if bad_categories:
                t.write(f"# {identifier} bad codes\n\n")
                for key, value in bad_categories.items():
                    t.write(f"## Bad code: {key}\n")
                    counter = stats[key]
                    for item, count in counter.items():
                        t.write(f"  Item: {item}, Count: {count}\n")




from pathlib import Path

from bravo import Carrefour

def main() -> None:
    origin = Path('~', '.Info', 'webdeprecios').expanduser()
    timestamp = "20241230120000"
    extractor = ExtractorCarrefour(origin, timestamp)
    for number, event in extractor.execute():


if __name__ == "__main__":
    main()

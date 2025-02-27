import logging

from components.precios_claros import juliet_to_kilo_precios_claros_process_storage
from components.juliet import JulietPaths
from components.kilo import KiloPaths
from components.helpers import get_resource


def main() -> None:
    # script identifier,
    identifier = "translate_juliet_to_kilo_precios_claros"
    print(f"{__file__}", " - ", identifier)
    # log levels
    #     logging.NOTSET,
    #     logging.DEBUG,
    #     logging.INFO,
    #     logging.WARN,
    #     logging.ERROR,
    #     logging.CRITICAL,
    #
    log_level = logging.DEBUG
    mode = "live"

    juliet_paths = JulietPaths(mode)
    kilo_paths = KiloPaths(mode)

    # log_txt = str(get_resource_with_timestamp(kilo_paths.logs, identifier, ".txt"))
    log_txt = str(get_resource(kilo_paths.logs, identifier, ".txt"))


    logging.basicConfig(
        filename=log_txt,
        filemode="w",
        level=log_level,
        format="%(levelname)s > %(message)s",
    )
    logging.info("start")

    juliet_to_kilo_precios_claros_process_storage(juliet_paths, kilo_paths)

if __name__ == "__main__":
    main()

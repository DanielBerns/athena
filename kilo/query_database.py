import pdb
import logging
import os
from pathlib import Path
from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.kilo_precios_claros_basic_reader import KiloPreciosClarosBasicReader
from components.precios_claros.db_kilo_precios_claros_reader import (
    DBKiloPreciosClarosReader,
    DBStatesGenerator,
    DBCitiesGenerator
)

from components.precios_claros.db_new_interface import db_get_new_interface
from components.precios_claros.db_precios_claros_new_interface import DBPreciosClarosNewInterface
from components.helpers.helpers import get_container, get_resource, measure_execution_time


def get_reader(storage_precios_claros: Path) -> DBKiloPreciosClarosReader:
    _reader = KiloPreciosClarosBasicReader(storage_precios_claros)
    return DBKiloPreciosClarosReader(_reader)

def main() -> None:
    # script identifier,
    identifier = Path(__file__).stem
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

    kilo_paths = KiloPaths(mode)

    log_txt = str(get_resource(kilo_paths.logs, identifier, ".txt"))


    logging.basicConfig(
        filename=log_txt,
        filemode="w",
        level=log_level,
        format="%(levelname)s > %(message)s",
    )

    logging.info(f"{identifier} start")

    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    factory = lambda s: DBPreciosClarosNewInterface(s)
    with db_get_new_interface(storage_precios_claros, factory) as db:
        # db.get_all_the_states()
        # db.get_all_the_cities()
        # db.get_all_the_places()
        # db.get_all_the_points_of_sale()
        # db.get_all_the_article_codes()
        # db.get_all_the_article_cards()
        #
        # logging.info(f"## Puntos de venta\n")
        # for count, (a_key, pos) in enumerate(db.all_the_points_of_sale.items()):
        #     logging.info(
        #         f"{count}. {pos.flag} - {pos.business} en {pos.branch} - {pos.place.address} - {pos.place.city.name} - {pos.place.city.state.name}"
        #     )
        # logging.info("\n\n")


        # logging.info(f"## Artículos\n")
        # for count, article_code in enumerate(db.query_ordered_article_codes(50)):
        #     logging.info(f"{count:>6d}. - {article_code.code}")
        #     for index, card in enumerate(article_code.cards):
        #          logging.info(f"   {index:>3d}. {card.brand} | {card.description} | {card.package}")
        #     if count > 1000:
        #         break

        logging.info(f"## Artículos\n")
        known_article_codes: dict[str, bool] = {}
        tab = ' '*6
        for count, article_card in enumerate(db.query_ordered_article_cards(10)):
            article_code = article_card.article_code
            if known_article_codes.get(article_code.code, False):
                pass
            else:
                known_article_codes[article_code.code] = True
                logging.info(f"{count:>6d}. {article_code.code}")
                for index, card in enumerate(article_code.cards):
                     logging.info(f"{tab}{index:>3d}. {card.brand} - {card.description} - {card.package}")

    logging.info(f"{identifier} stop")

if __name__ == "__main__":
    main()


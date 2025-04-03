# import pdb

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

FIRST_SAMPLE = os.environ.get("FIRST_SAMPLE", "-1")
LAST_SAMPLE = os.environ.get("LAST_SAMPLE", "-1")

# import pdb

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

    # log_txt = str(get_resource_with_timestamp(kilo_paths.logs, identifier, ".txt"))
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
        # pdb.set_trace()
        db.get_all_the_states()
        states = DBStatesGenerator(get_reader(storage_precios_claros))
        for a_state in states.iterate():
            db_state = db.query_state(a_state["code"])
            if db_state:
                logging.info(f"{db_state.code} - {db_state.name}")
            else:
                logging.info(f"None db_state for {str(a_state)}")

        # pdb.set_trace()
        db.get_all_the_cities()
        for a_key, a_city in db.all_the_cities.items():
            logging.info(f"    {a_key} :: {a_city.name} at {a_city.state.name} - {a_city.state.code}")

        # pdb.set_trace()
        db.get_all_the_places()
        for a_key, a_place in db.all_the_places.items():
            logging.info(f"    {a_key} :: {a_place.address} {a_place.city.name} at {a_place.city.state.name} - {a_place.city.state.code}")

        # pdb.set_trace()
        db.get_all_the_points_of_sale()
        for a_key, pos in db.all_the_points_of_sale.items():
            logging.info(f"    {a_key} :: {pos.flag} {pos.business} at {pos.branch} - {pos.place.address} - {pos.place.city.name}")

        # pdb.set_trace()
        db.get_all_the_article_codes()
        for a_key, ac in db.all_the_article_codes.items():
            logging.info(f"    {a_key} :: {ac.code}")

        # pdb.set_trace()
        db.get_all_the_article_cards()
        for a_key, ac in db.all_the_article_cards.items():
            logging.info(f"    {a_key} :: {ac.article_code.code} [[{len(ac.article_code.cards)}]] {ac.brand}")


        # pdb.set_trace()
        count = 0
        logging.info("# ArticleCode")
        for key, article_code in db.all_the_article_codes.items():
            if len(article_code.cards) == 0:
                logging.error(f"*** Error: article_code: {article_code.code} with no card.")
                continue
            ac = article_code.cards[0]
            logging.info(f"## {article_code.code:s} - {ac.brand} - {ac.description}")

            article_code_prices = db.session.scalars(
                article_code.prices.select()
                # .limit(10)
            ).all()
            for a_price in article_code_prices:
                ts = a_price.timestamp
                pos = a_price.point_of_sale
                logging.info(
                    f"   {str(ts):s} - {pos.flag:s} - {pos.place.city.name} - {pos.place.address} - ${a_price.amount/100:>6.2f}"
                )
            count += 1
            if count > 100:
               break


    logging.info(f"{identifier} stop")

if __name__ == "__main__":
    main()


from collections import defaultdict
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
from components.precios_claros.database import db_get_session
from components.precios_claros.db_interface_basic_queries import (
    DBInterfaceBasicQueries,
    geometric_mean_times_100
)
from components.helpers.helpers import get_container, get_resource, measure_execution_time

FIRST_SAMPLE = os.environ.get("FIRST_SAMPLE", "-1")
LAST_SAMPLE = os.environ.get("LAST_SAMPLE", "-1")
DB_NAME = os.environ.get("DB_NAME", "mecon_dev")

import pdb

def get_reader(storage_precios_claros: Path) -> DBKiloPreciosClarosReader:
    _reader = KiloPreciosClarosBasicReader(storage_precios_claros)
    return DBKiloPreciosClarosReader(_reader)


def show_prices_by_article_code_city_and_timestamp(
    city_name: str, # city_name = "comodoro rivadavia"
    some_timestamp_strs: List[str] # some_timestamp_strs = ["20241023183002", "20241120183001", "20241218183003", "20250122183002", "20250220224436"]
) -> None:
        logging.info(f"## Prices at {city_name}")
        aggregation = defaultdict(lambda: defaultdict(lambda: (0,0,0)))

        for timestamp_str in some_timestamp_strs:
            for (article_code_str, min_price, max_price, geomean_price) in db.get_prices_by_article_code_city_and_timestamp(
               city_name,
               timestamp_str,
               aggregation_function=geometric_mean_times_100
            ):
                aggregation[article_code_str][timestamp_str] = \
                    (min_price, min_price, max_price) if min_price == max_price else (min_price, geomean_price, max_price)

        for article_code_str, samples in aggregation.items():
            card = db.all_the_article_codes[article_code_str].cards[0]
            logging.info(f"{article_code_str}: {card.brand} _ {card.description} _ {card.package}")

            table = [(ts, minp, geop, maxp) for ts, (minp, geop, maxp) in samples.items()]
            if len(table) == 0:
                continue
            for (ts, minp, geop, maxp) in table:
                logging.info(f"    {ts[:8]:>15s}: {minp/100:>12.2f} {geop/100:>12.2f} {maxp/100:>12.2f}")
            else:
                max_variation = 0
                for reference, measure in zip(table[:-1], table[1:]):
                    (reference_ts, reference_minp, reference_geop, reference_maxp) = reference
                    (measure_ts, measure_minp, measure_geop, measure_maxp) = measure
                    variation = (measure_geop - reference_geop) / measure_geop
                    if abs(variation) > abs(max_variation):
                        max_variation = variation
                    logging.info(f"  {reference_ts[:8]} -> {measure_ts[:8]} variation: {variation*100:>12.2f}")
                logging.info(f"                   max variation: {max_variation*100:>12.2f}")
                if len(table) > 2:
                    reference, measure = table[0], table[-1]
                    (reference_ts, reference_minp, reference_geop, reference_maxp) = reference
                    (measure_ts, measure_minp, measure_geop, measure_maxp) = measure
                    variation = (measure_geop - reference_geop) / measure_geop
                    logging.info(f"  {reference_ts[:8]} -> {measure_ts[:8]} variation: {variation*100:>12.2f}")
    logging.info(f"{identifier} stop")


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

    logging.info(f"FIRST_SAMPLE: {FIRST_SAMPLE}")
    logging.info(f"LAST_SAMPLE: {LAST_SAMPLE}")
    logging.info(f"DB_NAME: {DB_NAME}")
    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    db_uri = str(get_resource(storage_precios_claros_sqlite, DB_NAME, ".db"))
    with db_get_session(db_uri) as session:
        db = DBInterfaceBasicQueries(session)
        db.get_all_the_states()
        # states = DBStatesGenerator(get_reader(storage_precios_claros))
        # for a_state in states.iterate():
        #     db_state = db.query_state(a_state["code"])
        #     if db_state:
        #         logging.info(f"{db_state.code} - {db_state.name}")
        #     else:
        #         logging.info(f"None db_state for {str(a_state)}")
        #
        db.get_all_the_cities()
        # for a_key, a_city in db.all_the_cities.items():
        #     logging.info(f"    {a_key} :: {a_city.name} at {a_city.state.name} - {a_city.state.code}")
        #
        db.get_all_the_places()
        # for a_key, a_place in db.all_the_places.items():
        #     logging.info(
        #         f"    {a_key} :: {a_place.address} {a_place.city.name} at {a_place.city.state.name} - {a_place.city.state.code}"
        #     )
        #
        db.get_all_the_points_of_sale()
        # for a_key, pos in db.all_the_points_of_sale.items():
        #     logging.info(
        #         f"    {a_key} :: {pos.flag} {pos.business} at {pos.branch} - {pos.place.address} - {pos.place.city.name}"
        #     )
        #
        db.get_all_the_article_codes()
        # for a_key, ac in db.all_the_article_codes.items():
        #     logging.info(f"    {a_key} :: {ac.code}")
        #
        db.get_all_the_article_cards()
        # for a_key, ac in db.all_the_article_cards.items():
        #     logging.info(f"    {a_key} :: {ac.article_code.code} [[{len(ac.article_code.cards)}]] {ac.brand}")
        #
        db.get_all_the_timestamps()
        # for key, ts in db.all_the_timestamps.items():
        #     logging.info(f"    {key}:: {str(ts)}")
        city_name = "comodoro rivadavia"
        some_timestamp_strs = ["20241023183002", "20241120183001", "20241218183003", "20250122183002", "20250220224436"]
        show_prices_by_article_code_city_and_timestamp(city_name, some_timestamp_strs))

if __name__ == "__main__":
    main()


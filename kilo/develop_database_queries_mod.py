from typing import List, Generator, Tuple
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
from components.helpers.helpers import get_container, get_resource, create_text_file, read_text_lines, measure_execution_time

logger = logging.getLogger(__file__)

class DatabaseQueriesException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logger.error(message)

DB_NAME = os.environ.get("DB_NAME", "mecon_dev")


def get_reader(storage_precios_claros: Path) -> DBKiloPreciosClarosReader:
    _reader = KiloPreciosClarosBasicReader(storage_precios_claros)
    return DBKiloPreciosClarosReader(_reader)

CSV = '|'

months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

def ts_to_date(this_ts: str) -> str:
    yyyy = this_ts[:4]
    mm = months[int(this_ts[4:6]) - 1]
    dd = this_ts[6:8]
    return f"{yyyy}/{mm}/{dd}"

EMPTY = (" ", " ", " ")

class Modifier:
    def __init__(self, observed_values: dict[str, Tuple[int, int, int]]) -> None:
        self._last_valid_tuple: Tuple[int, int, int] | bool = False
        self._observed_values = observed_values

    @property
    def last_valid_tuple(self) -> Tuple[int, int, int] | bool:
        return self._last_valid_tuple

    @last_valid_tuple.setter
    def last_valid_tuple(self, value: Tuple[int, int, int] | bool) -> None:
        self._last_valid_tuple = value

    @property
    def observed_values(self) -> dict[str, Tuple[int, int, int]]:
        return self._observed_values

    def update(self, a_key: str) -> Tuple[int, int, int] | bool:
        current = self.observed_values.get(a_key, False)
        if current:
            self.last_valid_tuple = current
        else:
            current = self.last_valid_tuple if self.last_valid_tuple else False
        return current

    def run(self, keys: List[str]) -> dict[str, Tuple[int, int, int]]:
        return {this_key: self.update(this_key) for this_key in keys}


def get_prices_by_article_code_city_and_timestamp(
    db: DBInterfaceBasicQueries,
    city_name: str,
    some_timestamp_strs: List[str]
) -> Generator[str, None, None]:

    yield CSV.join([
        "Código",
        "Marca",
        "Descripción",
        "Fecha",
        "Precio $ Min",
        "Precio $ Geo",
        "Precio $ Max",
        "Var % Min",
        "Var % Geo",
        "Var Max %",
        "Total Var % Min",
        "Total Var % Geo",
        "Total Var % Max"
    ])

    aggregation = defaultdict(lambda: defaultdict(lambda: (0, 0, 0)))

    for timestamp_str in some_timestamp_strs:
        for (article_code_str, min_price, max_price, geomean_price) in db.get_prices_by_article_code_city_and_timestamp(
           city_name,
           timestamp_str,
           aggregation_function=geometric_mean_times_100
        ):
            aggregation[article_code_str][timestamp_str] = \
                (min_price, min_price, max_price) if min_price == max_price else (min_price, geomean_price, max_price)

    all_article_code_strs = [acs for acs in aggregation.keys()]
    for article_code_str in all_article_code_strs:
        observed_values = aggregation.get(article_code_str, False)
        if observed_values:
            card = db.all_the_article_codes[article_code_str].cards[0]
            prefix = CSV.join([f"[{article_code_str}]", card.brand, card.description])
            modifier = Modifier(observed_values)
            modified_values = modifier.run(some_timestamp_strs)
            first_measure = some_timestamp_strs[0]
            first_triple_measure = modified_values.get(first_measure, False)
            delta_string = CSV.join(f"{dd:>12s}" for dd in EMPTY)
            total_delta_string = CSV.join(f"{dd:>12s}" for dd in EMPTY)
            if first_triple_measure:
                measure_string = CSV.join(f"{mm/100:>12.2f}" for mm in first_triple_measure)
            else:
                measure_string = CSV.join(f"{mm:>12s}" for mm in EMPTY)
            yield CSV.join([prefix, ts_to_date(first_measure), measure_string, delta_string, total_delta_string])

            for base, measure in zip(some_timestamp_strs[:-1], some_timestamp_strs[1:]):
                triple_base = modified_values.get(base, False)
                triple_measure = modified_values.get(measure, False)
                if triple_base and triple_measure:
                    if not first_triple_measure:
                        first_measure = base
                        first_triple_measure = triple_base
                    triple_delta = ((y - x)/y for x, y in zip(triple_base, triple_measure))
                    delta_string = CSV.join(f"{dd:>12.2f}" for dd in triple_delta)
                    triple_total_delta = ((y - x)/y for x, y in zip(first_triple_measure, triple_measure))
                    total_delta_string = CSV.join(f"{dd:>12.2f}" for dd in triple_total_delta)
                    measure_string = CSV.join(f"{mm/100:>12.2f}" for mm in triple_measure)
                else:
                    if triple_base:
                        if first_triple_measure:
                            pass
                        else:
                            first_measure = base
                            first_triple_measure = triple_base
                    elif triple_measure:
                        if first_triple_measure:
                            pass
                        else:
                            first_measure = measure
                            first_triple_measure = triple_measure
                    else:
                        logger.info(f"{article_code_str} {base} {measure} {triple_base} {triple_measure}")

                    delta_string = CSV.join(f"{mm:>12s}" for mm in EMPTY)
                    if triple_measure:
                        if first_triple_measure:
                            triple_total_delta = ((y - x)/y for x, y in zip(first_triple_measure, triple_measure))
                            total_delta_string = CSV.join(f"{dd:>12.2f}" for dd in triple_total_delta)
                        else:
                            total_delta_string = CSV.join(f"{mm:>12s}" for mm in EMPTY)
                        measure_string = CSV.join(f"{mm/100:>12.2f}" for mm in triple_measure)
                    else:
                        total_delta_string = CSV.join(f"{mm:>12s}" for mm in EMPTY)
                        measure_string = CSV.join(f"{mm:>12s}" for mm in EMPTY)
                yield CSV.join([prefix, ts_to_date(measure), measure_string, delta_string, total_delta_string])


def main() -> None:
    # script identifier,
    identifier = Path(__file__).stem
    print(f"{__file__}", " - ", identifier)
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
    logging.info(f"DB_NAME: {DB_NAME}")
    logging.info("--------------------")
    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    reports_precios_claros = get_container(kilo_paths.reports, "precios_claros")

    parameters_container = get_container(storage_precios_claros, "parameters")
    some_article_codes_resource = get_resource(parameters_container, "some_article_codes", ".txt")
    some_article_codes: dict[str, bool] = {}
    if some_article_codes_resource.exists():
        for line in read_text_lines(some_article_codes_resource):
            this_article_code = line.strip()
            some_article_codes[this_article_code] = True
    some_cities_resource = get_resource(parameters_container, "some_cities", ".txt")
    some_cities: dict[str, bool] = {}
    if some_cities_resource.exists():
        for line in read_text_lines(some_cities_resource):
            this_city = line.strip()
            some_cities[this_city] = True
    some_timestamp_strs_resource = get_resource(parameters_container, "some_timestamp_strs", ".txt")
    some_timestamp_strs = []
    if some_timestamp_strs_resource.exists():
        for line in read_text_lines(some_timestamp_strs_resource):
            this_timestamp_str = line.strip()
            some_timestamp_strs.append(this_timestamp_str)
    separator = "="*150

    db_uri = str(get_resource(storage_precios_claros_sqlite, DB_NAME, ".db"))
    with db_get_session(db_uri) as session:
        db = DBInterfaceBasicQueries(session)
        db.get_all_the_states()
        db.get_all_the_cities()
        db.get_all_the_places()
        db.get_all_the_points_of_sale()
        db.get_all_the_article_codes()
        db.get_all_the_article_cards()
        db.get_all_the_timestamps()

        for city_name, city_value in some_cities.items():
            city_underscore = city_name.replace(' ', '_')
            report_file = get_resource(reports_precios_claros, f"prices_{city_underscore}", ".csv")
            with create_text_file(report_file) as text_file:
                for line in get_prices_by_article_code_city_and_timestamp(db, city_name, some_timestamp_strs):
                    text_file.write(line + "\n")

        report_file = get_resource(reports_precios_claros, "timestamps", ".txt")
        with create_text_file(report_file) as text_file:
            for key, _ in db.all_the_timestamps.items():
                text_file.write(key + "\n")

        report_file = get_resource(reports_precios_claros, "cities", ".txt")
        with create_text_file(report_file) as text_file:
            for key, _ in db.all_the_cities.items():
                text_file.write(key + "\n")

    logging.info(f"{identifier} stop")

if __name__ == "__main__":
    main()


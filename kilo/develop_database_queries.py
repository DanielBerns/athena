from typing import List, Generator
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

def get_prices_by_article_code_city_and_timestamp(
    db: DBInterfaceBasicQueries,
    city_name: str,
    some_timestamp_strs: List[str]
) -> Generator[str, None, None]:

    yield CSV.join(["Código","Marca","Descripción","Fecha","Precio Min","Precio Geo","Precio Max"])

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
        table = aggregation.get(article_code_str, False)
        if table:
            card = db.all_the_article_codes[article_code_str].cards[0]
            prefix = CSV.join([f"[{article_code_str}]", card.brand, card.description])
            for a_ts in some_timestamp_strs:
                triple = table.get(a_ts, False)
                date = ts_to_date(a_ts)
                if triple:
                    (minp, geop, maxp) = triple
                    body_fields = [f"{date:>15s}", f"{minp/100:>12.2f}", f"{geop/100:>12.2f}", f"{maxp/100:>12.2f}"]
                else:
                    body_fields = [f"{date:>15s}", " "*12, " "*12, " "*12]
                body = CSV.join(body_fields)
                yield f"{prefix}{CSV}{body}"



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


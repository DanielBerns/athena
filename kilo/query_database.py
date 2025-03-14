import logging
from pathlib import Path

from components.precios_claros.database import db_open_session
from components.precios_claros.database_queries import DBGet

from components.kilo.kilo_paths import KiloPaths
from components.helpers.helpers import get_container, get_resource


def database_make_some_queries(
    kilo_paths: KiloPaths
) -> None:
    storage = kilo_paths.storage
    results = kilo_paths.results
    precios_claros = "precios_claros"
    storage_precios_claros = get_container(storage, precios_claros)
    results_precios_claros = get_container(results, precios_claros)
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    db_uri = str(Path(storage_precios_claros_sqlite, "mecon_197").with_suffix(".db"))
    with db_open_session(db_uri) as session:
        get = DBGet(session)
        all_the_states = get.all_the_states()
        all_the_cities = get.all_the_cities()
        all_the_places = get.all_the_places()
        all_the_timestamps = get.all_the_timestamps()
        all_the_point_of_sale_codes = get.all_the_point_of_sale_codes()
        all_the_point_of_sale_representations = get.all_the_point_of_sale_representations()
        all_the_article_codes = get.all_the_article_codes()
        all_the_article_representations = get.all_the_article_representations()
        all_the_prices = get.all_the_prices()
        logging.info(f"all_the_states: {len(all_the_states)}")
        logging.info(f"all_the_cities: {len(all_the_cities)}")
        logging.info(f"all_the_places: {len(all_the_places)}")
        logging.info(f"all_the_timestamps: {len(all_the_timestamps)}")
        logging.info(f"all_the_point_of_sale_codes: {len(all_the_point_of_sale_codes)}")
        logging.info(f"all_the_point_of_sale_representations: {len(all_the_point_of_sale_representations)}")
        logging.info(f"all_the_article_codes: {len(all_the_article_codes)}")
        logging.info(f"all_the_article_representations: {len(all_the_article_representations)}")

        count = 0
        for key, ac in all_the_article_codes.items():
            ar = all_the_article_representations[ac.id]
            logging.info(f"# {key:s} {ar.brand:s} {ar.description:s} {ar.package:s}")
            for pp in ac.prices:
                logging.info(f"  precio: {pp.amount/100:>6.2f}")
            count += 1
            if count > 100:
                break

        count = 0
        for key, pp in all_the_prices.items():
            ac = all_the_article_codes[pp.article_code_id]
            ar = all_the_article_representations[ac.id]
            logging.info(f"# {key:s} {ac.code:s} {ar.brand} {ar.description:s} {ar.package:s}")
            logging.info(f"  precio: {pp.amount/100:>6.2f}")
            count += 1
            if count > 100:
                break

def main() -> None:
    # script identifier,
    identifier = "query_database"
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

    print("log_txt", log_txt)

    logging.basicConfig(
        filename=log_txt,
        filemode="w",
        level=log_level,
        format="%(levelname)s > %(message)s",
    )

    logging.info("start")
    database_make_some_queries(kilo_paths)


if __name__ == "__main__":
    main()


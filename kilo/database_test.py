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
    db_uri = str(Path(storage_precios_claros_sqlite, "mecon").with_suffix(".db"))
    with db_open_session(db_uri) as session:
        get = DBGet(session)
        all_the_states = get.all_the_states()
        all_the_cities = get.all_the_cities()
        all_the_places = get.all_the_places()
        all_the_timestamps = get.all_the_timestamps()
        all_the_points_of_sale = get.all_the_points_of_sale()
        all_the_article_codes = get.all_the_article_codes()
        all_the_article_cards = get.all_the_article_cards()
        all_the_prices = get.all_the_prices()
        logging.info(f"all_the_states: {len(all_the_states)}")
        logging.info(f"all_the_cities: {len(all_the_cities)}")
        logging.info(f"all_the_places: {len(all_the_places)}")
        logging.info(f"all_the_timestamps: {len(all_the_timestamps)}")
        logging.info(f"all_the_point_of_sale: {len(all_the_points_of_sale)}")
        logging.info(f"all_the_article_codes: {len(all_the_article_codes)}")
        logging.info(f"all_the_article_cards: {len(all_the_article_cards)}")
        logging.info(f"all_the_prices: {len(all_the_prices)}")

        logging.info("# Database tests")

        logging.info("## States and more")
        for key, st in all_the_states.items():
            logging.info(f"#1 {key:s} {st.code:s} {st.name:s}")
            for cc in st.cities:
                logging.info(f"#2  {cc.name:s}")
                for pp in cc.places:
                    logging.info(f"#3    {pp.address:s}")
                    for pos in pp.points_of_sale:
                        logging.info(f"#4      {pos.flag:s} - {pos.business:s} - {pos.branch:s}")

        logging.info("## Points of sale")
        for key, pos in all_the_points_of_sale.items():
            logging.info(f"#2   {key:s} {pos.code} - {pos.flag} - {pos.business:s} - {pos.branch}")
            logging.info(f"#3     {pos.place.address:s} {pos.place.city.name:s}")

        count = 0
        logging.info(f"# ArticleCode ({len(all_the_article_codes)})")
        for key, article_code in all_the_article_codes.items():
            logging.info(f"## article code: {article_code.code}")
            logging.info(f"### cards")
            for cc in article_code.cards:
                logging.info(f"      ({cc.brand}) - ({cc.description}) ({cc.package})")
            logging.info(f"### prices")
            for pp in article_code.prices[:5]:
                logging.info(f"      ({pp.timestamp}) - (${pp.amount/100:>6.2f}) ")
            count += 1
            if count > 5000:
                break

        logging.info("# Timestamps")
        for key, ts in all_the_timestamps.items():
            logging.info(f"## {ts}")
            for a_price in ts.prices[:100]:
                pos = a_price.point_of_sale
                article_code = a_price.article_code
                article_card = article_code.cards[0]
                logging.info(f"   {pos.flag:s} - {article_code.code} - {article_card.brand} - {article_card.description} - ${a_price.amount/100:>6.2f}")

        count = 0
        logging.info("# Price")
        for key, price in all_the_prices.items():
            ac = price.article_code
            ar = ac.cards[0]
            logging.info(f"# {key} {ac.code:s} {ar.brand} {ar.description:s} {ar.package:s}")
            ts = price.timestamp
            logging.info(f"   timestamp: {str(ts):s} - ${price.amount/100:>6.2f}")
            pos = price.point_of_sale
            logging.info(f"   points_of_sale: {pos.flag:s} - {pos.business:s} - {pos.branch:s} - {pos.place.address:s}")
            count += 1
            if count > 100:
               break

        count = 0
        logging.info("# ArticleCode")
        for key, article_code in all_the_article_codes.items():
            ac = article_code.cards[0]
            logging.info(f"## {article_code.code:s} - {ac.brand} - {ac.description}")
            for a_price in article_code.prices[:10]:
                ts = a_price.timestamp
                pos = a_price.point_of_sale
                logging.info(f"   timestamp: {str(ts):s} - {pos.flag:s} - ${a_price.amount/100:>6.2f}")
            count += 1
            if count > 100:
               break

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


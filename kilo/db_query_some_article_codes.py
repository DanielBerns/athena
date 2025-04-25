import logging
import os
from pathlib import Path
from typing import Optional, Any

from sqlalchemy.orm import Session

from components.kilo.kilo_paths import KiloPaths

from components.precios_claros.database import db_get_session
from components.precios_claros.db_interface_basic_queries import (
    DBInterfaceBasicQueries,
    geometric_mean_times_100
)
from components.helpers.helpers import get_container, get_resource, measure_execution_time



DB_NAME = os.environ.get("DB_NAME", "mecon_dev")

if __name__ == "__main__":
    # script identifier,
    identifier = Path(__file__).stem
    print(f"{__file__}", " - ", identifier)
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

    # Example Usage (replace with your actual database URI and data)
    logging.info(f"DB_NAME: {DB_NAME}")
    storage_precios_claros = get_container(kilo_paths.storage, "precios_claros")
    storage_precios_claros_sqlite = get_container(storage_precios_claros, "sqlite")
    db_uri = str(get_resource(storage_precios_claros_sqlite, DB_NAME, ".db"))

    with db_get_session(db_uri) as session:
        db = DBInterfaceBasicQueries(session)

        article_code_list = ["7790070415370", "7790070416247", "7790070416865", "7790070416872", "7790070416889"]
        city_string = "comodoro rivadavia"
        timestamp_string = "20250220224436"

        logging.info(f"Price Summary: {city_string} - {timestamp_string}")

        for article_code_string in article_code_list:
            for (minp, maxp, geop) in db.get_price_summary(
                article_code_string,
                city_string,
                timestamp_string,
                geometric_mean_times_100
            ):
                if minp and maxp and geop:
                    logging.info(f"{article_code_string:>30s} {minp/100:>12.2f} - {maxp/100:>12.2f} - {geop/100:>12.2f}")

    logging.info(f"{identifier} stop")


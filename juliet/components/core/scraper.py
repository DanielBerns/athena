import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator

from requests import Session

from components.helpers import classname, get_timestamp


class Scraper:
    def __init__(self) -> None:
        self._session: Session = Session()

    def start(self) -> None:
        remark = f"{classname(self):s}.start()"
        print(remark)
        logging.info(remark)

    def stop(self) -> None:
        # https://stackoverflow.com/questions/49253246/how-to-close-requests-session
        self._session.close()
        remark = f"{classname(self):s}.stop()"
        print(remark)
        logging.info(remark)

    def get(self, url: str) -> Dict[Any, Any]:
        remark = f"{classname(self):s}.get({url:s}) 1"
        print(remark)
        logging.info(remark)
        try:
            response = self._session.get(url, headers={"User-Agent": "Mozilla/5.0"})
            content, http_code = response.text, response.status_code 
            attributes = {
                "timestamp": get_timestamp(),
                "original url": url,
                "response.url": response.url,
                "http_code": str(http_code),
            }
        except Exception as message:
            content, http_code = "", -1
            attributes = {"error": str(message), "http_code": str(http_code)}
            remark = (
                f"{classname(self):s}.get({url:s}) 2 - " f"error {str(message):s}"
            )
            print(remark)
            logging.debug(remark)
        else:
            remark = (
                f"{classname(self):s}.get({url:s} 3 - "
                f"http_code: {response.status_code:d}"
            )
            print(remark)
            logging.info(remark)
        remark = f"{classname(self):s}.get({url:s}) 4"
        logging.info(remark)
        return content, attributes


@contextmanager
def open_scraper() -> Generator[Scraper, None, None]:
    try:
        client = Scraper()
        client.start()
        yield client
    except Exception as error:
        remark = f"open_webclient error: {str(error):s}"
        logging.debug(remark)
    finally:
        client.stop()

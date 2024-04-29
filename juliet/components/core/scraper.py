import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator

from requests import Session

from components.helpers import classname, get_timestamp


class Scraper:
    def __init__(self) -> None:
        self._session: Session = Session()

    def start(self) -> None:
        explanation = f"{classname(self):s}.start()"
        print(explanation)
        logging.info(explanation)

    def stop(self) -> None:
        # https://stackoverflow.com/questions/49253246/how-to-close-requests-session
        self._session.close()
        explanation = f"{classname(self):s}.stop()"
        print(explanation)
        logging.info(explanation)

    def get(self, url: str) -> Dict[Any, Any]:
        explanation = f"{classname(self):s}.get({url:s}) 1"
        print(explanation)
        logging.info(explanation)
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
            explanation = (
                f"{classname(self):s}.get({url:s}) 2 - " f"error {str(message):s}"
            )
            print(explanation)
            logging.debug(explanation)
        else:
            explanation = (
                f"{classname(self):s}.get({url:s} 3 - "
                f"http_code: {response.status_code:d}"
            )
            print(explanation)
            logging.info(explanation)
        explanation = f"{classname(self):s}.get({url:s}) 4"
        logging.info(explanation)
        return content, attributes


@contextmanager
def open_scraper() -> Generator[Scraper, None, None]:
    try:
        client = Scraper()
        client.start()
        yield client
    except Exception as error:
        explanation = f"open_webclient error: {str(error):s}"
        logging.debug(explanation)
    finally:
        client.stop()

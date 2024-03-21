import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator

from requests import Session

from components.helpers import classname


class WebClient:
    def __init__(self) -> None:
        self._session: Session = Session()

    def start(self) -> None:
        logging.info(f"{classname(self):s}.start()")

    def stop(self) -> None:
        # https://stackoverflow.com/questions/49253246/how-to-close-requests-session
        self._session.close()
        logging.info(f"{classname(self):s}.stop()")

    def get(self, url: str) -> Dict[Any, Any]:
        logging.info(f"{classname(self):s}.get({url:s}) 1")
        try:
            response = self._session.get(url, headers={"User-Agent": "Mozilla/5.0"})
        except Exception as exception:
            remark = (
                f"{classname(self):s}.get({url:s}) 2 - " f"error {str(exception):s}"
            )
            logging.debug(remark)
            return {"errorMessage": remark}
        else:
            remark = (
                f"{classname(self):s}.get({url:s} 3 - "
                f"status_code: {response.status_code:d}"
            )
            logging.info(remark)
            if response.status_code == 200:
                return response.json()
            else:
                remark = (
                    f"{classname(self):s}.get({url:s}) "
                    f"error unexpected status_code: {response.status_code:d}"
                )
                logging.debug(remark)
                return {"errorMessage": remark}
        logging.info(f"{classname(self):s}.get({url:s}) 4")


@contextmanager
def open_webclient() -> Generator[WebClient, None, None]:
    try:
        webclient = WebClient()
        webclient.start()
        yield webclient
    except Exception as error:
        remark = f"open_webclient error: {str(error):s}"
        logging.debug(remark)
    finally:
        webclient.stop()

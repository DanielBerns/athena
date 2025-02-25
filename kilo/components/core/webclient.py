import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator
from requests import Session
from components.helpers import classname

class WebClient:
    """
    WebClient is a class that handles HTTP GET requests using the requests library.
    """

    def __init__(self) -> None:
        """
        Initialize the WebClient with a new requests Session.
        """
        self._session: Session = Session()

    def start(self) -> None:
        """
        Start the WebClient session and log the action.
        """
        logging.info(f"{classname(self):s}.start()")

    def stop(self) -> None:
        """
        Close the WebClient session and log the action.
        """
        # Close the session to release resources
        # See https://stackoverflow.com/questions/49253246/how-to-close-requests-session
        self._session.close()
        logging.info(f"{classname(self):s}.stop()")

    def get(self, url: str) -> Dict[Any, Any]:
        """
        Perform a GET request to the specified URL.

        Args:
            url (str): The URL to send the GET request to.

        Returns:
            Dict[Any, Any]: The response JSON if the request was successful,
                            otherwise a dictionary with an error message.
        """
        logging.info(f"{classname(self):s}.get({url:s}) 1")
        try:
            response = self._session.get(url, headers={"User-Agent": "Mozilla/5.0"})
        except Exception as exception:
            explanation = (
                f"{classname(self):s}.get({url:s}) 2 - " f"error {str(exception):s}"
            )
            logging.debug(explanation)
            return {"errorMessage": explanation}
        else:
            explanation = (
                f"{classname(self):s}.get({url:s} 3 - "
                f"status_code: {response.status_code:d}"
            )
            logging.info(explanation)
            if response.status_code == 200:
                return response.json()
            else:
                explanation = (
                    f"{classname(self):s}.get({url:s}) "
                    f"error unexpected status_code: {response.status_code:d}"
                )
                logging.debug(explanation)
                return {"errorMessage": explanation}
        logging.info(f"{classname(self):s}.get({url:s}) 4")


@contextmanager
def open_webclient() -> Generator[WebClient, None, None]:
    """
    Context manager to handle the lifecycle of a WebClient.

    Yields:
        Generator[WebClient, None, None]: An instance of WebClient.
    """
    try:
        webclient = WebClient()
        webclient.start()
        yield webclient
    except Exception as error:
        explanation = f"open_webclient error: {str(error):s}"
        logging.debug(explanation)
    finally:
        webclient.stop()

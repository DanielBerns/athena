import logging
import time
from contextlib import contextmanager
from typing import Generator, Dict
from components.core.filesystem import FileSystem
from components.configuration import Settings, CLI, Constants
from components.helpers import get_resource_with_timestamp


class Application:
    def __init__(self, file_system: FileSystem, settings: Dict[str, str]):
        self._file_system: FileSystem = file_system
        self._settings: Dict[str, str] = settings

    @property
    def file_system(self) -> FileSystem:
        return self._file_system

    @property
    def settings(self) -> Dict[str, str]:
        return self._settings


def show(message: str) -> None:
    print(message)
    logging.info(message)

def register_error(message: str) -> None:
    print(message)
    logging.error(message)

LOG_LEVELS = {
    "NOTSET": logging.NOTSET,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


@contextmanager
def create_application(
    identifier: str, arguments: Dict[str, str]
) -> Generator[Application, None, None]:
    mode = arguments.get("mode", "live")
    dotenv = arguments.get("dotenv", ".env")
    settings = Settings.build(identifier, mode, dotenv)
    file_system = FileSystem(settings)
    file_system.start()

    log_txt = str(get_resource_with_timestamp(file_system.logs, identifier, ".txt"))
    # log_txt = "./log.txt"
    log_level_key = settings["log_level_key"]
    log_level = LOG_LEVELS.get(settings[log_level_key], logging.DEBUG)

    logging.basicConfig(
        filename=log_txt,
        filemode="w",
        level=log_level,
        format="%(levelname)s > %(message)s",
    )
    logging.info("start")

    application = Application(file_system, settings)
    show("application started")
    start_time = time.time()
    try:
        yield application
    except Exception as message:
        logging.warning(f"exception: {str(message):s}\n")
    finally:
        end_time = time.time()
        file_system.stop()
        show("application stopped")
        show(f"Execution time: {int(end_time - start_time) * 1000} ms")
    logging.info("stop")

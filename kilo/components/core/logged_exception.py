import logging

class LoggedException(Exception):
    """
    Custom exception for logging errors messages.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


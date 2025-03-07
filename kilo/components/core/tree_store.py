import json
from pathlib import Path
from shutil import rmtree
import logging
from typing import Tuple, Generator

from components.helpers import get_container, get_directory, get_resource, classname


class TreeStoreError(Exception):
    """
    Custom exception for errors related to the TreeStore class.

    This exception is raised when operations within the TreeStore encounter
    issues such as out-of-range indices or invalid operations.  It logs
    the error message before raising the exception.
    """
    def __init__(self, explanation: str) -> None:
        """
        Initializes a TreeStoreError with an explanation message.

        Args:
            explanation: A string describing the error.
        """
        logging.error(explanation)
        super().__init__(explanation)


def base_256(number: int) -> Tuple[int, int, int]:
    """
    Converts a non-negative integer to a base-256 representation.

    Args:
        number: The integer to convert (must be between 0 and 16777215 inclusive).

    Returns:
        A tuple of three integers representing the base-256 digits
        (most significant to least significant).

    Raises:
        AssertionError: If the input number is out of range.
    """
    assert 0 <= number < 16777216, f"Input number must be between 0 and 16777215. Got {number}"
    third_digit = number % 256
    number >>= 8  # Equivalent to number //= 256
    second_digit = number % 256
    first_digit = number >> 8  # Equivalent to number //= 256
    return first_digit, second_digit, third_digit


def base_10(first_digit: int, second_digit: int, third_digit: int) -> int:
    """
    Converts a three-digit base-256 number to its base-10 representation.

    Args:
        first_digit: The most significant digit (0-255).
        second_digit: The middle digit (0-255).
        third_digit: The least significant digit (0-255).

    Returns:
        The integer representation of the base-256 number.
    """
    return (((first_digit << 8) + second_digit) << 8) + third_digit


def get_sample_identifier(number: int) -> Tuple[str, str, str]:
    """
    Generates a zero-padded, 9-digit string identifier from an integer.

    Args:
        number: The integer to convert (must be between 0 and 16777215 inclusive).

    Returns:
        Three 3-character strings representing the identifier (e.g., "000000000", "001002003").
    """
    first_digit, second_digit, third_digit = base_256(number)
    return (f"{first_digit:03d}", f"{second_digit:03d}", f"{third_digit:03d}")


class Index:
    """
    Manages an integer index stored in a JSON file.

    This class provides methods to read, write, and increment an index value
    that is persisted in a JSON file.  It's used to keep track of the
    current sample number in the TreeStore.
    """
    def __init__(self, resource: Path) -> None:
        """
        Initializes the Index object.

        Args:
            resource: The path to the JSON file where the index is stored.
        """
        self._resource: Path = resource
        if self.resource.exists():
            # Restarting Index: Load existing value.
            value = self.read()
            self._value = int(value["index"])
        else:
            # Initialize Index: Start from 0.
            self._value = 0
            self.write()

    @property
    def resource(self) -> Path:
        """
        Returns the path to the index file.

        Returns:
            Path: The path to the JSON file.
        """
        return self._resource

    @property
    def value(self) -> int:
        """
        Returns the current value of the index.

        Returns:
            int: The current index value.
        """
        return self._value

    @value.setter
    def value(self, update: int) -> None:
        """
        Sets the index to a new value and writes it to the file.

        Args:
            update: The new value for the index.
        """
        self._value = update
        self.write()

    def write(self) -> None:
        """
        Writes the current index value to the JSON file.
        """
        value = {"index": str(self.value)}
        with open(self.resource, "w") as target:
            json.dump(value, target)

    def read(self) -> dict[str, str]:
        """
        Reads the index value from the JSON file.

        Returns:
            dict[str, str]: A dictionary containing the index value (as a string).
        """
        with open(self.resource, "r") as source:
            values = json.load(source)
        return values


class TreeStore:
    """
    Manages a hierarchical directory structure for storing samples.

    The TreeStore organizes samples into directories named using a 9-digit
    zero-padded identifier. It uses an Index object to keep track of the
    next available sample identifier.  The structure is as follows:

    ```
    <base_path>/
        <identifier>/  (e.g., my_data)
            index.json
            samples/
                000000000/
                000000001/
                ...
                <sample_id>/
                    ... (sample data) ...
    ```
    """
    def __init__(self, base: Path, identifier: str) -> None:
        """
        Initializes a TreeStore object.

        Args:
            base: The base directory where the TreeStore will be created.
            identifier: A string identifier for this specific TreeStore instance.
        """
        self._home = get_container(base, identifier)
        self._samples = get_container(self.home, "samples")
        resource = get_resource(self.home, "index", ".json")
        self._index = Index(resource)

    @property
    def home(self) -> Path:
        """
        Returns the root directory of the TreeStore.

        Returns:
           Path: The path to the TreeStore's home directory.
        """
        return self._home

    @property
    def samples(self) -> Path:
        """
        Returns the directory containing the sample subdirectories.

        Returns:
            Path: The path to the samples directory.
        """
        return self._samples

    @property
    def index(self) -> Index:
        """
        Returns the Index object associated with this TreeStore.

        Returns:
             Index: The Index object.
        """
        return self._index

    def create_sample_home(self) -> Path:
        """
        Creates a new sample directory and increments the index.

        Returns:
            Path: The path to the newly created sample directory.
        """
        (alpha, bravo, charlie) = get_sample_identifier(self.index.value)
        new_sample_home = get_directory(Path(self.samples, alpha, bravo, charlie))
        self.index.value += 1
        return new_sample_home

    def start(self) -> None:
        """Logs a message indicating the start of the TreeStore."""
        logging.info(f"treestore.start() with index {self.index.value:d}")

    def stop(self) -> None:
        """Logs a message indicating the stop of the TreeStore."""
        logging.info(f"treestore.stop() with index {self.index.value:d}")

    def iterate(self, top: int = -1) -> Generator[Path, None, None]:
        """
        Iterates over the sample directories.

        Args:
            top: The maximum number of sample directories to iterate over.
                 If -1 (default), iterates over all existing sample directories.

        Yields:
            Path: The path to each sample directory.

        Raises:
            TreeStoreError: If `top` is greater than the current index value.
        """
        if top == -1:
            top = self.index.value
        elif 0 <= top <= self.index.value:
            pass  # Valid top value
        else:
            explanation = (
                f"{classname(self):s}.samples:"
                f"top {top:d} out of range (-1, {self.index.value:d})"
            )
            raise TreeStoreError(explanation)

        for k in range(top):
            (alpha, bravo, charlie) = get_sample_identifier(k)
            yield get_container(Path(self.samples, alpha, bravo, charlie))

    def get_sample_home(self, k: int) -> Path:
        """
        Retrieves the path to a specific sample directory by its index.

        Args:
            k: The index of the sample directory.

        Returns:
           Path: The path to the requested sample directory.
        """
        return get_container(self.samples, get_sample_identifier(k))

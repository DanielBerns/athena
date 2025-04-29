# Please, write test for the class FlatStore using the module unittest
import glob
from pathlib import Path
from typing import Generator, List

from components.helpers import get_container

class FlatStore:
    """
    A class for managing a simple file-based storage system where data is organized
    into a hierarchical structure of directories.  The `FlatStore` creates a
    "home" directory, and within that, "samples" directories.

    Args:
        base (Path): The base directory where the FlatStore's home directory will be created.
        identifier (str): An identifier string used to name the FlatStore's home directory
            (created as a subdirectory within `base`).

    Attributes:
        _home (Path):  The private home directory of the FlatStore.  This is where
            all samples directories are stored.

    Example:
        ```python
        from pathlib import Path
        # from flatstore import FlatStore  # Assuming FlatStore is in your_module.py

        base_path = Path("./my_data")
        store = FlatStore(base_path, "my_experiment")

        # store.home will be ./my_data/my_experiment
        print(store.home)

        # Create a new sample directory
        sample_1_path = store.sample_home("sample_1")
        # sample_1_path will be ./my_data/my_experiment/sample_1
        print(sample_1_path)
        ```
    """

    def __init__(self, base: Path, identifier: str) -> None:
        """
        Initializes a new FlatStore instance. Creates the home directory if it
        doesn't already exist.
        """
        self._home = get_container(base, identifier)

    @property
    def home(self) -> Path:
        """
        Path: The home directory of the FlatStore.  This directory is created
        during initialization.  It serves as the root for all sample directories.
        """
        return self._home

    def sorted_sample_keys(self) -> List[str]:
        """
        Gets a list of the sample directory names (keys), sorted alphabetically.

        Returns:
            List[str]: A sorted list of strings, where each string is the name
                (stem) of a sample directory within the FlatStore's home directory.
                Returns an empty list if no sample directories exist.

        Example:
            ```python
            # Assuming sample directories "sample_2", "sample_1", "sample_3" exist.
            keys = store.sorted_sample_keys()
            print(keys)  # Output: ['sample_1', 'sample_2', 'sample_3']
            ```
        """
        paths = [dd for dd in glob.glob(f"{str(self.home):s}/*")]
        sorted_paths = sorted(paths)
        return [Path(dd).stem for dd in sorted_paths]


    def sample_home(self, key: str) -> Path:
        """
        Gets the path to a specific sample directory. Creates the sample directory
        if it doesn't already exist.

        Args:
            key (str): The name (key) of the sample directory.

        Returns:
            Path: The `Path` object representing the sample directory.

        Example:
            ```python
            sample_dir = store.sample_home("my_sample")
            # sample_dir will be a Path object representing the directory
            # store.home / "my_sample", and the directory will be created.
            ```
        """
        return get_container(self.home, key)

    def iterate(self, first: str == "") -> Generator[Path, None, None]:
        """
        Iterates over the samples directory within the FlatStore's home directory.

        Yields:
            Path:  A `Path` object representing each sample directory.
                   Samples are sorted

        Example:
            ```python
            for sample_path in store.iterate():
                print(sample_path)  # Prints the Path to each sample directory.
            ```
        """
        if len(first):
            for dd in self.sorted_sample_keys():
                if dd < first:
                    continue
                yield self.sample_home(dd)
        else:
            yield from ()


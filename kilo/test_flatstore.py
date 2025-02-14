import unittest
import shutil
import tempfile
from pathlib import Path

from components.core.flatstore import FlatStore
from components.helpers.helpers import get_container


class TestFlatStore(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

    def tearDown(self):
        # Remove the temporary directory after testing
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        identifier = "test_store"
        store = FlatStore(self.test_dir, identifier)
        expected_home = self.test_dir / identifier
        self.assertEqual(store.home, expected_home)

    def test_sorted_sample_keys(self):
        store = FlatStore(self.test_dir, "my_store")
        # Create some sample directories in a non-sorted order
        (store.home / "sample_c").mkdir()
        (store.home / "sample_a").mkdir()
        (store.home / "sample_b").mkdir()

        keys = store.sorted_sample_keys()
        self.assertEqual(keys, ["sample_a", "sample_b", "sample_c"])

    def test_sorted_sample_keys_empty(self):
        store = FlatStore(self.test_dir, "empty_store")
        keys = store.sorted_sample_keys()
        self.assertEqual(keys, [])  # Should return an empty list

    def test_iterate(self):
        store = FlatStore(self.test_dir, "iter_store")
        (store.home / "sample_1").mkdir()
        (store.home / "sample_2").mkdir()

        sample_paths = list(store.iterate())
        self.assertEqual(len(sample_paths), 2)
        # Check if the returned paths are correct (order may vary, so use set)
        expected_paths = {store.home / "sample_1", store.home / "sample_2"}
        actual_paths = set(sample_paths)
        self.assertEqual(actual_paths, expected_paths)


    def test_iterate_empty(self):
        store = FlatStore(self.test_dir, "empty_iter_store")
        sample_paths = list(store.iterate())
        self.assertEqual(len(sample_paths), 0)

    def test_sample_home(self):
        store = FlatStore(self.test_dir, "main_store")
        key = "sub_sample"
        sample_path = store.sample_home(key)
        expected_path = store.home / key
        self.assertEqual(sample_path, expected_path)
        self.assertTrue(expected_path.exists()) # Ensure directory is created

    def test_get_container(self):
        base_path = self.test_dir / "base"
        identifier = "sub"
        container_path = get_container(base_path, identifier)

        self.assertEqual(container_path, base_path / identifier)
        self.assertTrue(container_path.exists())

        #Test with a non-existing base
        non_existing_path = self.test_dir / "non_existing"
        identifier2 = "sub2"
        container_path2 = get_container(non_existing_path,identifier2)
        self.assertEqual(container_path2, non_existing_path / identifier2)
        self.assertTrue(container_path2.exists())


if __name__ == '__main__':
    unittest.main()

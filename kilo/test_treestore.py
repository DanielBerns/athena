from pathlib import Path
from shutil import rmtree
import unittest

from components.core.treestore import TreeStore, Index, TreeStoreError, get_sample_identifier, base_256, base_10

class TestTreeStore(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_treestore")
        self.test_dir.mkdir(exist_ok=True)
        self.base_path = self.test_dir / "base"
        self.base_path.mkdir(exist_ok=True)
        self.identifier = "my_treestore"
        self.treestore = TreeStore(self.base_path, self.identifier)

    def tearDown(self):
        rmtree(self.test_dir)

    def test_create_sample_home(self):
        sample_home = self.treestore.create_sample_home()
        self.assertTrue(sample_home.exists())
        self.assertEqual(self.treestore.index.value, 1)
        sample_home2 = self.treestore.create_sample_home()
        self.assertTrue(sample_home2.exists())
        self.assertEqual(self.treestore.index.value, 2)
        self.assertNotEqual(sample_home, sample_home2)


    def test_index_initialization(self):
        index_path = self.treestore.home / "index.json"
        self.assertTrue(index_path.exists())
        index = Index(index_path)
        self.assertEqual(index.value, 0)

    def test_index_increment(self):
        self.treestore.create_sample_home()
        self.assertEqual(self.treestore.index.value, 1)
        self.treestore.create_sample_home()
        self.assertEqual(self.treestore.index.value, 2)

    def test_index_persistence(self):
        self.treestore.create_sample_home()
        self.treestore.create_sample_home()
        new_treestore = TreeStore(self.base_path, self.identifier)  # Re-instantiate
        self.assertEqual(new_treestore.index.value, 2)

    def test_iterate(self):
        for _ in range(5):
            self.treestore.create_sample_home()
        count = 0
        for _ in self.treestore.iterate():
            count += 1
        self.assertEqual(count, 5)

        count = 0
        for _ in self.treestore.iterate(3):
            count += 1
        self.assertEqual(count, 3)

        with self.assertRaises(TreeStoreError):
            for _ in self.treestore.iterate(10):
                pass

    def test_get_sample_home(self):
        sample_home_0 = self.treestore.get_sample_home(0)
        self.assertEqual(sample_home_0, self.treestore.samples / "000000000")
        self.treestore.create_sample_home()
        sample_home_1 = self.treestore.get_sample_home(1)
        self.assertEqual(sample_home_1, self.treestore.samples / "000000001")

    def test_base_256(self):
        self.assertEqual(base_256(0), (0, 0, 0))
        self.assertEqual(base_256(255), (0, 0, 255))
        self.assertEqual(base_256(256), (0, 1, 0))
        self.assertEqual(base_256(65535), (0, 255, 255))
        self.assertEqual(base_256(65536), (1, 0, 0))
        self.assertEqual(base_256(16777215), (255, 255, 255))
        with self.assertRaises(AssertionError):
            base_256(-1)
        with self.assertRaises(AssertionError):
            base_256(16777216)

    def test_base_10(self):
        self.assertEqual(base_10(0, 0, 0), 0)
        self.assertEqual(base_10(0, 0, 255), 255)
        self.assertEqual(base_10(0, 1, 0), 256)
        self.assertEqual(base_10(0, 255, 255), 65535)
        self.assertEqual(base_10(1, 0, 0), 65536)
        self.assertEqual(base_10(255, 255, 255), 16777215)

    def test_get_sample_identifier(self):
        self.assertEqual(get_sample_identifier(0), "000000000")
        self.assertEqual(get_sample_identifier(255), "000000255")
        self.assertEqual(get_sample_identifier(256), "000001000")
        self.assertEqual(get_sample_identifier(65535), "000255255")
        self.assertEqual(get_sample_identifier(65536), "001000000")
        self.assertEqual(get_sample_identifier(16777215), "255255255")

    def test_start_stop(self):
        # Just make sure they don't raise exceptions
        self.treestore.start()
        self.treestore.stop()
        self.treestore.create_sample_home()
        self.treestore.start()
        self.treestore.stop()

if __name__ == '__main__':
    unittest.main()

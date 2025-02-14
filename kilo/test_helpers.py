import unittest
from datetime import datetime, timezone, timedelta
import os
import json
from pathlib import Path
import tempfile

from components.helpers.helpers import (
    classname, indentation, i, aware_utcnow, get_timestamp, read_json, write_json,
    read_text, write_text, read_text_lines, write_text_lines,
    get_directory, get_container, get_resource, get_resource_with_timestamp,
    remove_directory, get_environment_variable
)


class TestMyModule(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        # Remove the temporary directory after testing
        remove_directory(self.temp_dir)

    def test_classname(self):
        self.assertEqual(classname(self), "TestMyModule")
        self.assertEqual(classname("test"), "str")
        self.assertEqual(classname(123), "int")

    def test_i(self):
        self.assertEqual(i(0), "")
        self.assertEqual(i(1), indentation)
        self.assertEqual(i(3), indentation * 3)

    def test_aware_utcnow(self):
        # Basic check if it returns a datetime object.  Precise time comparison
        # is tricky due to potential delays. We'll check the timezone.
        offset = timedelta(hours=5)
        dt = aware_utcnow(offset)
        self.assertEqual(dt.tzinfo, timezone(offset))


    def test_get_timestamp(self):
        offset = timedelta(hours=-8)  # PST
        timestamp = get_timestamp(separator="_", offset=offset)
        now = aware_utcnow(offset)
        expected_prefix = f"{now.year:4d}_{now.month:02d}_{now.day:02d}_{now.hour:02d}_{now.minute:02d}_{now.second:02d}"
        self.assertTrue(timestamp.startswith(expected_prefix))
        self.assertEqual(len(timestamp), len("YYYY_MM_DD_HH_MM_SS"))


    def test_read_write_json(self):
        test_file = self.temp_dir / "test.json"
        data = {"key1": "value1", "key2": "value2"}
        write_json(test_file, data)
        read_data = read_json(test_file)
        self.assertEqual(read_data, data)
        #Test with empty dictionary
        empty_data = {}
        write_json(test_file, empty_data)
        read_empty_data = read_json(test_file)
        self.assertEqual(read_empty_data, empty_data)

    def test_read_write_text(self):
        test_file = self.temp_dir / "test.txt"
        text = "This is a test string.\nWith multiple lines."
        write_text(test_file, text)
        read_text_content = read_text(test_file)
        self.assertEqual(read_text_content, text)
        #Test empty string.
        write_text(test_file, "")
        self.assertEqual(read_text(test_file), "")

    def test_read_write_text_lines(self):
        test_file = self.temp_dir / "test_lines.txt"
        lines = ["Line 1", "Line 2", "Line 3"]

        writer = write_text_lines(test_file)
        next(writer)  # Initialize the generator
        for line in lines:
            writer.send(line)
        try:
            writer.send(None) # Close the generator
        except StopIteration:
            pass
        else:
            self.assertTrue(False)

        read_lines = list(read_text_lines(test_file))
        self.assertEqual(read_lines, lines)

        # Test empty file
        empty_file = self.temp_dir / "empty.txt"
        writer = write_text_lines(empty_file)
        next(writer)
        try:
            writer.send(None) # Close the generator
        except StopIteration:
            pass
        else:
            self.assertTrue(False)


    def test_get_directory(self):
        test_dir = self.temp_dir / "test_dir"
        returned_dir = get_directory(test_dir)
        self.assertEqual(returned_dir, test_dir)
        self.assertTrue(test_dir.exists())
        self.assertTrue(test_dir.is_dir())

        # Test with expansion of ~
        home_dir_plus = Path("~", "test_expand")
        expanded = get_directory(home_dir_plus)
        self.assertTrue(expanded.is_absolute())
        remove_directory(expanded)


    def test_get_container(self):
        test_dir = self.temp_dir / "base_dir"
        identifier = "sub_dir"
        container_dir = get_container(test_dir, identifier)
        expected_dir = test_dir / identifier
        self.assertEqual(container_dir, expected_dir)
        self.assertTrue(container_dir.exists())


    def test_get_resource(self):
        test_dir = self.temp_dir / "resource_dir"
        name = "my_file"
        suffix = ".txt"
        resource_path = get_resource(test_dir, name, suffix)
        expected_path = test_dir / "my_file.txt"
        self.assertEqual(resource_path, expected_path)
        self.assertTrue(test_dir.exists()) # Directory should be created

    def test_get_resource_with_timestamp(self):
        test_dir = self.temp_dir / "resource_dir_ts"
        name = "my_file"
        suffix = ".txt"
        resource_path = get_resource_with_timestamp(test_dir, name, suffix)
        self.assertTrue(test_dir.exists())
        self.assertTrue(resource_path.name.startswith("my_file_"))
        self.assertTrue(resource_path.name.endswith(".txt"))
        self.assertEqual(resource_path.suffix, suffix)

    def test_remove_directory(self):
        test_dir = self.temp_dir / "remove_me"
        test_dir.mkdir()
        remove_directory(test_dir)
        self.assertFalse(test_dir.exists())

    def test_get_environment_variable(self):
        # Test with an existing variable
        existing_var = "PATH"  # Assuming PATH is always set
        self.assertEqual(get_environment_variable(existing_var), os.environ[existing_var])
        #Test default
        self.assertEqual(get_environment_variable("NO_SUCH_VAR", "default"), "default")
        # Test with a non-existing variable and no default
        self.assertEqual(get_environment_variable("NON_EXISTENT_VAR"), "-")
        #Test empty default
        os.environ["TEST_VAR"] = "test_value"
        self.assertEqual(get_environment_variable("TEST_VAR", ""), "test_value")
        del os.environ["TEST_VAR"]


if __name__ == '__main__':
    unittest.main()

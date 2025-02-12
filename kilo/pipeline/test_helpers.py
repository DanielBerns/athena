from datetime import datetime, timezone, timedelta
import time

from components import random_sleep, get_timestamp, aware_utcnow, ARG, UTC

import unittest

class TestFunctions(unittest.TestCase):

    def test_random_sleep(self):
        start_time = aware_utcnow()
        random_sleep(base=2, lo=1, hi=3)
        end_time = aware_utcnow()
        delta = end_time - start_time
        # print(f"{delta=}")
        self.assertTrue(timedelta(seconds=0) < delta <= timedelta(seconds=6), "Sleep duration not within expected range")

    def test_aware_utcnow(self):
        now_arg = aware_utcnow(offset=timedelta(hours=-3))
        now_utc = now_arg + timedelta(hours=3)
        time_diff = now_utc - now_arg
        # print(f"{now_utc=}")
        # print(f"{now_arg=}")
        # print(f"{time_diff=}")
        self.assertTrue(timedelta(hours=2, minutes=59) <= time_diff <= timedelta(hours=3, minutes=1), "Timezone offset incorrect")

    def test_get_timestamp(self):
        timestamp = get_timestamp()
        self.assertEqual(len(timestamp), 14, "Timestamp length incorrect")
        try:
            int(timestamp)  # Should be convertible to an int
        except ValueError:
            self.fail("Timestamp should be numeric")

        timestamp_with_sep = get_timestamp(separator="-")
        self.assertIn("-", timestamp_with_sep, "Separator not present")

        now = aware_utcnow()
        expected_start = f"{now.year:4d}{now.month:02d}{now.day:02d}"
        self.assertEqual(timestamp[:8], expected_start, "Date part of timestamp incorrect")


if __name__ == "__main__":
    unittest.main()






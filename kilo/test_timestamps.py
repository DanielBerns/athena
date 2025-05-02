from components.helpers.timestamps import (
    timestamp_to_datetime,
    timestamp_to_datetime_sequence,
    datetime_to_timestamp,
    datetime_to_timestamp_sequence,
    get_ideal_datetime_sequence,
    find_closest_datetimes,
    generate_closest_datetime_sequence
)



def test_find_closest_datetimes():
    """Tests the find_closest_datetimes function."""
    timestamps = [
        "20230101100000", # 0
        "20230108095958", # 1: Closest (-2s) to 20230115 - 7 days
        "20230108100000", # 2: Exact match for 20230115 - 7 days
        "20230108100003", # 3: Also close (+3s) to 20230115 - 7 days
        "20230110120000", # 4
        "20230115100000", # 5: Target 1
        "20230120100000", # 6
        "20230122090000", # 7: Closest to 20230129 - 7 days (but only one)
        "20230129100000", # 8: Target 2
        "20230201120000", # 9
        "20230205115955", # 10: Closest (-5s) to 20230212 - 7 days
        "20230205120005", # 11: Also closest (+5s) to 20230212 - 7 days
        "20230212120000", # 12: Target 3
        "20230213000000", # 13: Target 4 (no match exactly 7 days prior)
    ]

    # Test case 1: timestamps -> datetimes -> timestamps
    datetimes = timestamp_to_datetime_sequence(timestamps)
    result = datetime_to_timestamp_sequence(datetimes)
    print("test 1")
    for ts, rr in zip(timestamps, result):
        print(ts == rr, ts, rr)
    print("-"*80)

    # Test case 2: Exact match found
    initial_timestamp = "20230115100000"
    initial_datetime = timestamp_to_datetime(initial_timestamp)
    expected_timestamps_sequence = ["20230108100000"]
    ideal_datetime_sequence = get_ideal_datetime_sequence(initial_datetime, days_difference=7, length=1)
    closest_datetimes = find_closest_datetimes(
        datetimes, ideal_datetime_sequence[0]
    )
    print("test 2")
    if closest_datetimes:
        sequence = closest_datetimes if closest_datetimes else []
        result = datetime_to_timestamp_sequence([dt for (i, dt) in sequence])
        for ts, rr in zip(expected_timestamps_sequence, result):
            print(ts == rr, ts, rr)
    else:
        print("closest_datetimes is empty")
    print("-"*80)

    # Test case 3: Closest match (single)
    initial_timestamp = "20230129100000"
    initial_datetime = timestamp_to_datetime(initial_timestamp)
    expected_timestamps_sequence = ["20230122090000"] # This is 7d 1h before, closer than 20230120 (9d)
    ideal_datetime_sequence = get_ideal_datetime_sequence(initial_datetime, days_difference=7, length=1)
    closest_datetimes = find_closest_datetimes(
        datetimes, ideal_datetime_sequence[0]
    )
    print("test 3")
    if closest_datetimes:
        sequence = closest_datetimes if closest_datetimes else []
        result = datetime_to_timestamp_sequence([dt for (i, dt) in sequence])
        for ts, rr in zip(expected_timestamps_sequence, result):
            print(ts == rr, ts, rr)
    else:
        print("closest_datetimes is empty")
    print("-"*80)

    # Test case 4: Multiple closest matches (equidistant)
    initial_timestamp = "20230212120000"
    initial_datetime = timestamp_to_datetime(initial_timestamp)
    expected_timestamps_sequence = ["20230205115955", "20230205120005"] # Both are 5 seconds away
    ideal_datetime_sequence = get_ideal_datetime_sequence(initial_datetime, days_difference=7, length=1)
    closest_datetimes = find_closest_datetimes(
        datetimes, ideal_datetime_sequence[0]
    )
    print("test 4")
    if closest_datetimes:
        sequence = closest_datetimes if closest_datetimes else []
        result = datetime_to_timestamp_sequence([dt for (i, dt) in sequence])
        for ts, rr in zip(expected_timestamps_sequence, result):
            print(ts == rr, ts, rr)
    else:
        print("closest_datetimes is empty")
    print("-"*80)

    # Test case 5: Target is the first element
    target_timestamp = "20230101100000"
    target_datetime = timestamp_to_datetime(target_timestamp)
    expected_timestamps_sequence: List[str] = []
    closest_datetimes = find_closest_datetimes(
        datetimes, target_datetime
    )
    print("test 5")
    if closest_datetimes:
        sequence = closest_datetimes if closest_datetimes else []
        result = datetime_to_timestamp_sequence([dt for (i, dt) in sequence])
        print(f"test 5 == {len(result) == 1} - target_timestamp: {target_timestamp} - target_datetime: {target_datetime}")
        for rr in result:
            print(f"{rr}")
    print("-"*80)

    # Test case 6: Empty datetimes list
    target_timestamp = "20230101100000"
    target_datetime = timestamp_to_datetime(target_timestamp)
    closest_datetimes = find_closest_datetimes(
        [], target_datetime
    )
    if closest_datetimes is None:
        print(f"test 6 == {closest_datetimes is None}")
    else:
        print("closest_datetimes is not None")
        for kk, vv in closest_datetimes:
            print(f"{vv} at {kk}")
    print("-"*80)

    # Test case 7: No timestamp exactly 7 days before, closest is selected
    initial_timestamp = "20230213000000" # 7 days prior is 20230206000000
    initial_datetime = timestamp_to_datetime(initial_timestamp)
    expected_timestamps_sequence = ["20230205120005"] # This is the closest one before the target
    ideal_datetime_sequence = get_ideal_datetime_sequence(initial_datetime, days_difference=7, length=1)
    closest_datetimes = find_closest_datetimes(
        datetimes, ideal_datetime_sequence[0]
    )
    print("test 7")
    if closest_datetimes:
        sequence = closest_datetimes if closest_datetimes else []
        result = datetime_to_timestamp_sequence([dt for (i, dt) in sequence])
        for ts, rr in zip(expected_timestamps_sequence, result):
            print(ts == rr, ts, rr)
    else:
        print("closest_datetimes is empty")
    print("-"*80)

    # Test case 8: Specify a different day difference (e.g., 1 day)
    initial_timestamp = "20230108100000" # Target index 2
    initial_datetime = timestamp_to_datetime(initial_timestamp)
    expected_timestamps_sequence = ["20230108100000"]
    ideal_datetime_sequence = get_ideal_datetime_sequence(initial_datetime, days_difference=1, length=1)
    expected_timestamps_sequence = ["20230108095958"] # Looking for ~20230107100000, index 2 is closest
    closest_datetimes = find_closest_datetimes(
        datetimes, ideal_datetime_sequence[0]
    )
    print("test 8")
    if closest_datetimes:
        sequence = closest_datetimes if closest_datetimes else []
        result = datetime_to_timestamp_sequence([dt for (i, dt) in sequence])
        for ts, rr in zip(expected_timestamps_sequence, result):
            print(ts == rr, ts, rr)
    else:
        print("closest_datetimes is empty")
    print("-"*80)

    new_timestamps = [
        "20240101101010",
        "20240109101010",
        "20240114101010",
        "20240122101010",
        "20240129101010",
        "20240205101010",
        "20240212101010",
        "20240219101010",
        "20240227101010",
        "20240305101010",
        "20240312101010",
        "20240320101010",
    ]
    new_datetimes = timestamp_to_datetime_sequence(new_timestamps)
    new_ideal_datetime_sequence = get_ideal_datetime_sequence(new_datetimes[-1], length=10)
    for target, closest in generate_closest_datetime_sequence(new_datetimes, new_ideal_datetime_sequence):
        print(
            datetime_to_timestamp(target),
            "->",
            datetime_to_timestamp(closest),
            "--",
            str(target - closest)
        )

if __name__ == "__main__":
    test_find_closest_datetimes()

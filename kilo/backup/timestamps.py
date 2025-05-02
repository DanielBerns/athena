import datetime
from typing import List, Optional

# Define the timestamp format globally for consistency
TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

def find_closest_past_timestamps(
    timestamps: List[str],
    target_timestamp: str,
    days_diff: int = 7
) -> List[str]:
    """
    Finds timestamps in a sorted list that are closest to a specific number
    of days prior to a target timestamp.

    Given a sorted list of timestamp strings ("YYYYMMDDhhmmss") and a
    target timestamp string from that list, this function identifies all
    timestamps that occurred *before* the target and are exactly 'days_diff'
    (default 7) days earlier, or are the closest in time difference to that
    ideal date if an exact match is not found.

    Args:
        timestamps: A list of timestamp strings in "YYYYMMDDhhmmss" format,
                    sorted in ascending chronological order.
        target_timestamp: The reference timestamp string (must exist in the
                          'timestamps' list).
        days_diff: The target number of days difference (default is 7).

    Returns:
        A list of timestamp strings from the input list that represent the
        closest match(es) to 'days_diff' days before the 'target_timestamp'.
        Returns an empty list if 'timestamps' is empty, 'target_timestamp'
        is not found, 'target_timestamp' is the first element, or no
        prior timestamps exist.

    Raises:
        ValueError: If any timestamp string in the list (including the target)
                    does not conform to the "YYYYMMDDhhmmss" format.
    """
    if not timestamps:
        return []

    try:
        # Find the index of the target timestamp
        target_index = timestamps.index(target_timestamp)
    except ValueError:
        # Target timestamp not found in the list
        print(f"Warning: Target timestamp '{target_timestamp}' not found in the list.")
        return []

    # If the target is the first element, there are no previous timestamps
    if target_index == 0:
        return []

    try:
        # Convert target timestamp string to datetime object
        target_dt = datetime.datetime.strptime(target_timestamp, TIMESTAMP_FORMAT)

        # Calculate the ideal timestamp (target - days_diff)
        ideal_past_dt = target_dt - datetime.timedelta(days=days_diff)

        # --- Find the closest timestamp(s) ---
        min_abs_diff = datetime.timedelta.max  # Initialize with maximum possible timedelta
        closest_timestamps_indices: List[int] = []

        # Iterate only through timestamps *before* the target index
        for i in range(target_index):
            current_ts_str = timestamps[i]
            # Convert current timestamp string to datetime object
            this_dt = datetime.datetime.strptime(current_ts_str, TIMESTAMP_FORMAT)

            # Calculate the absolute difference between current and ideal past time
            abs_diff = abs(this_dt - ideal_past_dt)

            # Check if this difference is the new minimum
            if abs_diff < min_abs_diff:
                min_abs_diff = abs_diff
                closest_timestamps_indices = [i]  # Start a new list with this index
            # Check if this difference is equal to the current minimum
            elif abs_diff == min_abs_diff:
                closest_timestamps_indices.append(i) # Add index to existing list

    except ValueError as e:
        # Reraise if the format is wrong for any timestamp during processing
        raise ValueError(f"Timestamp format error: {e}. Ensure all timestamps are 'YYYYMMDDhhmmss'.") from e


    # Return the actual timestamp strings corresponding to the closest indices
    return [timestamps[idx] for idx in closest_timestamps_indices]


def get_closest_dts(
    ideal_dt: datetime.datetime,
    all_the_dts: List[datetime]
) -> List[datetime.timedelta] | None:
    min_abs_diff = datetime.timedelta.max
    closest_dts: List[datetime.timedelta] | None = None
    for this_dt in all_the_dts:
        abs_diff = abs(this_dt - ideal_dt)
        if abs_diff < min_abs_diff:
            min_abs_diff = abs_diff
            closest_dts = [this_dt]
        elif abs_diff == min_abs_diff:
            closest_dts.append(this_dt)
        else:
            break
    return closest_dts

def find_closest_sequence(
    timestamps: List[str],
    target_timestamp: str,
    days_diff: int = 7
) -> List[List[datetime.timedelta] | None]:
    """
    Finds timestamps in a sorted list that are closest to
    a specific sequence of days prior to a target timestamp.

    Given a sorted list of timestamp strings ("YYYYMMDDhhmmss") and a
    target timestamp string from that list, this function identifies all
    timestamps that occurred *before* the target,
    with a sampling period equal or closest to 'days_diff'
    (default 7) days earlier, or are the closest in time difference to that
    ideal date if an exact match is not found.

    Args:
        timestamps: A list of timestamp strings in "YYYYMMDDhhmmss" format,
                    sorted in ascending chronological order.
        target_timestamp: The reference timestamp string (must exist in the
                          'timestamps' list).
        days_diff: The target number of days difference (default is 7).

    Returns:
        A list of timestamp strings from the input list that represent the
        closest match(es) to a periodic sequence, with period equal to 'days_diff' days,
        before the 'target_timestamp'.
        Returns an empty list if 'timestamps' is empty, or
        'target_timestamp' is not found, or
        'target_timestamp' is the first element, or
        no prior timestamps exist.

    Raises:
        ValueError: If any timestamp string in the list (including the target)
                    does not conform to the "YYYYMMDDhhmmss" format.
    """
    if not timestamps:
        return []

    try:
        # Find the index of the target timestamp
        target_index = timestamps.index(target_timestamp)
    except ValueError:
        # Target timestamp not found in the list
        print(f"Warning: Target timestamp '{target_timestamp}' not found in the list.")
        return []

    # If the target is the first element, there are no previous timestamps
    if target_index == 0:
        return []

    # Convert target timestamp string to datetime object
    all_the_dts = [
        datetime.datetime.strptime(a_timestamp, TIMESTAMP_FORMAT)
        for a_timestamp in timestamps
    ]
    target_dt = all_the_dts[target_index]

    # Calculate the ideal timestamp sequence
    ideal_dt_sequence = [
        target_dt - datetime.timedelta(days=_days) for _days in range(days_diff * target_index, days_diff, -days_diff)
    ]
    closest_dts_sequence = [
        (ideal_dt, get_closest_dts(ideal_dt, all_the_dts[:target_index])) for ideal_dt in ideal_dt_sequence)
    ]

    # Return the closest datetime sequence
    return closest_dts_sequence


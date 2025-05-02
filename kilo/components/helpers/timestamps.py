import datetime
from typing import List, Tuple, Generator

# Define the timestamp format globally for consistency
TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

def timestamp_to_datetime(ts: str) -> datetime.datetime:
    return datetime.datetime.strptime(ts, TIMESTAMP_FORMAT)


def timestamp_to_datetime_sequence(timestamps: List[str]) -> List[datetime.datetime]:
    return [timestamp_to_datetime(this_timestamp) for this_timestamp in timestamps]


def datetime_to_timestamp(dt: datetime.datetime) -> str:
    return dt.strftime(TIMESTAMP_FORMAT)


def datetime_to_timestamp_sequence(datetimes: List[datetime.datetime]) -> List[str]:
    return [datetime_to_timestamp(this_datetime) for this_datetime in datetimes]


def get_ideal_datetime_sequence(
    target_datetime: datetime.datetime,
    days_difference: int = 7,
    length: int = 3
) -> List[datetime.datetime]:
    sequence = [
        target_datetime - datetime.timedelta(days=_days)
        for _days in range(days_difference * length, 0, -days_difference)
    ]
    return sequence


def find_closest_datetimes(
    datetime_sequence: List[datetime.datetime],
    target_datetime: datetime.datetime
) -> List[Tuple[int, datetime.datetime]] | None:

    if len(datetime_sequence) == 0:
        return None
    mininum_absolute_difference = datetime.timedelta.max
    closest_datetimes: List[datetime.timedelta] | None = None
    indices = [vv for vv in range(len(datetime_sequence))]
    for index, this_datetime in zip(indices[-1::-1], datetime_sequence[-1::-1]):
        absolute_difference = abs(this_datetime - target_datetime)
        if absolute_difference < mininum_absolute_difference:
            mininum_absolute_difference = absolute_difference
            closest_datetimes = [(index, this_datetime)]
        elif absolute_difference == mininum_absolute_difference:
            closest_datetimes.append((index, this_datetime))
        else:
            break
    return closest_datetimes # Maybe None

def generate_closest_datetime_sequence(
    datetimes: List[datetime.datetime],
    targets: List[datetime.datetime]
) -> Generator[Tuple[datetime.datetime, datetime.datetime], None, None]:
    lo, hi = 0, len(datetimes)
    for this_target in targets[-1::-1]:
        closest_datetimes = find_closest_datetimes(datetimes[lo:hi], this_target)
        if closest_datetimes:
            (hi, closest_datetime) = closest_datetimes[-1]
            yield this_target, closest_datetime


import re
import time
from datetime import datetime
from datetime import timedelta

REGEX = re.compile(
    r"^((?P<days>[\.\d]+?)d)?((?P<hours>[\.\d]+?)h)?((?P<minutes>[\.\d]+?)m)?((?P<seconds>[\.\d]+?)s)?$"
)


def parse_time(time_str: str) -> timedelta:
    """Parse a time string e.g. (2h13m) into a timedelta object.

    Modified from virhilo's answer at https://stackoverflow.com/a/4628148/851699

    Args:
        time_str: A string identifying a duration.  (eg. 2h13m)

    Returns:
        A `datetime.timedelta` instance.

    CREDIT: https://stackoverflow.com/a/51916936
    """
    parts = REGEX.match(time_str)
    if parts is None:
        raise ValueError(
            f"Could not parse any time information from '{time_str}'.  Examples of "
            "valid strings: '8h', '2d8h5m20s', '2m4s'"
        )

    time_params = {
        name: float(param) for name, param in parts.groupdict().items() if param
    }
    return timedelta(**time_params)


def to_unix(dt: datetime) -> int:
    """Convert <datetime.datetime> to unix timestamp."""
    return int(time.mktime(dt.timetuple()))


def strftimedelta(td: timedelta | float | int) -> str:
    """Convert `datetime.timedelta`, `float` or `int` into a `str` format.

    Example:
        >>> strftimedelta(timedelta(days=1, minutes=1))
        "1 天 0 小時 1 分 0 秒"
        >>> strftimedelta(timedelta(minutes=24))
        "24 分 0 秒"
        >>> strftimedelta(timedelta(seconds=50))
        "50 秒"

    Args:
        td: A `datetime.timedelta` instance.

    Returns:
        Formatted time string
    """
    if not isinstance(td, (timedelta, float, int)):
        raise TypeError

    fields = {"日": 86400, "小時": 3600, "分": 60, "秒": 1}
    result = {}
    remainder = td.total_seconds() if isinstance(td, timedelta) else td
    for field, value in fields.items():
        result[field], remainder = divmod(remainder, value)

    first_value = False
    time_to_joined = []
    for k, v in result.items():
        if v != 0 or first_value:
            first_value = True
            time_to_joined.append(f"{int(v):,} {k}")

    return " ".join(time_to_joined)

"""
utils.time_process
----------------

A set of time processing functions.

:Date: 09-19-2022
:feat: 10-22-2022
    New to_unix() function converts <datetime.datetime> to unix timestamp string.
:feat: 11-28-2022
    New strftimedelta() function converts a <datetime.timedelta> object into a stirng.
"""
import re
import time
from datetime import datetime
from datetime import timedelta


REGEX = re.compile(r'^((?P<days>[\.\d]+?)d)?((?P<hours>[\.\d]+?)h)?((?P<minutes>[\.\d]+?)m)?((?P<seconds>[\.\d]+?)s)?$')


def parse_time(time_str: str) -> timedelta:
    """ Parse a time string e.g. (2h13m) into a timedelta object.

    Modified from virhilo's answer at https://stackoverflow.com/a/4628148/851699

    :param time_str: A string identifying a duration.  (eg. 2h13m)
    :return datetime.timedelta: A datetime.timedelta object

    :CREDIT: https://stackoverflow.com/a/51916936
    """
    parts = REGEX.match(time_str)
    assert parts is not None, f"Could not parse any time information from '{time_str}'.  Examples of valid strings: '8h', '2d8h5m20s', '2m4s'"
    time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
    return timedelta(**time_params)


def to_unix(dt: datetime) -> int:
    """ Convert <datetime.datetime> to unix timestamp. """
    return int(time.mktime(dt.timetuple()))


def strftimedelta(td: timedelta) -> str:
    """ Convert <datetime.timedelta> into a string format.

    :param td: A timedelta object.

    ..:example:
        >> td = timedelta(days=1, minutes=24)
        >> strftimedelta(td)
        "1 天 0 小時 24 分 0 秒"

        >> td = timedelta(seconds=50)
        >> strftimedelta(td)
        "50 秒"
    """

    if not isinstance(td, timedelta):
        raise TypeError

    fields = {"天": 86400, "小時": 3600, "分": 60, "秒": 1}
    result = {}
    remainder = td.total_seconds()
    for field, _value in fields.items():
        result[field], remainder = divmod(remainder, fields[field])

    return " ".join(["%d %s" % (v, k) for k, v in result.items() if v != 0])

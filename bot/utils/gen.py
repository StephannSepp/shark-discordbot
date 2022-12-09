"""
utils.gen
----------------

A set of functions that is related to string generator.

:Date: 09-19-2022
:feat: 10-22-2022
    New One-Time Password generator.
"""
import datetime
import os
import random


def OTP_str(length: int=4) -> str:
    """ Generate a string for one-time password usage.

    :param length: The length of the password, defualt is 4.

    :return OTP: A random password string.
    """
    string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    OTP = ""
    for _ in range(length):
        OTP += string[random.randint(0, len(string)-1)]
    return OTP


def OTP_num(length: int=4) -> str:
    """ Generate a string for one-time password usage.
        But only in numbers.

    :param length: The length of the password, defualt is 4.

    :return OTP: A random password string.
    """
    string = "0123456789"
    OTP = ""
    for _ in range(length):
        OTP += string[random.randint(0, len(string)-1)]
    return OTP


def snowflake() -> int:
    """ Generate a snowflake-like ID.

    ID is composed of:
        * Milliseconds since Gawr Gura debut in binary
            Epoch is on Sep 12th 2020 22:12:32 UTC. - 41 bits
        * Process ID in binary - 17 bits
        * Random number in binary - 5 bits

    :return snowflake_id: A snowflake-like integer. Should have 18 digits or more.
    """
    epoch = datetime.datetime(2020, 9, 12, 22, 12, 32)
    now = datetime.datetime.utcnow()
    ts = format(int((now-epoch).total_seconds()*1000), "b").zfill(42)
    pid = format(int(os.getpid()), "b").zfill(17)
    r = format(random.randint(0, 31), "b").zfill(5)
    snowflake_id = int((ts + pid + r), 2)
    return snowflake_id

import datetime
import os
import random


def OTP_str(length: int = 4) -> str:
    """Generate a string for one-time password usage.

    Args:
        length: The length of the password, defualts to 4.

    Returns:
        A random one-time password string.
    """
    string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    OTP = ""
    for _ in range(length):
        OTP += string[random.randint(0, len(string) - 1)]
    return OTP


def OTP_num(length: int = 4) -> str:
    """Generate a string for one-time password usage.
    But only in numbers.

    Args:
        length: The length of the password, defualts to 4.

    Returns:
        A random one-time password string.
    """
    string = "0123456789"
    OTP = ""
    for _ in range(length):
        OTP += string[random.randint(0, len(string) - 1)]
    return OTP


def snowflake() -> int:
    """Generate a snowflake-like ID.

    The ID is composed of:
        * Milliseconds since Gawr Gura debut in binary
            Epoch is on Sep 12th 2020 22:12:32 UTC. - 41 bits
        * Process ID in binary - 17 bits
        * Random number in binary - 5 bits

    Returns:
        A snowflake-like integer ID. Should have 18 digits or more.
    """
    epoch = datetime.datetime(2020, 9, 12, 22, 12, 32)
    now = datetime.datetime.utcnow()
    ts = int((now - epoch).total_seconds() * 1000)
    pid = os.getpid()
    r = random.randint(0, 31)
    return ts << 22 | pid << 5 | r

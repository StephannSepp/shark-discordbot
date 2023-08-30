from textwrap import wrap

VALID_CHAR = "_AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz-0123456789"


def b64sf_encode(snowflake_id: int):
    """Give a snowflake int and encode it into a modified base64 method."""
    bsfid = format(snowflake_id, "b").zfill(64)
    group = wrap(bsfid, 6)
    return "".join([VALID_CHAR[int(i, 2)] for i in group])


def b64sf_decode(encoded_char: str):
    """Give a encoded snowflake string and decode it back to a snowflake ID."""
    decoded = [format(VALID_CHAR.index(c), "b").zfill(6) for c in encoded_char]
    decoded[-1] = decoded[-1][-4:]
    return int("".join(decoded), 2)

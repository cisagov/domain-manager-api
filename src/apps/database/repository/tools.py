"""
This is the tools file.

Here we have methods to help translate objects in DB/Json.
"""
# Standard Python Libraries
import datetime


def parse_datetime(
    value,
    formats=(
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%f%Z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d",
    ),
):
    """
    Helper function.

    Which when provided with a string in certain
    datetime formats (which optionally can be provided via the
    ``formats`` kwarg defaults to preset generally accepted ISO formats)
    returns a parsed datetime object.

    :param str value: The string containing the datetime information
    :param formats: List of datetime formats to use to parse the specified
    datetime string (optional)
    :type formats: list(str)
    :throws ValueError: If it cannot parse the datetime string given the a/provided formats.
    :rtype: datetime.datetime
    """
    for time_format in formats:
        try:
            value = datetime.datetime.strptime(value, time_format)
            return value.astimezone(datetime.timezone.utc)
        except ValueError:
            pass
    raise ValueError(f"Cannot parse {value} as a datetime.datetime object")

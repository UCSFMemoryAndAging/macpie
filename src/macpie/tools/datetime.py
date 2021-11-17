"""
Utility functions related to dates and times.
"""

import datetime


def current_datetime_str(fmt="%Y%m%d_%H%M%S", ms=False, ms_prefix="_"):
    """Get the current datetime with second precision with default format ``YYYYMMDD_HHMMSS``"""
    dt = datetime.datetime.now()
    dt_str = dt.strftime(fmt)
    if ms:
        dt_str = dt_str + ms_prefix + str(datetime_ms(dt))
    return dt_str


def datetime_ms(dt: datetime.datetime):
    """Return milliseconds of the datetime"""
    return round(dt.microsecond / 1000)

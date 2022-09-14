"""
Utility functions related to dates and times.
"""

import datetime

import pandas as pd


def current_datetime_str(fmt="%Y%m%d_%H%M%S", ms=False, ms_prefix="_"):
    """
    Get the current datetime with second precision with default
    format ``YYYYMMDD_HHMMSS``
    """

    dt = datetime.datetime.now()
    dt_str = dt.strftime(fmt)
    if ms:
        dt_str = dt_str + ms_prefix + str(datetime_ms(dt))
    return dt_str


def datetime_ms(dt: datetime.datetime):
    """Return milliseconds of the datetime"""
    return round(dt.microsecond / 1000)


def reformat_datetime_str(arg, format="%Y-%m-%d", **kwargs):
    """
    Reformat a datetime string into specified format.

    Parameters
    ----------
    arg : str
        String to convert to a datetiime.
    format : str, default is ``%Y-%m-%d``
        Format string (passed to underlying :py:meth:`datetime.date.strftime`
        to generate new formatted datetime string.
    **kwargs
        All keyword arguments are passed through to the underlying
        :func:`pandas.to_datetime` function.

    Returns
    -------
    str
        Reformatted datetime string
    """
    dt = pd.to_datetime(arg, **kwargs)
    if isinstance(dt, (pd.Timestamp, datetime.datetime)) and not pd.isnull(dt):
        return dt.strftime(format)
    return dt

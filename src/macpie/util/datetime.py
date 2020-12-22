import datetime


def append_current_datetime_str(prefix):
    """
    Appends a string representing the current datetime with second
    precision to ``prefix``.
    See :func:`get_current_datetime_str`

    :param prefix: string to append to
    """
    return '_'.join((prefix, get_current_datetime_str()))


def append_current_datetime_ms_str(prefix):
    """
    Appends a string representing the current datetime with ms
    precision to ``prefix``.
    See :func:`get_current_datetime_ms_str`

    :param prefix: string to append to
    """
    return '_'.join((prefix, get_current_datetime_ms_str()))


def get_current_datetime_str():
    """
    Get the current datetime with second precision with format ``YYYYMMDD-HHMMSS``
    """
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


def get_current_datetime_ms_str():
    """
    Get the current datetime with millisecond precision with format ``YYYYMMDD-HH_MM_SS_mmm``
    """
    return datetime.datetime.now().strftime('%Y%m%d_%H_%M_%S_%f')[:-3]

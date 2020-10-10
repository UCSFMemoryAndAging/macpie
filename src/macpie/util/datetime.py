import datetime


def append_current_datetime_str(prefix):
    return '_'.join((prefix, get_current_datetime_str()))


def append_current_datetime_ms_str(prefix):
    return '_'.join((prefix, get_current_datetime_ms_str()))


def get_current_datetime_str():
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


def get_current_datetime_ms_str():
    return datetime.datetime.now().strftime('%Y%m%d_%H_%M_%S_%f')[:-3]

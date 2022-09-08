"""
Misc tools for implementing data structures

Note: macpie.core.common is *not* part of the public API.
"""


def count_not_none(*args) -> int:
    """
    Returns the count of arguments that are not None.

    From: https://github.com/pandas-dev/pandas/blob/9757d1f93faaa517161fd719e884be7344c18b62/pandas/core/common.py#L213-L217
    """
    return sum(x is not None for x in args)


def count_bool_falsey(*args) -> int:
    """
    Returns the count of arguments that are falsey.
    """
    return sum(bool(x) is False for x in args)


def count_bool_true(*args) -> int:
    """
    Returns the count of arguments that are truthy.
    """
    return sum(bool(x) is True for x in args)

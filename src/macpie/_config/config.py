"""
The config module holds package-wide configurables and provides
a uniform API for working with them.

Entire module adapted from the pandas library.
URL: https://github.com/pandas-dev/pandas/blob/b524462e1f88319912ee5ad91a45e6d1986c9dba/pandas/_config/config.py
Date: 2021-03-19
"""

from collections import namedtuple
from typing import Any, Callable, Dict, Optional, Tuple


RegisteredOption = namedtuple("RegisteredOption", "key defval doc validator cb")

# holds registered option metadata
_registered_options: Dict[str, RegisteredOption] = {}

# holds the current values for registered options
_global_config: Dict[str, Any] = {}


class OptionError(AttributeError, KeyError):
    """
    Exception for macpie.options
    """


def register_option(
    key: str,
    defval: object,
    doc: str = "",
    validator: Optional[Callable[[Any], Any]] = None,
    cb: Optional[Callable[[str], Any]] = None,
) -> None:
    """
    Register an option in the package-wide macpie config object
    Parameters
    ----------
    key : str
        Fully-qualified key, e.g. "x.y.option - z".
    defval : object
        Default value of the option.
    doc : str
        Description of the option.
    validator : Callable, optional
        Function of a single argument, should raise `ValueError` if
        called with a value which is not a legal value for the option.
    cb
        a function of a single argument "key", which is called
        immediately after an option value is set/reset. key is
        the full name of the option.
    Raises
    ------
    ValueError if `validator` is specified and `defval` is not a valid value.
    """
    key = key.lower()

    if key in _registered_options:
        raise OptionError(f"Option '{key}' has already been registered")

    default_value = defval() if callable(defval) else defval

    # the default value should be legal
    if validator:
        validator(default_value)

    _global_config[key] = default_value  # initialize

    # save the option metadata
    _registered_options[key] = RegisteredOption(
        key=key, defval=defval, doc=doc, validator=validator, cb=cb
    )


def get_option(key: str):
    """
    Retrieves the value of the specified option. ::

        >>> macpie.get_option("operators.binary.column_suffixes")
        ("_x", "_y")

    """

    key = key.lower()

    if key not in _global_config:
        raise OptionError(f"No such option exists: '{key}'")

    return _global_config[key]


def set_option(key, value) -> None:
    """
    Sets the value of the specified option. ::

        >>> macpie.set_option("operators.binary.column_suffixes", ("_link", "_y"))
        >>> macpie.get_option("operators.binary.column_suffixes")
        ("_link", "_y")

    """

    key = key.lower()

    opt = _get_registered_option(key)

    if opt is None:
        raise OptionError(f"No such option exists: '{key}'")

    if opt.validator:
        opt.validator(value)

    _global_config[key] = value

    if opt.cb:
        opt.cb(key)


def reset_option(key: str) -> None:
    """
    Reset one or more options to their default value. ::

        >>> macpie.reset_option("operators.binary.column_suffixes")

    """

    key = key.lower()

    if key not in _global_config:
        raise OptionError(f"No such option exists: '{key}'")

    defval = _registered_options[key].defval

    set_option(key, defval() if callable(defval) else defval)


def _get_registered_option(key: str):
    """
    Retrieves the option metadata if `key` is a registered option.
    Returns
    -------
    RegisteredOption (namedtuple) if key is deprecated, None otherwise
    """
    return _registered_options.get(key)


def is_tuple_of_str(value: Tuple[str, ...]) -> None:
    """
    Verify that value is tuple of strings.

    Parameters
    ----------
    value : tuple of strings
            The `value` to be checked.

    Raises
    ------
    ValueError
        When the value is not a tuple of strings
    """
    if isinstance(value, tuple):
        for str_value in value:
            if type(str_value) != str:
                raise ValueError("Tuple values must be strings")
        return
    raise ValueError("Value must be a tuple")


def is_tuple_of_two(value: Tuple[str, str]) -> None:
    """
    Verify that value is tuple of 2 strings.

    Parameters
    ----------
    value : tuple of two strings
            The `value` to be checked.

    Raises
    ------
    ValueError
        When the value is not a tuple of 2 strings
    """
    if isinstance(value, tuple):
        if len(value) == 2:
            if type(value[0]) == str and type(value[1] == str):
                return
    raise ValueError("Value must be a tuple of 2 strings.")

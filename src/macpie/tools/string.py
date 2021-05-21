from typing import List


def add_suffix(s: str, suffix: str, max_length: int = -1):
    """Add a suffix to a string, optionally specifying a maximum string length
    and giving priority to the suffix if maximum string length is reached. ::

        >>> add_suffix("testing", "suffix", 7)
        "tsuffix"
        >>> add_suffix("testing", "suffix", 8)
        "tesuffix"
        >>> add_suffix("testing", "suffix", 9)
        "tessuffix"

    :param s: string
    :param suffix: suffix to append to ``s``
    :param max_length: maximum string length of result, giving priority to the suffix
    """
    if max_length > -1:
        if len(suffix) >= max_length:
            raise ValueError("suffix can't be equal to or longer than max_length specified")
        return s[0:max_length - len(suffix)] + suffix
    else:
        return s + suffix


def add_suffixes(s: str, suffixes: List[str], max_length: int = -1):
    """Add a list of suffixes to a string, optionally specifying a maximum string length
    and giving priority to the suffix if maximum string length is reached.

    :param s: string
    :param suffixes: suffixes to append to ``s``
    :param max_length: maximum string length of result, giving priority to the suffix
    """
    if not s:
        return None

    if max_length > -1:
        for suffix in suffixes:
            s = add_suffix(s, suffix, max_length)
        return s
    else:
        return s + ''.join(suffixes)


def add_suffixes_with_base(base, suffixes: List[str] = [], delimiter: str = "_", max_length: int = -1):
    """Adds a list of suffixes to a specified `base` string.

    :param base: Base to add suffixes to
    :param suffixes: List of suffixes to add to `base`
    :param delimiter: Delimiter to use when adding suffixes. Defaults to "_"
    :param max_length: Maximum string length of final result, giving priority to
                       the suffixes. Defaults to -1, meaning no maximum.
    """
    if not suffixes:
        return base[:max_length] if max_length > -1 else base

    result = base

    if max_length > -1:
        max_length = max_length - (len(base) + len(suffixes))

    for suffix in suffixes:
        result = add_suffix(result, delimiter + suffix, max_length)

    return result


def strip_suffix(s: str, suffix: str):
    """Remove a suffix from a string.

    :param s: string
    :param suffix: suffix to remove from ``s``
    """
    if s is not None and s.endswith(suffix):
        return s[:-len(suffix)]
    return s

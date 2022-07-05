import collections
import itertools
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
        return s[0 : max_length - len(suffix)] + suffix
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
        return s + "".join(suffixes)


def add_suffixes_with_base(
    base, suffixes: List[str] = [], delimiter: str = "_", max_length: int = -1
):
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


def make_unique(
    seq,
    suffs_iter=None,
    suffs_prefix="",
    suffs_suffix="",
    skip=0,
    skip_suffix="",
    inplace=False,
):
    """Make sequence of string elements unique by adding a differentiating suffix.

    Parameters
    ----------
    seq : Sequence
        Mutable sequence of strings
    suffs_iter : optional, default is itertools.count(1)
        An alternative iterable of suffixes
    suffs_prefix : optional, default is empty string
        An alternative string to prepend to each suffix in ``suffs_iter``
    suffs_suffix : optional, default is empty string
        An alternative string to append to each suffix in ``suffs_iter``
    skip : optional, default is 0
        How many duplicates to skip before appending suffixes.
    skipped_suffix : optional, default is empty string
        Add this suffix to any skipped duplicates.
    inplace : optional, default is False
        Whether to modify the list in place

    Examples
    --------
    >>> lst = ["name", "state", "name", "city", "name", "zip", "zip"]
    >>> make_unique(lst)
    ["name1", "state", "name2", "city", "name3", "zip1", "zip2"]

    >>> make_unique(lst, skip=1)
    ["name", "state", "name1", "city", "name2", "zip", "zip1"]

    >>> make_unique(lst, suffs_prefix="_")
    ["name_1", "state", "name_2", "city", "name_3", "zip_1", "zip_2"]
    """

    if suffs_iter is None:
        suffs_iter = itertools.count(1)

    def final_suffs_iter():
        for si in suffs_iter:
            yield suffs_prefix + str(si) + suffs_suffix

    final_suffs_iter = itertools.chain(itertools.repeat(skip_suffix, skip), final_suffs_iter())

    if inplace:
        result = seq
    else:
        result = seq.copy()

    not_unique = [k for k, v in collections.Counter(result).items() if v > 1]
    suffix_generator_mapping = dict(
        zip(not_unique, itertools.tee(final_suffs_iter, len(not_unique)))
    )

    for idx, item in enumerate(seq):
        try:
            suffix = next(suffix_generator_mapping[item])
        except KeyError:
            # item was unique
            continue
        else:
            result[idx] = str(result[idx]) + suffix

    if inplace:
        return None
    return result


def seq_contains(s: str, seq, case_sensitive=True):
    """Does sequence contain string."""
    if case_sensitive:
        if s in seq:
            return True
    else:
        seq_casefold = [seq_str.casefold() for seq_str in seq if isinstance(seq_str, str)]
        if s.casefold() in seq_casefold:
            return True
    return False


def str_equals(a: str, b: str, case_sensitive=True):
    """Are strings equal."""
    if case_sensitive:
        return str(a) == str(b)
    else:
        return str(a).casefold() == str(b).casefold()


def str_startswith(s: str, prefix: str, case_sensitive=True):
    """Does string start with a prefix."""
    if case_sensitive:
        return s.startswith(prefix)
    else:
        return s.lower().startswith(prefix.lower())


def strip_suffix(s: str, suffix: str):
    """Remove a suffix from a string.

    :param s: string
    :param suffix: suffix to remove from ``s``
    """
    if s is not None and s.endswith(suffix):
        return s[: -len(suffix)]
    return s

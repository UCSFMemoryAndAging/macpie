def add_suffix(s: str, suffix: str, max_length: int = -1):
    """
    Add a suffix to a string, optionally specifying a maximum string length
    and giving priority to the suffix if maximum string length is reached. ::

        $ assert add_suffix("testing", "suffix", 7) == "tsuffix"
        $ assert add_suffix("testing", "suffix", 8) == "tesuffix"
        $ assert add_suffix("testing", "suffix", 9) == "tessuffix"

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


def strip_suffix(s: str, suffix: str):
    """
    Remove a suffix from a string.

    :param s: string
    :param suffix: suffix to remove from ``s``
    """
    if s is not None and s.endswith(suffix):
        return s[:-len(suffix)]
    return s

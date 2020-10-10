def add_suffix(s: str, suffix: str, max_length: int = -1):
    if max_length > -1:
        if len(suffix) >= max_length:
            raise ValueError("suffix can't be equal to or longer than max_length specified")
        return s[0:max_length - len(suffix)] + suffix
    else:
        return s + suffix


def strip_suffix(s: str, suffix: str):
    if s is not None and s.endswith(suffix):
        return s[:-len(suffix)]
    return s

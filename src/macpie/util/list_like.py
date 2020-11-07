def is_list_like(obj):
    return isinstance(obj, (tuple, list))


def list_like_str_equal(a, b, case_insensitive=False):
    if is_list_like(a) and is_list_like(b):
        if len(a) == len(b):
            if case_insensitive:
                return str(a).lower() == str(b).lower()
            else:
                return str(a) == str(b)


def maybe_make_list(obj):
    if obj is not None and not is_list_like(obj):
        return [obj]
    return obj

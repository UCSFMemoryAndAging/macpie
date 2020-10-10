def is_list_like(obj):
    return isinstance(obj, (tuple, list))


def maybe_make_list(obj):
    if obj is not None and not is_list_like(obj):
        return [obj]
    return obj

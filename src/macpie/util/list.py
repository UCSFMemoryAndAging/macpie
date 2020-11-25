def diff(a, b):
    b = set(b)
    return [item for item in a if item not in b]


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


def move(a, item, item_to_move_to):
    item_idx = a.index(item)
    item_to_move_to_idx = a.index(item_to_move_to)

    if item_idx < item_to_move_to_idx:
        a.insert(item_to_move_to_idx - 1, a.pop(item_idx))
    elif item_idx > item_to_move_to_idx:
        a.insert(item_to_move_to_idx, a.pop(item_idx))

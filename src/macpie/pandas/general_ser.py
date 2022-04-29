import pandas as pd


def remove_trailers(ser: pd.Series, predicate=None, remove_na=True):
    if predicate is None:
        if remove_na is False:
            raise ValueError("A predicate must be specified if 'remove_na' is False.")
        else:
            func = lambda x: pd.isna(x)
    else:
        if remove_na is False:
            func = predicate
        else:
            func = lambda x: pd.isna(x) or predicate(x)

    counter = 0
    for val in reversed(ser.array):
        if func(val):
            counter += 1
        else:
            break

    if counter > 0:
        new_last_index = ser.size - counter
        return ser.iloc[0:new_last_index]

    return ser

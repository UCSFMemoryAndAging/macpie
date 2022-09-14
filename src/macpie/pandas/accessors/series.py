import functools

import pandas as pd

import macpie.pandas as mppd


@pd.api.extensions.register_series_accessor("mac")
class MacSeriesAccessor:
    """
    Custom Series accessor to extend the :class:`pandas.DataSeriesFrame` object.
    This creates an additional namepace on the Series object called ``mac``.

    The majority of methods exposed via this accessor are derived from functions
    already available from the public API. This is essentially syntactic sugar
    for calling those functions (leaving out the first argument, as that is the
    Series object using the accessor).

    Examples
    --------
    >>> import pandas as pd
    >>> import macpie as mp

    >>> ser = pd.Series([1, 2, 3, None, ''])
    >>> ser.mac.rtrim()
    0    1
    1    2
    2    3
    dtype: object
    >>> mp.pandas.rtrim(ser, trim_empty_string=False)
    0    1
    1    2
    2    3
    3    None
    4
    dtype: object
    """

    accessor_api = [
        mppd.count_trailers,
        mppd.remove_trailers,
        mppd.rtrim,
        mppd.rtrim_longest,
    ]

    def __init__(self, ser):
        self._validate(ser)
        self._ser = ser

    @staticmethod
    def _validate(obj):
        pass

    def __getattr__(self, attr):
        try:
            func = next(filter(lambda f: f.__name__ == attr, MacSeriesAccessor.accessor_api))
            return functools.partial(func, self._ser)
        except StopIteration:
            raise AttributeError(
                f"Function not available on this accessor: {self.__class__}.'{attr}'"
            )

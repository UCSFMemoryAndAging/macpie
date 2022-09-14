import functools

import pandas as pd

import macpie.pandas as mppd


@pd.api.extensions.register_dataframe_accessor("mac")
class MacDataFrameAccessor:
    """
    Custom DataFrame accessor to extend the :class:`pandas.DataFrame` object.
    This creates an additional namepace on the DataFrame object called ``mac``.

    The majority of methods exposed via this accessor are derived from functions
    already available from the public API. This is essentially syntactic sugar
    for calling those functions (leaving out the first argument, as that is the
    DataFrame object using the accessor).

    Examples
    --------
    >>> from datetime import datetime
    >>> import pandas as pd
    >>> import macpie as mp

    >>> df = pd.DataFrame({'numeric_col': [1], 'date_col': [datetime(2001, 3, 2)]})
    >>> df.mac.is_date_col('numeric_col')
    False
    >>> df.mac.is_date_col('date_col')
    True
    >>> mp.pandas.is_date_col(df, 'date_col')
    True
    """

    accessor_api = [
        mppd.add_diff_days,
        mppd.any_duplicates,
        mppd.compare,
        mppd.conform,
        mppd.date_proximity,
        mppd.diff_cols,
        mppd.diff_rows,
        mppd.drop_suffix,
        mppd.equals,
        mppd.filter_by_id,
        mppd.filter_labels,
        mppd.filter_labels_pair,
        mppd.flatten_multiindex,
        mppd.get_col_name,
        mppd.get_col_names,
        mppd.get_cols_by_prefixes,
        mppd.group_by_keep_one,
        mppd.insert,
        mppd.is_date_col,
        mppd.mark_duplicates_by_cols,
        mppd.merge,
        mppd.mimic_dtypes,
        mppd.mimic_index_order,
        mppd.prepend_multi_index_level,
        mppd.replace_suffix,
        mppd.sort_values_pair,
        mppd.subset,
        mppd.subset_pair,
        mppd.to_datetime,
    ]

    def __init__(self, df):
        self._validate(df)
        self._df = df

    @staticmethod
    def _validate(obj):
        pass

    def __getattr__(self, attr):
        try:
            func = next(filter(lambda f: f.__name__ == attr, MacDataFrameAccessor.accessor_api))
            return functools.partial(func, self._df)
        except StopIteration:
            raise AttributeError(
                f"Function not available on this accessor: {self.__class__}.'{attr}'"
            )

    def col_count(self):
        return len(self._df.columns)

    def row_count(self):
        return len(self._df.index)

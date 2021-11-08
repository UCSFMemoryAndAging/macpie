"""
Styler functions
"""

import pandas as pd

"""
Style functions to use with the df.style.apply() method.

For reference:

df.style.apply() (column-/row-/table-wise): accepts a function that takes a Series or
DataFrame and returns a Series, DataFrame, or numpy array with an identical
shape where each element is a string with a CSS attribute-value pair.
This method passes each column or row of your DataFrame one-at-a-time or the
entire table at once, depending on the axis keyword argument.
For columnwise use axis=0, rowwise use axis=1, and for the entire table at
once use axis=None.

URL: https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html#Styler-Functions
"""


def highlight_axis_by_predicate(s: pd.Series, index_or_column, predicate, color="yellow"):
    """
    Highlight entire row or column if predicate is true for any one of the
    values in the row or column.

    Parameters
    ----------
    s : Series.
        row or column depending on the axis parameter supplied to style.apply() method
    index_or_column: index or column label value
        index label (if axis=0) or column label (if axis=1)
    predicate: a Boolean-valued function
        Tests the value in `index_or_column`. If True, the entire row (i.e. Series)
        is highlighted
    color : str, default 'yellow'
        Background color to use for highlighting.

    Examples
    --------
    Basic usage
    >>> df = pd.DataFrame({
    ...     "One": [1.2, 1.6, 1.5],
    ...     "Two": [2.9, 2.1, 2.5],
    ...     "Three": [3.1, 3.2, 3.8],
    ... })
    >>> df.style.apply(
            highlight_axis_by_predicate,
            index_or_column="Two",
            predicate=lambda x: x == 2.1,
            axis=1,
        )
    """
    props = f"background-color: {color}"
    if predicate(s[index_or_column]):
        return [props] * len(s)
    else:
        return [""] * len(s)
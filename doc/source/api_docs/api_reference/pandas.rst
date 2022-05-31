Pandas
======

As MACPie relies heavily on the ``pandas`` library, a rich set of methods
that work with :class:`pandas.DataFrame` and :class:`pandas.Series` objects
were created and are provided through this API. These custom methods are
exposed and accessible through the :class:`pandas.DataFrame` and
:class:`pandas.Series` objects themselves via the ``mac`` namespace.
See the corresponding accessor class to see which methods are available
via the ``mac`` namespace.

Example: ::

    >>> from datetime import datetime 
    >>> import pandas as pd
    >>> from macpie import MacDataFrameAccessor

    >>> df = pd.DataFrame({'col1': [1,2], 'date1': [datetime(2001, 3, 2), datetime(2001, 8, 1)]})
    >>> df.mac.is_date_col('col1')
    False
    >>> df.mac.is_date_col('date1')
    True

DataFrame Accessor
~~~~~~~~~~~~~~~~~~

Methods on this accessor class are available on :class:`pandas.DataFrame`
objects via the ``mac`` namespace.

.. currentmodule:: macpie
.. autosummary::
   :toctree: api/

   MacDataFrameAccessor


Series Accessor
~~~~~~~~~~~~~~~

Methods on this accessor class are available on :class:`pandas.Series`
objects via the ``mac`` namespace.


.. currentmodule:: macpie
.. autosummary::
   :toctree: api/

   MacSeriesAccessor


.. currentmodule:: macpie.pandas

Core Functions
~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   date_proximity
   filter_by_id
   group_by_keep_one
   merge


I/O Functions
~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   csv_to_dataframe
   excel_to_dataframe
   file_to_dataframe


DataFrame Helper Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   add_diff_days
   any_duplicates
   assimilate
   diff_cols
   diff_rows
   drop_cols
   drop_suffix
   equals
   flatten_multiindex
   get_col_name
   get_col_names
   get_cols_by_prefixes
   insert
   is_date_col
   mark_duplicates_by_cols
   replace_suffix
   to_datetime


Series Helper Functions
~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   count_trailers
   remove_trailers
   rtrim
   rtrim_longest

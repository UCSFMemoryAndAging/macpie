Pandas
======

As MACPie relies heavily on the ``pandas`` library, a rich set of methods
that work with :class:`pandas.DataFrame` and :class:`pandas.Series` objects
were created and are provided through this API. These custom methods are
exposed and accessible through the :class:`pandas.DataFrame` and
:class:`pandas.Series` objects themselves via an extension.

DataFrame Accessor
~~~~~~~~~~~~~~~~~~

Pandas allows extensions of its :class:`pandas.DataFrame` class using custom accessors.
To create a custom accessor with its own "namespace," a class is decorated with the
:meth:`pandas.api.extensions.register_dataframe_accessor` decorator and provides the name
of the namespace attribute.

MACPie creates a namespace called ``mac``, which can then be accessed
via dot notation. Example: ::

    >>> from datetime import datetime 
    >>> import pandas as pd
    >>> from macpie import MacDataFrameAccessor

    >>> df = pd.DataFrame({'col1': [1,2], 'date1': [datetime(2001, 3, 2), datetime(2001, 8, 1)]})
    >>> df.mac.is_date_col('col1')
    False
    >>> df.mac.is_date_col('date1')
    True

.. currentmodule:: macpie
.. autosummary::
   :toctree: api/

   MacDataFrameAccessor


Series Accessor
~~~~~~~~~~~~~~~

Extension of the :class:`pandas.Series` class.

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


Helper Functions
~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   add_diff_days
   any_duplicates
   assimilate
   diff_cols
   diff_rows
   drop_suffix
   equals
   flatten_multiindex
   get_col_name
   get_col_names
   insert
   is_date_col
   mark_duplicates_by_cols
   replace_suffix
   to_datetime

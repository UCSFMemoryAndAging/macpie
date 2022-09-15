Pandas
======

As MACPie relies heavily on the ``pandas`` library, a rich set of functions
that work with :class:`pandas.DataFrame` and :class:`pandas.Series` objects
were created and are provided through this API.


.. currentmodule:: macpie.pandas

I/O Functions
~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   read_csv
   read_excel
   read_file


Selecting data
~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   filter_by_id
   filter_labels
   filter_labels_pair
   get_col_name
   get_col_names
   get_cols_by_prefixes
   remove_trailers
   rtrim
   rtrim_longest
   subset
   subset_pair


Indexing
~~~~~~~~

.. autosummary::
   :toctree: api/

   drop_suffix
   flatten_multiindex
   insert
   prepend_multi_index_level
   replace_suffix


Describing data
~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   add_diff_days
   any_duplicates
   count_trailers
   is_date_col
   mark_duplicates_by_cols


Combining data
~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   date_proximity
   merge


Comparing data
~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   compare
   diff_cols
   diff_rows
   equals


Converting data
~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   conform
   mimic_dtypes
   mimic_index_order
   to_datetime


Group by
~~~~~~~~

.. autosummary::
   :toctree: api/

   group_by_keep_one


Sorting Data
~~~~~~~~~~~~

.. autosummary::
   :toctree: api/

   sort_values_pair


.. currentmodule:: macpie

Accessors
~~~~~~~~~

Pandas allows adding additional "namespaces" to pandas objects to extend them.
MACPie adds the ``mac`` namespace to :class:`pandas.DataFrame` and
:class:`pandas.Series` objects to provide access to many of these methods and more.

See the corresponding accessor classes to see which methods are available
via the ``mac`` namespace.

DataFrame Accessor
^^^^^^^^^^^^^^^^^^

Methods on this accessor class are available on :class:`pandas.DataFrame`
objects via the ``mac`` namespace.

.. autosummary::
   :toctree: api/

   MacDataFrameAccessor

Series Accessor
^^^^^^^^^^^^^^^

Methods on this accessor class are available on :class:`pandas.Series`
objects via the ``mac`` namespace.

.. autosummary::
   :toctree: api/

   MacSeriesAccessor

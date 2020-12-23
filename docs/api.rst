API Reference
=============

This part of the documentation contains a detailed description of the MACPie API.
This reference describes how the classes and methods work and which parameters can be used.


DataObject Class
----------------

.. autoclass:: macpie.core.DataObject
   :members:


Query Class
-----------

.. autoclass:: macpie.core.Query
   :members:


Core Functions
--------------

.. autofunction:: macpie.pandas.date_proximity

.. autofunction:: macpie.pandas.filter_by_id

.. autofunction:: macpie.pandas.group_by_keep_one

.. autofunction:: macpie.pandas.merge


Pandas DataFrame Extension
--------------------------

Pandas allows extensions of its :class:`pandas.DataFrame` class using custom accessors.
To create a custom accessor with its own "namespace," a class is decorated with the
:meth:`pandas.api.extensions.register_dataframe_accessor` decorator and provides the name
of the namespace attribute.

MACPie creates a namespace called ``mac``, which can then be accessed
via dot notation. Example: ::

    $ from macpie.pandas import MacDataFrameAccessor
    $ df = pd.DataFrame({'col1': [1,2], 'date1': [datetime(2001, 3, 2), datetime(2001, 8, 1)]})
    $ df.mac.is_date_col('col1')
    False
    $ df.mac.is_date_col('date1')
    True


.. autoclass:: macpie.pandas.MacDataFrameAccessor
   :members:


Pandas Functions
----------------

.. autofunction:: macpie.pandas.add_diff_days

.. autofunction:: macpie.pandas.any_duplicates

.. autofunction:: macpie.pandas.assimilate

.. autofunction:: macpie.pandas.diff_cols

.. autofunction:: macpie.pandas.diff_rows

.. autofunction:: macpie.pandas.drop_suffix

.. autofunction:: macpie.pandas.flatten_multiindex

.. autofunction:: macpie.pandas.get_col_name

.. autofunction:: macpie.pandas.get_col_names

.. autofunction:: macpie.pandas.is_date_col

.. autofunction:: macpie.pandas.json_dumps_contents

.. autofunction:: macpie.pandas.json_loads_contents

.. autofunction:: macpie.pandas.mark_duplicates_by_cols

.. autofunction:: macpie.pandas.num_rows

.. autofunction:: macpie.pandas.num_cols

.. autofunction:: macpie.pandas.replace_suffix

.. autofunction:: macpie.pandas.to_datetime


I/O Functions
-------------

.. autofunction:: macpie.io.get_files_from_dir

.. autofunction:: macpie.io.validate_filepath

.. autofunction:: macpie.io.validate_filepaths


Utility Functions
-----------------

.. autofunction:: macpie.util.datetime.append_current_datetime_str

.. autofunction:: macpie.util.datetime.append_current_datetime_ms_str

.. autofunction:: macpie.util.datetime.get_current_datetime_str

.. autofunction:: macpie.util.datetime.get_current_datetime_ms_str

.. autofunction:: macpie.util.list.diff

.. autofunction:: macpie.util.list.is_list_like

.. autofunction:: macpie.util.list.list_like_str_equal

.. autofunction:: macpie.util.list.maybe_make_list

.. autofunction:: macpie.util.list.move

.. autofunction:: macpie.util.pyxl.get_row_by_col_val

.. autofunction:: macpie.util.pyxl.move_sheets

.. autofunction:: macpie.util.pyxl.ws_autoadjust_colwidth

.. autofunction:: macpie.util.pyxl.ws_get_col

.. autofunction:: macpie.util.pyxl.ws_highlight_row

.. autofunction:: macpie.util.pyxl.ws_highlight_rows_with_col

.. autofunction:: macpie.util.string.add_suffix

.. autofunction:: macpie.util.string.strip_suffix

.. autofunction:: macpie.util.testing.assert_dfs_equal

.. autofunction:: macpie.util.testing.assert_excels_equal

.. autofunction:: macpie.util.validators.validate_bool_kwarg


Utility Objects
---------------

.. autoclass:: macpie.core.Datasheet
   :members:

.. autoclass:: macpie.core.Databook
   :members:


Exceptions
----------

.. automodule:: macpie.errors
   :members:
   
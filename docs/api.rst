API Reference
=============

This part of the documentation contains a detailed description of the MACPie API.
This reference describes how the classes and methods work and which parameters can be used.


Dataset Class
-------------

.. autoclass:: macpie.Dataset
    :members:


.. _api-collections-classes:

Collections Classes
-------------------

Various container datatypes for :class:`macpie.Dataset` objects.

Abstract Base Class
~~~~~~~~~~~~~~~~~~~

.. autoclass:: macpie.collections.base.BaseCollection
    :members:

Concrete Classes
~~~~~~~~~~~~~~~~

.. autoclass:: macpie.BasicList
    :members:
    :inherited-members:

.. autoclass:: macpie.AnchoredList
    :members:
    :inherited-members:

.. autoclass:: macpie.MergeableAnchoredList
    :members:
    :inherited-members:

.. autoclass:: macpie.BasicGraph
    :members:
    :inherited-members:

.. autoclass:: macpie.ExecutableGraph
    :members:
    :inherited-members:


Core Data Analysis Functions
----------------------------

.. autofunction:: macpie.date_proximity

.. autofunction:: macpie.group_by_keep_one


Pandas
------

As MACPie relies heavily on the ``pandas`` library, a rich set of methods
that work with :class:`pandas.DataFrame` objects were created and are
provided through this API. These custom methods are exposed and accessible
through the :class:`pandas.DataFrame` objects themselves via an extension.

Pandas DataFrame Extension
~~~~~~~~~~~~~~~~~~~~~~~~~~

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

.. autoclass:: macpie.MacDataFrameAccessor
   :members:


Pandas Core Functions
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: macpie.pandas.date_proximity

.. autofunction:: macpie.pandas.filter_by_id

.. autofunction:: macpie.pandas.group_by_keep_one

.. autofunction:: macpie.pandas.merge


Pandas I/O Functions
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: macpie.pandas.csv_to_dataframe

.. autofunction:: macpie.pandas.excel_to_dataframe

.. autofunction:: macpie.pandas.file_to_dataframe


Pandas Helper Functions
~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: macpie.pandas.add_diff_days

.. autofunction:: macpie.pandas.any_duplicates

.. autofunction:: macpie.pandas.assimilate

.. autofunction:: macpie.pandas.diff_cols

.. autofunction:: macpie.pandas.diff_rows

.. autofunction:: macpie.pandas.drop_suffix

.. autofunction:: macpie.pandas.equals

.. autofunction:: macpie.pandas.flatten_multiindex

.. autofunction:: macpie.pandas.get_col_name

.. autofunction:: macpie.pandas.get_col_names

.. autofunction:: macpie.pandas.insert

.. autofunction:: macpie.pandas.is_date_col

.. autofunction:: macpie.pandas.json_dumps_contents

.. autofunction:: macpie.pandas.json_loads_contents

.. autofunction:: macpie.pandas.mark_duplicates_by_cols

.. autofunction:: macpie.pandas.num_rows

.. autofunction:: macpie.pandas.num_cols

.. autofunction:: macpie.pandas.replace_suffix

.. autofunction:: macpie.pandas.to_datetime


.. _api-tools:

General Programming Tools
-------------------------

MACPie aims to standardize a set of Python tools useful for programmers at the MAC
in particular, and the data science community in general. The tools are divided into
the following various modules:

Date/Time Tools
~~~~~~~~~~~~~~~

.. autofunction:: macpie.datetimetools.append_current_datetime_str

.. autofunction:: macpie.datetimetools.append_current_datetime_ms_str

.. autofunction:: macpie.datetimetools.get_current_datetime_str

.. autofunction:: macpie.datetimetools.get_current_datetime_ms_str

Excel Tools
~~~~~~~~~~~

.. autofunction:: macpie.exceltools.keep_ws

.. autofunction:: macpie.exceltools.move_ws_before_sheetname

I/O Tools
~~~~~~~~~

.. autofunction:: macpie.iotools.copy_file

.. autofunction:: macpie.iotools.has_csv_extension

.. autofunction:: macpie.iotools.has_excel_extension

`OpenPyXL <https://openpyxl.readthedocs.io/en/stable/>`_ Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: macpie.openpyxltools.ws_autoadjust_colwidth

.. autofunction:: macpie.openpyxltools.ws_get_col

.. autofunction:: macpie.openpyxltools.ws_get_row_by_col_val

.. autofunction:: macpie.openpyxltools.ws_highlight_row

.. autofunction:: macpie.openpyxltools.ws_highlight_rows_with_col

.. autofunction:: macpie.openpyxltools.ws_is_row_empty

.. autofunction:: macpie.openpyxltools.wb_move_sheets

.. autofunction:: macpie.openpyxltools.ws_to_df


`Pandas <http://pandas.pydata.org/pandas-docs/stable/>`_ Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: macpie.pandastools.is_potential_multi_index

.. autofunction:: macpie.pandastools.maybe_make_multi_index_columns


:class:`pathlib.Path` Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: macpie.pathtools.create_output_dir

.. autofunction:: macpie.pathtools.get_files_from_dir

.. autofunction:: macpie.pathtools.validate_filepath

.. autofunction:: macpie.pathtools.validate_filepaths

Sequence Tools
~~~~~~~~~~~~~~

Tools related to Python :class:`list`, :class:`tuple`, and :class:`set`.

.. autofunction:: macpie.seqtools.chunks

.. autofunction:: macpie.seqtools.diff

.. autofunction:: macpie.seqtools.is_list_like

.. autofunction:: macpie.seqtools.list_like_str_equal

.. autofunction:: macpie.seqtools.maybe_make_list

.. autofunction:: macpie.seqtools.move

:class:`str` Tools
~~~~~~~~~~~~~~~~~~

.. autofunction:: macpie.strtools.add_suffix

.. autofunction:: macpie.strtools.add_suffixes

.. autofunction:: macpie.strtools.add_suffixes_with_base

.. autofunction:: macpie.strtools.strip_suffix


.. _api-tools-tablib:

`Tablib <https://tablib.readthedocs.io/en/stable/>`_ Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tablib is an format-agnostic tabular dataset library.
It allows you to import, export, and manipulate tabular data sets.
Advanced features include segregation, dynamic columns, tags & filtering,
and seamless format import & export.

.. autoclass:: macpie.tablibtools.TablibWrapper
    :members:

.. autofunction:: macpie.tablibtools.append_with_tags

.. autofunction:: macpie.tablibtools.excel_to_tablib

Validation Tools
~~~~~~~~~~~~~~~~

.. autofunction:: macpie.validatortools.validate_bool_kwarg


.. _api-utilities:

Utilities
---------

.. autoclass:: macpie.util.DatasetFields
   :members:

.. autoclass:: macpie.util.Info
   :members:

.. autoclass:: macpie.util.TrackHistory
   :members:


.. _api-options:

Working with Options
--------------------

MACPie has an options system that lets you customize some aspects of its behaviour and output.

Options have a "dotted-style", case-insensitive name (e.g. ``display.max_rows``).

The API is composed of 3 relevant functions, available directly from the ``macpie`` namespace:

.. autofunction:: macpie.reset_option

.. autofunction:: macpie.get_option

.. autofunction:: macpie.set_option

Available Options
~~~~~~~~~~~~~~~~~

======================================= ============ ==================================
Option                                  Default      Function
======================================= ============ ==================================
dataset.id_col                          "InstrID"    Default column name (case-sensitive)
                                                     for the ``id_col`` value of a :class:`macpie.Dataset`.
dataset.date_col                        "DCDate"     Default column name (case-sensitive)
                                                     for the ``date_col`` value of a :class:`macpie.Dataset`.
dataset.id2_col                         "PIDN"       Default column name (case-sensitive)
                                                     for the ``id2_col`` value of a :class:`macpie.Dataset`.
column.system.prefix                    "_mp"        Column prefix for :class:`macpie.Dataset` columns
                                                     generated by MACPie.
operators.binary.column_suffixes        "_x", "_y"   For binary operators, suffix to add
                                                     to left and right :class:`macpie.Dataset` columns,
                                                     if applicable.
======================================= ============ ==================================


Testing
----------

.. automodule:: macpie.testing
   :members:


Exceptions
----------

.. automodule:: macpie.exceptions
   :members:
   
Tools
=====

MACPie aims to standardize a set of Python tools useful for programmers at the MAC
in particular, and the data science community in general. The tools are divided into
the following various modules:


datetimetools
-------------
.. automodule:: macpie.datetimetools
   :noindex:

.. autosummary::
   :toctree: api/
   
   current_datetime_str
   datetime_ms
   reformat_datetime_str


itertools
---------
.. automodule:: macpie.itertools
   :noindex:

.. autosummary::
   :toctree: api/
   
   duplicate_indices
   filter_get_index
   filter_get_message
   first_true
   overlay


lltools
-------
.. automodule:: macpie.lltools
   :noindex:

.. autosummary::
   :toctree: api/

   chunks
   common_members
   difference
   filter_seq
   filter_seq_pair
   is_disjoint
   is_list_like
   list_like_str_equal
   make_list_if_list_like
   make_same_length
   make_tuple_if_list_like
   maybe_make_list
   maybe_make_tuple
   move_item_to
   remove_duplicates
   rtrim
   rtrim_longest


openpyxltools
-------------
.. automodule:: macpie.openpyxltools
   :noindex:

.. autosummary::
   :toctree: api/

   autofit_column_width
   file_to_dataframe
   get_column_index
   get_sheet_names
   highlight_row
   is_row_empty
   iter_rows_with_column_value
   to_tablib_dataset
   worksheet_to_dataframe


pathtools
---------
.. automodule:: macpie.pathtools
   :noindex:

.. autosummary::
   :toctree: api/

   create_dir_with_datetime
   create_subdir
   get_files_from_dir
   has_csv_extension
   has_excel_extension
   validate_paths


shelltools
----------
.. automodule:: macpie.shelltools
   :noindex:

.. autosummary::
   :toctree: api/

   copy_file_same_dir


strtools
--------
.. automodule:: macpie.strtools
   :noindex:

.. autosummary::
   :toctree: api/

   add_suffix
   add_suffixes
   add_suffixes_with_base
   make_unique
   seq_contains
   str_equals
   str_startswith
   strip_suffix


.. _api-tools-tablibtools:

tablibtools
-----------
.. automodule:: macpie.tablibtools
   :noindex:

.. autosummary::
   :toctree: api/

   MacpieTablibDataset
   DictLikeTablibDataset
   read_excel


validatortools
--------------
.. automodule:: macpie.validatortools
   :noindex:

.. autosummary::
   :toctree: api/

   validate_bool_kwarg


xlsxwritertools
---------------
.. automodule:: macpie.xlsxwritertools
   :noindex:

.. autosummary::
   :toctree: api/

   tlset_sheet
   XlsxWriterAutofitColumnsWorksheet

Tools
=====

MACPie aims to standardize a set of Python tools useful for programmers at the MAC
in particular, and the data science community in general. The tools are divided into
the following various modules:


datetimetools
-------------
.. module:: macpie.datetimetools

.. automodule:: macpie.datetimetools
   :noindex:

.. autosummary::
   :toctree: api/
   :recursive:

   current_datetime_str
   datetime_ms


itertools
---------
.. module:: macpie.itertools

.. automodule:: macpie.itertools
   :noindex:

.. autosummary::
   :toctree: api/
   
   duplicate_indices
   filter_get_index
   filter_get_message
   overlay
   remove_duplicates


lltools
-------
.. module:: macpie.lltools

.. automodule:: macpie.lltools
   :noindex:

.. autosummary::
   :toctree: api/

   chunks
   common_members
   diff
   is_disjoint
   is_list_like
   list_like_str_equal
   make_list_if_list_like
   make_tuple_if_list_like
   maybe_make_list
   maybe_make_tuple
   move_item_to
   rtrim
   rtrim_longest


openpyxltools
-------------
.. module:: macpie.openpyxltools

.. automodule:: macpie.openpyxltools
   :noindex:

.. autosummary::
   :toctree: api/

   autofit_column_width
   get_column_index
   highlight_row
   is_row_empty
   iter_rows_with_column_value
   to_df
   to_tablib_dataset


pathtools
---------
.. module:: macpie.pathtools

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
.. module:: macpie.shelltools

.. automodule:: macpie.shelltools
   :noindex:

.. autosummary::
   :toctree: api/

   copy_file


strtools
--------
.. module:: macpie.strtools

.. automodule:: macpie.strtools
   :noindex:

.. autosummary::
   :toctree: api/

   add_suffix
   add_suffixes
   add_suffixes_with_base
   str_equals
   strip_suffix


.. _api-tools-tablibtools:

tablibtools
-----------
.. module:: macpie.tablibtools

.. automodule:: macpie.tablibtools
   :noindex:

.. autosummary::
   :toctree: api/

   DictLikeDataset
   TablibDataset
   read_excel


validatortools
--------------
.. module:: macpie.validatortools

.. automodule:: macpie.validatortools
   :noindex:

.. autosummary::
   :toctree: api/

   validate_bool_kwarg


xlsxwritertools
---------------
.. module:: macpie.xlsxwritertools

.. automodule:: macpie.xlsxwritertools
   :noindex:

.. autosummary::
   :toctree: api/

   tlset_sheet
   XlsxWriterAutofitColumnsWorksheet

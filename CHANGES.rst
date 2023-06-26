.. currentmodule:: macpie

.. Use these change groups:
   Added - for new features.
   Changed - for changes in existing functionality.
   Deprecated - for soon-to-be removed features.
   Removed - for now removed features.
   Fixed - for any bug fixes.
   Security - in case of vulnerabilities.


Release notes
=============


0.7 (2023-06-26)
----------------

Changed
~~~~~~~
- :class:`AnchoredList` to allow duplicates in primary Dataset

Other
~~~~~
- Drop support for Python 3.8
- Add support for Python 3.11


0.6 (2023-05-17)
----------------

Added
~~~~~

- CLI

  - :ref:`mppair <command-mppair>` command line tool for utilities related to
    working with pairs of files (e.g. comparing files)
  - ``macpie envfile`` command to create dotenv file template in your home directory

- Pandas

  - :func:`pandas.conform`
  - :func:`pandas.filter_labels`
  - :func:`pandas.filter_labels_pair`
  - :func:`pandas.mimic_dtypes`
  - :func:`pandas.mimic_index_order`
  - :func:`pandas.sort_values_pair`
  - :func:`pandas.subset`
  - :func:`pandas.subset_pair`

- Tools

  - :func:`lltools.remove_duplicates`
  - :func:`shelltools.copy_file_same_dir`
  - :func:`strtools.make_unique`

Changed
~~~~~~~
- Refactored :ref:`Masker <util-masker>` classes


0.5 (2022-06-04)
----------------

Added
~~~~~

- Input / Output

  - :attr:`MACPieXlsxWriterWorkbook.strip_carriage_return` to strip '``\r``'
    characters before writing file

- Pandas Functions

  - :func:`pandas.count_trailers`
  - :func:`pandas.rtrim`
  - :func:`pandas.rtrim_longest`

- Tools

  - :func:`datetimetools.reformat_datetime_str`
  - :func:`itertools.first_true`
  - :func:`lltools.make_same_length`
  - :func:`strtools.seq_contains`

- Utilities

  - :class:`util.DataTable` class to represent a table of data using a list of lists data structure


0.4 (2022-05-10)
----------------

Added
~~~~~
- :ref:`mpsql <command-mpsql>` command line tool for utilities related to sql
  databases (e.g. generate create statements for tables and stored procs)
- :class:`MacSeriesAccessor` to extend :class:`pandas.Series` functionality
- :external+xlsxwriter:doc:`xlsxwriter <index>` excel writing engine
  support for much improved writing performance
- :ref:`Masker <util-masker>` classes for masking data

Changed
~~~~~~~
- Refactored :class:`Dataset` class to use inheritance (from :class:`pandas.DataFrame`)
  rather than composition

Other
~~~~~
- Drop support for Python 3.6, 3.7
- Add support for Python 3.10


0.3 (2021-05-24)
----------------

Added
~~~~~
- Core :class:`Dataset` class
- :class:`DatasetFields` class
- :doc:`Collections <api_docs/api_reference/collections>` classes
  
  - :class:`BasicList`
  - :class:`AnchoredList`
  - :class:`MergeableAnchoredList`

- :doc:`Tools <api_docs/api_reference/tools>`

  - :ref:`tablibtools <api-tools-tablibtools>`

- :doc:`Utilities <api_docs/api_reference/util>`

  - :class:`util.TrackHistory`

- :doc:`Options <api_docs/api_reference/options>` system

Changed
~~~~~~~
- Breaking changes almost everywhere

Other
~~~~~
- Drop support for Python 3.6


0.2 (2020-12-23)
-----------------

- First public preview release.
- Add :ref:`merge <command-merge>` command


0.1 (2020-10-10)
-----------------

- First release for demo purposes.
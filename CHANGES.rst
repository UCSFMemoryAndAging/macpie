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

0.4 (2022-05-10)
----------------

Added
~~~~~
- :ref:`mpsql <command-mpsql>` command line tool for utilities related to sql
  databases (e.g. generate create statements for tables and stored procs)
- :ref:`mpfile <command-mpfile>` command line tool for utilities related to files
  (e.g. comparing files)
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
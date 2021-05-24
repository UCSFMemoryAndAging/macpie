.. currentmodule:: macpie

.. Use these change groups:
   Added - for new features.
   Changed - for changes in existing functionality.
   Deprecated - for soon-to-be removed features.
   Removed - for now removed features.
   Fixed - for any bug fixes.
   Security - in case of vulnerabilities.


0.3 (2021-05-24)
----------------

Added
~~~~~
- Core :class:`Dataset` class
- :ref:`Collections <api-collections-classes>` classes
  
  - :class:`BasicList`
  - :class:`AnchoredList`
  - :class:`MergeableAnchoredList`
  - :class:`BasicGraph`
  - :class:`ExecutableGraph`

- :ref:`Tools <api-tools>`

  - :ref:`Tablib <api-tools-tablib>`

- :ref:`Utilities <api-utilities>`

  - :class:`util.DatasetFields`
  - :class:`util.Info`
  - :class:`util.TrackHistory`

- :ref:`Options <api-options>` system

Changed
~~~~~~~
- Breaking changes almost everywhere

Other
~~~~~
- Drop support for Python 3.6
- Bumped pandas 1.1.5 -> 1.2.3
- Bumped pytest 6.2.1 -> 6.2.2
- Bumped openpyxl 3.0.5 -> 3.0.6
- Bumped sphinx 3.4.0 -> 3.5.2
- Bumped tox 3.20.1 -> 3.23.0


0.2 (2020-12-23)
-----------------

- First public preview release.
- Add :ref:`merge <command-merge>` command


0.1 (2020-10-10)
-----------------

- First release for demo purposes.

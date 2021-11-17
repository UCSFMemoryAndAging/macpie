.. _command-link:


macpie link
-----------

This command links data across multiple datasets using a specified timepoint anchor and time range.

Specifically, a single ``PRIMARY`` dataset contains the timepoint anchor (the :option:`macpie --date-col` column).
Then, one or more ``SECONDARY`` datasets is linked by retrieving all rows that match on the
``PRIMARY`` dataset's :option:`macpie --id2-col` field and whose :option:`macpie --date-col` fields are within a certain
time range of each other.

Usage
~~~~~
.. code-block:: bash

    $ macpie link [OPTIONS] PRIMARY [SECONDARY]

Options
~~~~~~~

.. option:: -k <STRING>, --primary-keep=<STRING> (all|earliest|latest)

   Specify which rows of the ``PRIMARY`` file to keep. These rows will serve as the timepoint anchor.

    - ``all`` (`default`): keep all rows
    - ``earliest``: for each group of unique :option:`macpie --id2-col` values, keep the earliest row,
      as determined by the :option:`macpie --date-col` values
    - ``latest``: for each group of unique :option:`macpie --id2-col` value, keep the latest row,
      as determined by the :option:`macpie --date-col` values

.. option:: -g <STRING>, --secondary-get=<STRING> (all|closest)

   Specify which rows of the ``[SECONDARY]`` file(s) to get:

    - ``all`` (`default`): get all rows that are within :option:`--secondary-days` days of the
      corresponding ``PRIMARY`` timepoint anchor
    - ``closest``: get only the closest row that is within :option:`--secondary-days` days of the
      corresponding ``PRIMARY`` timepoint anchor

.. option:: -t <INTEGER>, --secondary-days=<INTEGER>

   ``Default=90``. Specify the time range measured in days.

.. option:: -w <STRING>, --secondary-when=<STRING> (earlier|later|earlier_or_later)

   Specify which rows of the ``[SECONDARY]`` file(s) to get:

   - ``earlier``: get only rows that are earlier than the timepoint anchor
   - ``later``: get only rows that are later (more recent) than the timepoint anchor
   - ``earlier_or_later`` (`default`): get rows that are earlier or later (more recent)
     than the timepoint anchor

.. option:: -i <STRING>, --secondary-id-col=<STRING>

   Default = :option:`macpie --id-col` value. Secondary ID column header. The column header of the secondary ID column,
   if different from the primary ID column.

.. option:: -d <STRING>, --secondary-date-col=<STRING>

   Default = :option:`macpie --date-col` value. Secondary Date column header. The column header of the secondary date column,
   if different from the primary Date column.

.. option:: -j <STRING>, --secondary-id2-col=<STRING>

   Default = :option:`macpie --id2-col` value. Secondary ID2 column header. The column header of the secondary ID2 column,
   if different from the primary ID2 column.

.. option:: --merge-results/--no-merge-results

   ``Default=--merge-results``. Whether the linked results should be merged into one dataset. Otherwise, the linked
   datasets will remain in their worksheets.

.. option:: --help

    Show a short summary of the usage and options.
   

Arguments
~~~~~~~~~

.. option:: PRIMARY 

   *Required*. Filename of the primary dataset. One and only one must be specified.
    

.. option:: SECONDARY

   *Optional*. Filenames of the secondary dataset(s), delimited by a space. An unlimited
   number of files can be specified.
    


Output
~~~~~~

In the results file, the primary dataset will have the suffix ``_anchor``, and every linked
secondary dataset will have the suffix ``_linked``.

**IMPORTANT NOTE REGARDING DUPLICATES**: Each secondary dataset result will have an extra column
``_duplicates`` indicating whether that row is part of a duplicate set of rows (i.e. ``True`` if it is
a duplicate, ``False`` otherwise); that row will also be highlighted yellow. It is up to you to
remove any duplicates and keep the single record you consider the most valid or most useful to your dataset.

Duplicates can occur if more than one secondary record was found satisfying the time range criteria.
Some common conditions producing duplicates include:

    * A patient completes the same assessment on the same day but for two different
      projects; since there are two assessments completed on the same day, both are valid
      as being the *closest* to the primary timepoint anchor date.
    * If the criteria is to find *all* records within 90 days of the timepoint anchor, it
      is possible that a patient completed two or more assessments within 90 days of each other
    * If a patient cancels a visits and comes in for a visit a few days later, the data entry staffer
      may have forgotten to remove the assessment that were automatically created as part of the
      cancelled visit.

A good way to know whether you are ready to combine your datasets into a single dataset is if each secondary
dataset has the *same number of rows* as the primary anchor.


.. _examples-link:

Examples
~~~~~~~~
#. For every row in ``cdr.csv``, find all the records in ``faq.csv`` that match on the ``PIDN``
   field and whose ``DCDate`` is within 90 days of each other. ::

      $ macpie link cdr.csv faq.csv

   This is equivalent to the two commands below, with the defaults specified instead of implied.
   
   The first command uses the longer double-dash option names syntax for clairty. ::

      $ macpie --id-col=InstrID --date-col=DCDate --id2-col=PIDN link --keep=all --secondary-get=all --secondary-days=90 --secondary-when=earlier_or_later cdr.csv faq.csv

   The second command uses the shorter single-dash option names for brevity. ::

      $ macpie -i InstrID -d DCDate -j PIDN link -k all -g all -d 90 -w earlier_or_later cdr.csv faq.csv

#. Similar to above but uses a combination of defaults and option specifications.
   In this example, we are finding the records in ``faq.csv`` that match on the
   ``PIDN`` field and whose ``DCDate`` is the closest one within 60 days of and earlier than the ``DCDate``
   in ``cdr.csv`` ::

    $ macpie link -g closest -d 60 -w earlier cdr.csv faq.csv


API
~~~

.. click:: macpie.cli.macpie.link:link
   :prog: macpie link
   :nested: full

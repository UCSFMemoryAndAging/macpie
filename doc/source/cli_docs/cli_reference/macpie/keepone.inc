.. _command-keepone:

macpie keepone
--------------

This command groups rows that have the same :option:`macpie --id2-col` value, and allows you to keep
only the earliest or latest row in each group as determined by the :option:`macpie --date-col` values
(discarding the other rows in the group).


Usage
~~~~~
.. code-block:: bash

    $ macpie keepone [OPTIONS] [PRIMARY]


Options
~~~~~~~

.. option:: -k <STRING>, --keep=<STRING> (all|earliest|latest)

   Specify which rows of the ``PRIMARY`` file to keep.

   - ``all`` (`default`): keep all rows
   - ``earliest``: for each unique value in the column specified by the :option:`macpie --id2-col` option, keep only the earliest row (determined by the values in the :option:`macpie --date-col` column)
   - ``latest``: for each unique value in the column specified by the :option:`macpie --id2-col` option, keep only the latest row (determined by the values in the :option:`macpie --date-col` column)

Arguments
~~~~~~~~~

.. option:: PRIMARY

   *Required*. A list of filenames and/or directories.

Output
~~~~~~

The results of each dataset will be stored in a corresponding worksheet inside the results file.


.. _examples-keepone:

Examples
~~~~~~~~

#. For each ``PIDN``, keep only the earliest CDR record as determined by its ``DCDate``. ::

      $ macpie keepone --keep=earliest cdr.csv

   Equivalent command but using shorter single-dash option names for brevity::

      $ macpie keepone -k earliest cdr.csv

#. For each ``VID`` (a column containing Visit IDs), keep the latest record
   as determined by its ``VDate`` (a column containing the Visit Dates) values. ::

      $ macpie --id2-col=VID --date-col=VDate keepone --keep=latest visits.csv

   Equivalent command but using shorter single-dash option names for brevity::

      $ macpie -j VID -d VDate keepone -k earliest visits.csv


API
~~~

.. click:: macpie.cli.macpie.keepone:keepone
   :prog: macpie keepone
   :nested: full


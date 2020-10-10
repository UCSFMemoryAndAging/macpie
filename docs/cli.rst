

======================
Command Line Interface
======================

Installing MACPie also installs the ``macpie`` script, a command line tool that gives
you access to built-in commands that you can use to analyze Excel and/or CSV files.
The ``--help`` option will give more information about any commands and options.

Synopsis
--------
All commands should be executed inside the activated virtual environment (or conda environment)
you created in the :ref:`installation` section. All commands start with ``macpie`` and take
the following form:

.. code-block:: bash

    $ macpie [global_options] COMMAND [command_options] [ARGS]...

where:
    * ``[global_options]`` allow you to specify which columns in the files are the ID columns
      and/or Date columns, otherwise defaults are used.
      See :ref:`Global Options <global-options>` section for more details.

    * ``COMMAND`` is one of the commands you wish to execute, such as
      :ref:`link <command-link>` or :ref:`keepone <command-keepone>`.

    * ``[command_options]`` allow you to specify options specific to the chosen ``COMMAND``, otherwise
      defaults are used.

    * ``[ARGS]`` specify the files the command will analyze. Currently only Excel (``.xlsx``) and 
      comma-separated values (``.csv``) files are supported, so the files must be 
      in one of those formats and have one of those file extensions.


Output
~~~~~~
Executing a command will create a a results folder with a name containing the date and
time of execution: ``results_YYYYMMDD_HHMMSS``.

Inside the folder will contain a single results file in Excel format with the same name
as the folder: ``results_YYYYMMDD_HHMMSS.xlsx``.

Depending on the command executed, there may be other files (e.g. log files) placed in the
results folder, or other hidden worksheets (e.g. containing log information) in the results file.


Examples
~~~~~~~~

#. For every row in ``cdr.csv``, find all the records in ``faq.csv`` that match on the ``PIDN``
   field and whose ``DCDate`` is within 90 days of each other. ::

      $ macpie link cdr.csv faq.csv


For more examples specific to each command, go to the command's examples section:

#. :ref:`keepone <examples-keepone>` examples
#. :ref:`link <examples-link>` examples


.. _global-options:

Global Options
--------------

These global options help ``macpie`` know which columns in your files are the key columns
(such as columns containing your primary IDs and dates and/or any secondary IDs).
If they are not specified using these options, then defaults (as described below) will be used.


.. option:: -i <STRING>, --id-col=<STRING>

   ``Default=InstrID``. ID Column header. The column header of the primary ID column.
   In general, this column contains the primary key/index (unique identifiers) of the data
   object. In a research data management system, this is typically the ID of a specific
   data form or assessment.

.. option:: -d <STRING>, --date-col=<STRING>

   ``Default=DCDate``. Date column header. The column header of the primary date column.
   In a research data management system, this is typically the date the form or assessment
   was completed or collected.

.. option:: -j <STRING>, --id2-col=<STRING>

   ``Default=PIDN``. ID2 column header. The column header of the secondary ID column.
   In general, this column contains the secondary key/index of the data object. In a research
   data management system, this is typically the ID of the patient, subject, or participant
   who completed the form or assessment.

.. option:: -v, --verbose

   Verbose messages. Output more details on what the executed command is doing or has done.


.. _command-keepone:

Command - ``keepone``
---------------------

This command groups rows that have the same :option:`--id2-col` value, and allows you to keep
only the earliest or latest row in each group as determined by the :option:`--date-col` values
(discarding the other rows in the group).


Usage
~~~~~
.. code-block:: bash

    $ macpie keepone [OPTIONS] [PRIMARY]


Options
~~~~~~~

.. option:: -k <STRING>, --keep=<STRING> (all|first|latest)

   Specify which rows of the ``PRIMARY`` file to keep.

   - ``all`` (`default`): keep all rows
   - ``first``: for each unique value in the column specified by the :option:`--id2-col` option, keep only the first (i.e. earliest) row (determined by the values in the :option:`--date-col` column)
   - ``latest``: for each unique value in the column specified by the :option:`--id2-col` option, keep only the last (i.e. latest) row (determined by the values in the :option:`--date-col` column)

Arguments
~~~~~~~~~

.. option:: PRIMARY

   *Required*. A list of filenames and/or directories.

Output
~~~~~~

The results of each data object will be stored in a corresponding worksheet inside the results file.


.. _examples-keepone:

Examples
~~~~~~~~

#. For each ``PIDN``, keep only the first CDR record as determined by its ``DCDate``. ::

      $ macpie keepone --keep=first cdr.csv

   Equivalent command but using shorter single-dash option names for brevity::

      $ macpie keepone -k first cdr.csv

#. For each ``VID`` (a column containing Visit IDs), keep the latest record
   as determined by its ``VDate`` (a column containing the Visit Dates) values. ::

      $ macpie --id2-col=VID --date-col=VDate keepone --keep=latest visits.csv

   Equivalent command but using shorter single-dash option names for brevity::

      $ macpie -j VID -d VDate keepone -k first visits.csv


.. _command-link:

Command - ``link``
------------------

This command links data across multiple data objects using a specified timepoint anchor and time range.

Specifically, a single ``PRIMARY`` data object contains the timepoint anchor (the :option:`--date-col` column).
Then, one or more ``SECONDARY`` data objects is linked by retrieving all rows that match on the
``PRIMARY`` data object's :option:`--id2-col` field and whose :option:`--date-col` fields are within a certain
time range of each other.

Usage
~~~~~
.. code-block:: bash

    $ macpie link [OPTIONS] PRIMARY [SECONDARY]

Options
~~~~~~~

.. option:: -k <STRING>, --primary-keep=<STRING> (all|first|latest)

   Specify which rows of the ``PRIMARY`` file to keep. These rows will serve as the timepoint anchor.

    - ``all`` (`default`): keep all rows
    - ``first``: for each group of unique :option:`--id2-col` values, keep the first (i.e. earliest) row,
      as determined by the :option:`--date-col` values
    - ``latest``: for each group of unique :option:`--id2-col` value, keep the latest (i.e. most recent) row,
      as determined by the :option:`--date-col` values

.. option:: -g <STRING>, --secondary-get=<STRING> (all|closest)

   Specify which rows of the ``[SECONDARY]`` file(s) to get:

    - ``all`` (`default`): get all rows that are within :option:`--secondary-days` days of the
      corresponding ``PRIMARY`` timepoint anchor
    - ``closest``: get only the closest row that is within :option:`--secondary-days` days of the
      corresponding ``PRIMARY`` timepoint anchor

.. option:: -d <INTEGER>, --secondary-days=<INTEGER>

   ``Default=90``. Specify the time range measured in days.

.. option:: -w <STRING>, --secondary-when=<STRING> (earlier|later|earlier_or_later)

   Specify which rows of the ``[SECONDARY]`` file(s) to get:

   - ``earlier``: get only rows that are earlier than the timepoint anchor
   - ``later``: get only rows that are later (more recent) than the timepoint anchor
   - ``earlier_or_later`` (`default`): get rows that are earlier or later (more recent)
     than the timepoint anchor

.. option:: --help

    Show a short summary of the usage and options.
   


Arguments
~~~~~~~~~

.. option:: PRIMARY 

   *Required*. Filename of the primary data object. One and only one must be specified.
    

.. option:: SECONDARY

   *Optional*. Filenames of the secondary data object(s), delimited by a space. An unlimited
   number of files can be specified.
    


Output
~~~~~~

In the results file, the primary data object will have the suffix ``_anchor``, and every linked
secondary data object will have the suffix ``_linked``.

**IMPORTANT NOTE REGARDING DUPLICATES**: Each secondary data object result will have an extra column
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

A good way to know whether you are ready to combine your data objects into a single dataset is if each secondary
data object has the *same number of rows* as the primary anchor.


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
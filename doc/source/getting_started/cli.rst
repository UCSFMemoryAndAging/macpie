Command Line Interface
======================

Installing MACPie also installs a number of command line tools. The main command line tool
is also called ``macpie``, and it provides commands that you can use to analyze data contained
in Excel and/or CSV/text files. All commands should be executed inside your activated
virtual environment (or conda environment) that you created in the :ref:`installation` section.
The ``--help`` option will give more information about any commands and options.


``macpie`` command
------------------
All ``macpie`` commands start with ``macpie`` and take the following form:

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


Examples
~~~~~~~~

#. For every row in ``cdr.csv``, find all the records in ``faq.csv`` that match on the ``PIDN``
   field and whose ``DCDate`` is within 90 days of each other. ::

      $ macpie link cdr.csv faq.csv


For more examples specific to each command, visit the CLI Reference and go to the command's
examples section:

#. :ref:`keepone <examples-keepone>` examples
#. :ref:`link <examples-link>` examples
#. :ref:`merge <examples-merge>` examples


.. _command-mppair:

``mppair`` command
==================

.. program:: mppair

Commands for working with pairs of files.

``mppair`` subcommands are executed as part of a pipeline, where the output of one
command feeds the input of the next command, similar to how a pipe on unix works.

Example
~~~~~~~
.. code-block:: bash

    $ mppair -n "DCDate" -i left.xlsx right.xlsx conform -i replace -r "c" -v "b" replace -r "CDR[MZ]" -v CDR --regex compare

Breaking down the command:

#. ``mppair -n "DCDate" -i`` will drop/ignore the `DCDate` column
#. ``left.xlsx right.xlsx`` is the file pair to process
#. ``conform -i`` will conform the files to each other so that the column headers are similarly ordered
#. ``replace -r "c" -v "b"`` takes the resulting output file pair of the preceding ``conform`` command and replaces all cells with a value of "c" to "b"
#. ``replace -r "CDR[MZ]" -v CDR --regex`` takes the result file pair of the preceding ``replace`` command and replaces more values using a regular expression
#. ``compare`` compares the final results 


.. include:: ./compare.inc

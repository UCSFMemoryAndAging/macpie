.. program:: compare

.. _command-compare:

macpie compare
--------------

This command compares two Excel files and outputs differences found, if any.

If specific sheets to compare are not specified in the options (e.g. using
:option:`compare --sheet` or :option:`compare --sheet-pair`), then the default
is to compare common sheets (i.e. sheets with the same name.) If there are no
common sheets, then just compare the first sheets.

Usage
~~~~~
.. code-block:: bash

    $ macpie compare [OPTIONS] LEFT_FILE RIGHT_FILE


Options
~~~~~~~

.. option:: -s <STRING>, --sheet=<STRING>

   Name of worksheet to compare in both files. If worksheet names are different,
   then use the :option:`compare --sheet-pair` option below.

.. option:: -p <STRING>, --sheet-pair=(<STRING>,<STRING>)

   A length-2 tuple where the first and second strings are the names of the
   worksheets to be compared in the first and second Excel files, respectively.
   If the worksheet names are the same, you may use the :option:`compare --sheet`
   option above.

.. option:: -c <STRING>, --sort-col=<STRING>

   Column to sort on before comparing. Should exist in both files.

.. option:: -e <STRING>, --engines=<STRING> (pandas|tablib)

   Which comparison engine to use.

   - ``pandas``: compare using pandas DataFrames
   - ``tablib``: compare using tablib Datasets


Arguments
~~~~~~~~~

.. option:: LEFT_FILE

   *Required*. Filename/path of the first Excel file to compare.

.. option:: RIGHT_FILE

   *Required*. Filename/path of the other Excel file to compared with the first.


Output
~~~~~~

If differences are found, an Excel file is output showing the differences,
one worksheet for each worksheet pair comparison.


.. _examples-compare:

Examples
~~~~~~~~

#. To compare all common sheets between the two files: ::
   
   $ macpie compare file1.xlsx file2.xlsx

#. To compare sheet ``CDR`` in left file with sheet ``CDR`` in right file: ::
   
   $ macpie compare --sheet CDR file1.xlsx file2.xlsx

#. To compare sheet ``CDR_A`` in left file with sheet ``CDR_B`` in right file: ::
   
   $ macpie compare --sheet-pair CDR_A CDR_B file1.xlsx file2.xlsx

#. To compare sheet ``CDR`` in left file with sheet ``CDR`` in right file, but
   first sorting by the ``InstrID`` column. ::
   
   $ macpie compare --sheet CDR --sort-col InstrID file1.xlsx file2.xlsx


API
~~~

.. click:: macpie.cli.macpie.compare:compare
   :prog: macpie compare
   :nested: full


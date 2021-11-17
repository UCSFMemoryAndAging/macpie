
.. _command-merge:

macpie merge
------------

This command is a common follow-up to the :ref:`link <command-link>` command, as it allows you to select specific fields 
across various datasets to merge together into one dataset (thereby removing unwanted fields, which can be many).

The output file of the ``link`` command includes a worksheet named ``_available_fields``. This provides
a view of all the fields across all the datasets that you input into the ``link`` command. By placing an ``"x"``
next to a particular field, the ``merge`` command will attempt to merge only those fields you marked into one single dataset.
The linking fields (i.e. ``id_col_name``, ``date_col_name``, and ``id2_col`` of the primary argument in the ``link`` command, 
e.g. ``PIDN``, ``DCDate``, ``InstrID``) will always be included.

NOTE: The output file of this command can also be an input to this same command.


Usage
~~~~~
.. code-block:: bash

    $ macpie merge PRIMARY

Options
~~~~~~~

.. option:: --help

    Show a short summary of the usage and options.


Arguments
~~~~~~~~~

.. option:: PRIMARY 

   *Required*. Filename of the results file created by the ``link`` command OR this command.


Output
~~~~~~

In the results file, all the merged fields will be in a single worksheet. Any dataset that was not
merged (by choice or because there were duplicates), will remain in its own worksheet. If a dataset
could not be merged because there were duplicates, you can remove the duplicates, save the file, and use
this same command to attempt the merge again.

.. _examples-merge:

Examples
~~~~~~~~
#. After linking ``cdr.csv`` and ``faq.csv`` together, I decide only want the the following fields in my dataset:

    * ``CDRTot`` and ``BoxScore`` from ``cdr.csv``

    * ``FAQTot`` from ``faq.csv``

   #. So first, open the results file from the ``link`` command and navigate to the ``_available_fields`` worksheet.
   #. Mark an ``"x"`` next to those fields.
   #. Save the file.
   #. Run the following command: ::

      $ macpie merge results_XXX.xlsx


API
~~~

.. click:: macpie.cli.macpie.merge:merge
   :prog: macpie merge
   :nested: full


         
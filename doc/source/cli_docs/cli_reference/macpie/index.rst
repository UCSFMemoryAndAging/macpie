``macpie`` command
==================

.. program:: macpie

.. _global-options:

Global Options
--------------

These global options help ``macpie`` know which columns in your files are the key columns
(such as columns containing your primary IDs and dates and/or any secondary IDs).
If they are not specified using these options, then defaults (as described below) will be used.


.. option:: -i <STRING>, --id-col=<STRING>

   ``Default=InstrID``. ID column header. The column header of the primary ID column.
   In general, this column contains the primary key/index (unique identifiers) of the dataset.
   In a research data management system, this is typically the ID of a specific
   data form or assessment.

.. option:: -d <STRING>, --date-col=<STRING>

   ``Default=DCDate``. Date column header. The column header of the primary Date column.
   In a research data management system, this is typically the date the form or assessment
   was completed or collected.

.. option:: -j <STRING>, --id2-col=<STRING>

   ``Default=PIDN``. ID2 column header. The column header of the primary ID2 column.
   In general, this column contains the secondary key/index of the dataset. In a research
   data management system, this is typically the ID of the patient, subject, or participant
   who completed the form or assessment.

.. option:: -v, --verbose

   Verbose messages. Output more details on what the executed command is doing or has done.


.. include:: ./keepone.inc

.. include:: ./link.inc

.. include:: ./merge.inc

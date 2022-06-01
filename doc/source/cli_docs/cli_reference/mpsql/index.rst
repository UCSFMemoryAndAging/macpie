.. _command-mpsql:

``mpsql`` command
=================

.. program:: mpsql

Commands for working with SQL databases.


.. _mpsql-main-options:

Main Options
--------------

These main options provide the information needed to establish a connection
to the database.

.. option:: -u <STRING>, --user=<STRING>

   Username to connect to the database.
   Environment variable is ``MACPIE_MYSQL_USER``.

.. option:: -p <STRING>, --password=<STRING>

   Password to connect to the database.
   Environment variable is ``MACPIE_MYSQL_PWD``.

.. option:: -p <INTEGER>, --port=<INTEGER>

   Port number to use for connection. Default is ``3306``.
   Environment variable is ``MYSQL_TCP_PORT``.

.. option:: -h <STRING>, --host=<STRING>

   Host address of the database. Default is ``localhost``.
   Environment variable is ``MYSQL_HOST``.


.. include:: ./createtable.inc

.. include:: ./createproc.inc

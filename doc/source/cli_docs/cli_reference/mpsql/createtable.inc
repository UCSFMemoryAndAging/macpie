.. _command-createtable:

mpsql createtable
-----------------

This command generates the ``DROP TABLE`` and ``CREATE TABLE`` statements
for the specified database table.


Usage
~~~~~
.. code-block:: bash

    $ mpsql DATABASE createtable TABLENAME


Arguments
~~~~~~~~~

.. option:: TABLENAME

   *Required*. The table for which you want to generate ``DROP TABLE`` and
   ``CREATE TABLE`` statements.


Output
~~~~~~

``DROP TABLE`` and ``CREATE TABLE`` statements for the specified table.


.. _examples-createtable:

Examples
~~~~~~~~

#. To generate the drop/create statements for the ``FAQ`` table: ::

      $ mpsql lava_mac_dev createtable faq

   Output:

   .. code-block:: sql
      
      DROP TABLE IF EXISTS `faq`;
      CREATE TABLE `faq` (
      `InstrID` int(11) NOT NULL,
      `Checks` smallint(6) DEFAULT NULL,
      `Tax` smallint(6) DEFAULT NULL,
      `Shop` smallint(6) DEFAULT NULL,
      `Play` smallint(6) DEFAULT NULL,
      `Stove` smallint(6) DEFAULT NULL,
      `Meal` smallint(6) DEFAULT NULL,
      `Events` smallint(6) DEFAULT NULL,
      `Attn` smallint(6) DEFAULT NULL,
      `Appt` smallint(6) DEFAULT NULL,
      `Travel` smallint(6) DEFAULT NULL,
      `FAQTot` smallint(6) DEFAULT NULL,
      `CareID` int(11) DEFAULT NULL,
      `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      `TotalOnly` tinyint(1) NOT NULL DEFAULT '0',
      `Audit_Created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `Audit_EffDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `Audit_ExpDate` datetime NOT NULL DEFAULT '9999-09-09 00:00:00',
      `Audit_HostName` varchar(50) DEFAULT NULL,
      `Audit_Username` varchar(50) DEFAULT NULL,
      PRIMARY KEY (`InstrID`)
      ) ENGINE=InnoDB DEFAULT CHARSET=latin1;


API
~~~

.. click:: macpie.cli.mpsql.createtable:createtable
   :prog: mpsql createtable
   :nested: full


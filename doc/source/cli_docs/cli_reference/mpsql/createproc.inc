.. _command-createproc:

mpsql createproc
----------------

This command generates the ``DROP PROCEDURE`` and ``CREATE PROCEDURE``
statements for the specified database table.


Usage
~~~~~
.. code-block:: bash

    $ mpsql -u USERNAME -p DATABASE createproc PROCNAME


Arguments
~~~~~~~~~

.. option:: PROCNAME

   *Required*. The stored procedure name for which you want to generate
   ``DROP PROCEDURE`` and ``CREATE PROCEDURE`` statements.


Output
~~~~~~

``DROP PROCEDURE`` and ``CREATE PROCEDURE`` statements for the specified proc.


.. _examples-createproc:

Examples
~~~~~~~~

#. To generate the drop/create statements for the ``lq_set_linkdata_multiple``
   stored proc: ::

      $ mpsql lava_mac_dev createproc lq_set_linkdata_multiple

   Output:

   .. code-block:: text

      -- -----------------------------------------------------------------
      -- procedure lq_set_linkdata_multiple
      -- -----------------------------------------------------------------
   
      DROP PROCEDURE IF EXISTS `lq_set_linkdata_multiple`;
      
      DELIMITER $$
      
      CREATE DEFINER=`root`@`localhost` PROCEDURE `lq_set_linkdata_multiple`(user_name varchar(50), host_name varchar(25), linkdata_list varchar(16000))
      BEGIN
      
      -- Ex. call lq_set_linkdata_multiple(null,null,'(1,"2019-03-02",2),(3,"2018-04-05",4),(0,"9999-9-9",0),');
      
      SET @s = CONCAT('INSERT INTO `temp_linkdata1` (`pidn`, `link_date`, `link_id`) VALUES ', linkdata_list, ';');
      PREPARE stmt1 FROM @s;
      EXECUTE stmt1;
      DEALLOCATE PREPARE stmt1;
      
      END
      
      $$
      DELIMITER ;


API
~~~

.. click:: macpie.cli.mpsql.createproc:createproc
   :prog: mpsql createproc
   :nested: full


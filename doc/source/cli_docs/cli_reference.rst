.. _cli_reference:

CLI Reference
=============

Installing MACPie also installs a number of command line tools. The main
command line tool is called ``macpie``, and it provides commands that you
can use to analyze data contained in Excel and/or CSV/text files. Other
commands include ``mpsql`` and ``mpfile``, commands that work with SQL
databases and files, respectively.

All commands should be executed inside your activated virtual environment
(or conda environment) that you created in the :ref:`installation` section.
The ``--help`` option will give more information about any commands and options.


Environment Variables
---------------------

Some commands (e.g. ``mpsql``) support environment variables, which can be
manually set (e.g. ``export ENV_VAR=ENV_VALUE``), or loaded from a dotenv
file named ``.macpieenv`` located in your home directory.

For example, instead of typing in your database password every time to the
``mpsql`` command, like so: ::

   $ mpsql -u lava_mac -p lava_mac_dev createtable faq

you can create a file in your home directory called ``.macpieenv``, and
set the database username and passwords using the proper environment variables
names, like so:

.. code-block:: text
   
   MACPIE_MYSQL_USER = lava_mac_dev
   MACPIE_MYSQL_PWD = somepassword

Now, the same command above can be executed with the following command: ::

   $ mpsql lava_mac_dev createtable faq


Command Summary
---------------

.. toctree::
  :maxdepth: 3

  macpie <cli_reference/macpie/index>
  mpsql <cli_reference/mpsql/index>
  mpfile <cli_reference/mpfile/index>
  

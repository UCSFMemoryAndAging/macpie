.. _installation:


Installation
============

All you need to install MACPie is a Python environment. If
you do not have Python installed or are not sure, the easiest way to proceed is to
install Anaconda, a popular cross platform distribution of Python.


Python version support
----------------------

Python version 3.7 or greater is required.


Installing MACPie using your existing Python installation
---------------------------------------------------------

When using Python tools such as MACPie, it is recommended to isolate
them inside of a virtual
environment so they do not conflict with other Python tools or projects. So
first create a virtual environment, and from then on, use this
virtual environment every time you use MACPie.

Create a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Go to the directory where you would like to create your virtual environment.

On MacOS and Linux:

.. code-block:: bash

    $ python3 -m venv env

On Windows:

.. code-block:: bash

    $ py -m venv env

The second argument, ``env``, is the name of your new virtual environment.

``venv`` will create a virtual Python installation in the ``env`` folder.

Activate the virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you can start installing or using packages in your virtual environment,
you need to *activate* it.

On MacOS and Linux:

.. code-block:: bash

    $ source env/bin/activate

On Windows:

.. code-block:: bash

    $ .\env\Scripts\activate

You can confirm you’re in the activated virtual environment by checking the location
of your Python interpreter; it should point to the ``env`` directory.

On MacOS and Linux:

.. code-block:: bash

    $ which python
    .../env/bin/python

On Windows:

.. code-block:: bash

    $ where python
    .../env/bin/python.exe

As long as your virtual environment is activated, pip will install packages
into that specific virtual environment.

Install `macpie` via `pip` in your virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Now that you're in your virtual environment, you can install ``macpie``.

.. code-block:: bash

    $ pip install macpie

MACPie is now installed and you are ready to use it in your code or on the command line.

Leaving the virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you want to switch projects or otherwise leave your virtual environment, simply run:

.. code-block:: bash

    $ deactivate

If you want to re-enter the virtual environment just follow the same instructions above
about activating a virtual environment. There’s no need to re-create the virtual environment.


Installing MACPie with Anaconda
-------------------------------

If you don't have an existing Python environment, we recommend installing Python by installing Anaconda.


Installing Conda
~~~~~~~~~~~~~~~~

The simplest way to install Anaconda is to use their minimal installer called Miniconda.

- Visit <https://docs.conda.io/en/latest/miniconda.html>
- Download the appropriate installer for your system (Windows, MacOSX, Linux)
- Follow the instructions prompted by the installer to install Miniconda on your system

Starting Conda
~~~~~~~~~~~~~~

On MacOS and Linux:

- Open a terminal window
- All commands below are typed into the terminal window.

On Windows:

- From the Start menu, search for and open "Anaconda Prompt (Miniconda)"
- All commands below are typed into the Anaconda Prompt window.

Verify that conda is installed and running on your system by typing:

.. code-block:: bash

    $ conda --version

Conda displays the number of the version that you have installed, such as ``conda 4.8.4``.

If you get an error message, make sure of the following:

- You are logged into the same user account that you used to install Anaconda or Miniconda.
- You are in a directory that Anaconda or Miniconda can find.
- You have closed and re-opened the terminal window after installing conda.

Create a conda environment
~~~~~~~~~~~~~~~~~~~~~~~~~~
When using Python tools, it is recommended to isolate them inside of a conda
environment so they do not conflict with other Python tools or projects. So
first create an environment, and from then on, you will use this
environment every time you use MACPie.

To create an environment:

.. code-block:: bash

    $ conda create --name myenv

Activate conda environment
~~~~~~~~~~~~~~~~~~~~~~~~~~
To activate your conda environment:

.. code-block:: bash

    $ conda activate myenv

By default, the active environment--the one you are currently using--is shown in parentheses ()
or brackets [] at the beginning of your command prompt: 

.. code-block:: bash

    (myenv) $

Install `macpie` via `pip` in your conda environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Now that you're in your conda environment and its activated, you can use `pip` to install `macpie`.

.. code-block:: bash

    $ pip install macpie


Leaving the conda environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To leave your conda environment, it is better to return to the base environment rather than
deactivate your current environment. You return to the base environment by calling `activate`
with no environment specified.

.. code-block:: bash

    $ conda activate


Installing optional dependencies
--------------------------------

macpie has optional dependencies that are only used for specific classes
or methods. For example, macpie.collections.BasicGraph uses the ``networkx``
package, while the ``mpfile`` command requires the ``tabulate`` package.

Dotenv file support for CLI tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Some commands make use of environment variables, and such environment variables
can be loaded from a dotenv file in your home directory called ``.macpieenv``.
To support this functionality, the following dependency needs to be installed.

========================= ================== =============================================================
Dependency                Minimum Version    Notes
========================= ================== =============================================================
python-dotenv             0.20               Reads .env file and sets environment variables
========================= ================== =============================================================

Install with: ``pip install macpie[dotenv]``

mpsql command
~~~~~~~~~~~~~
The ``mpsql`` commands deals with SQL databases, and therefore depends on the
the following packages:

========================= ================== =============================================================
Dependency                Minimum Version    Notes
========================= ================== =============================================================
mysql-connector-python    8.0                Python driver for communicating with MySQL servers
SQLAlchemy                1.3                Python ORM library
========================= ================== =============================================================

Install with: ``pip install macpie[mpsql]``

mpfile command
~~~~~~~~~~~~~~

========================= ================== =============================================================
Dependency                Minimum Version    Notes
========================= ================== =============================================================
tabulate                  0.8                Pretty print tabular data
========================= ================== =============================================================

Install with: ``pip install macpie[mpfile]``

All command line tools
~~~~~~~~~~~~~~~~~~~~~~
You can also install all of the command line tool dependencies with:

.. code-block:: bash

    $ pip install macpie[cli]

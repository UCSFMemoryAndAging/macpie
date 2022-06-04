Contributing
============

Thank you for considering contributing to MACPie!


Reporting issues
----------------

Include the following information in your post:

-   Describe what you expected to happen.
-   Describe what actually happened. Include the full traceback if there
    was an exception.
-   List your Python and MACPie versions. If possible, check
    if this issue is already fixed in the latest releases or the latest
    code in the repository.
-   If possible, include a `minimal reproducible example`_ to help us
    identify the issue. This also helps check that the issue is not with
    your own code.
-   Email the above to albert.lee2@ucsf.edu


.. _minimal reproducible example: https://stackoverflow.com/help/minimal-reproducible-example


Submitting patches
------------------

Include the following in your patch:

-   Include tests if your patch adds or changes code. Make sure the test
    fails without your patch.
-   Update any relevant docs pages and docstrings. Docs pages and
    docstrings should be wrapped at 72 characters.
-   Add an entry in ``CHANGES.rst``. Use the same style as other
    entries. Also include ``.. versionchanged::`` inline changelogs in
    relevant docstrings.


First time setup
~~~~~~~~~~~~~~~~

-   Download and install the `latest version of git`_.
-   Configure git with your `username`_ and `email`_.

    .. code-block:: text

        $ git config --global user.name 'your name'
        $ git config --global user.email 'your email'

-   Make sure you have a `GitHub account`_.
-   Fork MACPie to your GitHub account by clicking the `Fork`_ button.
-   `Clone`_ the main repository locally.

    .. code-block:: text

        $ git clone https://github.com/UCSFMemoryAndAging/macpie
        $ cd macpie

-   Add your fork as a remote to push your work to. Replace
    ``{username}`` with your username. This names the remote "fork", the
    default remote is "origin".

    .. code-block:: text

        git remote add fork https://github.com/{username}/macpie

-   Create a virtualenv.

    .. tabs::

       .. group-tab:: macOS/Linux

          .. code-block:: text

             $ python3 -m venv env
             $ . env/bin/activate

       .. group-tab:: Windows

          .. code-block:: text

             > py -3 -m venv env
             > env\Scripts\activate

-   Upgrade pip and setuptools.

    .. code-block:: text

        $ python -m pip install --upgrade pip setuptools

-   Install MACPie in editable mode with development dependencies.

    .. code-block:: text

        $ pip install -e . -r requirements/dev.txt

    If you want to start with all dependencies:

    -   At the prompt:

        .. code-block:: text

            $ pip install -e .[all] -r requirements/dev.txt

    -   Or if you are using ``zsh`` shell, note that square brackets are used
        for globbing / pattern matching, so you'll need to quote the argument like so:

        .. code-block:: text

            $ pip install -e '.[all]' -r requirements/dev.txt

        


.. _latest version of git: https://git-scm.com/downloads
.. _username: https://help.github.com/en/articles/setting-your-username-in-git
.. _email: https://help.github.com/en/articles/setting-your-commit-email-address-in-git
.. _GitHub account: https://github.com/join
.. _Fork: https://github.com/UCSFMemoryAndAging/macpie/fork
.. _Clone: https://help.github.com/en/articles/fork-a-repo#step-2-create-a-local-clone-of-your-fork


Start coding
~~~~~~~~~~~~

-   Create a branch to identify the issue you would like to work on. If
    you're submitting a bug or documentation fix, branch off of the
    latest ".x" branch.

    .. code-block:: text

        $ git fetch origin
        $ git checkout -b your-branch-name origin/0.2.x

    If you're submitting a feature addition or change, branch off of the
    "master" branch.

    .. code-block:: text

        $ git fetch origin
        $ git checkout -b your-branch-name origin/master

-   Using your favorite editor, make your changes,
    `committing as you go`_.
-   Include tests that cover any code changes you make. Make sure the
    test fails without your patch. Run the tests as described below.
-   Push your commits to your fork on GitHub and
    `create a pull request`_. Link to the issue being addressed with
    ``fixes #123`` in the pull request.

    .. code-block:: text

        $ git push --set-upstream fork your-branch-name

.. _committing as you go: https://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
.. _create a pull request: https://help.github.com/en/articles/creating-a-pull-request


Running basic test suite
~~~~~~~~~~~~~~~~~~~~~~~~

Run the basic test suite with pytest.

.. code-block:: text

    $ pytest --runslow

This runs the tests for the current environment, which is usually
sufficient. The ``--runslow`` flag tell pytest to run any tests marked as slow.

Running full test suite
~~~~~~~~~~~~~~~~~~~~~~~~

The full test suite takes a long time to run because it tests multiple combinations
of Python and dependencies. You need to have Python 3.8, 3.9, and 3.10 installed to
run all of the environments. Then run:

.. code-block:: text

    $ tox
    # or "tox -r" to force recreation of virtual environments

If you aren't already set up to install multiple version of Python, I recommend using `pyenv`_.

.. _pyenv: https://github.com/pyenv/pyenv

-   Install ``pyenv``

-   Update list of available versions.

    .. code-block:: text

        $ pyenv update

-   List available versions to install.

    .. code-block:: text

        $ pyenv install -l

-   Install the Python versions you want to test

    .. code-block:: text

        $ pyenv install 3.8.13
        $ pyenv install 3.9.13
        $ pyenv install 3.10.4
    
-   In your local repo root:

    .. code-block:: text

        $ pyenv local 3.8.13 3.9.13 3.10.4

    This will set local application-specific Python version(s) (in order of preference)
    by writing the version name(s) to a ``.python-version`` file in the current directory.

    Now you can execute the full test suite with ``tox``.

    .. code-block:: text

        $ tox

    When you're done and/or want to unset the local version:

    .. code-block:: text

        $ pyenv local --unset

Other useful ``pyenv`` commands:

.. code-block:: console
    
    $ # list versions
    $ pyenv versions
    $
    $ # set the global Python version
    $ pyenv global 3.6.12
    $
    $ # set application-specific version by creating a .python-version file in current dir.
    $ # sets the pyverison for current dir and subdirs
    $ pyenv local 3.8.5
    $
    $ # set shell-specific Python version
    $ pyenv shell 3.8-dev


Read more about `tox <https://tox.readthedocs.io>`__.


Running test coverage
~~~~~~~~~~~~~~~~~~~~~

Generating a report of lines that do not have test coverage can indicate
where to start contributing. Run ``pytest`` using ``coverage`` and
generate a report.

.. code-block:: text

    $ pip install coverage
    $ coverage run -m pytest --runslow
    $ coverage html

Open ``htmlcov/index.html`` in your browser to explore the report.

Read more about `coverage <https://coverage.readthedocs.io>`__.


Building the docs
~~~~~~~~~~~~~~~~~

Build the docs in the ``docs`` directory using Sphinx.

.. code-block:: text

    $ cd docs
    $ make html

Open ``_build/html/index.html`` in your browser to view the docs.

Read more about `Sphinx <https://www.sphinx-doc.org/en/stable/>`__.


Upgrading dependencies
~~~~~~~~~~~~~~~~~~~~~~

To upgrade dependencies, we use `pip tools <https://github.com/jazzband/pip-tools>`__.

-   Update all packages for dev

    .. code-block:: console

        $ pip-compile --upgrade --output-file requirements/dev.txt requirements/dev.in

-   Update all packages for tests

    .. code-block:: console

        $ pip-compile --upgrade --output-file requirements/tests.txt requirements/tests.in

-   Update all packages for docs

    .. code-block:: console

        $ pip-compile --upgrade --output-file requirements/doc.txt requirements/doc.in

-   Then to proceed with development, install the upgraded dev dependencies

    .. code-block:: console

        $ pip install -r requirements/dev.txt


Uploading new version to PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   Create a git tag for the new version

    .. code-block:: console

        $ git tag -a v0.5.0 -m "release: v0.5.0"

-   Push tag to remote

    .. code-block:: console

        $ git push origin v0.5.0

-   Create distribution archives

    .. code-block:: console

        $ python setup.py sdist bdist_wheel

-   Upload distribution files to PyPI via twine (``pip install twine`` if needed)

    .. code-block:: console

        $ python3 -m twine upload dist/macpie-0.5.0*

-   In github, perform the following:

    #. Click on `Releases`
    #. Click on `Draft a new release`
    #. Choose the proper tag
    #. Release title: v0.5.0
    #. Describe this release: Refer to the [changelog](https://macpie.readthedocs.io/en/latest/changelog/) for details.

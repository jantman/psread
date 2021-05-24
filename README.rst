psread
======

Quick, simple AWS Parameter Store CLI for listing/reading params with tab completion

.. image:: asciinema.gif
  :width: 590
  :alt: screen recording of psread usage example

.. image:: https://www.repostatus.org/badges/latest/wip.svg
   :alt: Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.
   :target: https://www.repostatus.org/#wip

Background
----------

The AWS-provided tools for using Parameter Store (the web UI and awscli) are fine if you know *exactly* what you're trying to find. They're not so good if you're... looking... for something, and want to explore your Parameter Store parameters like a filesystem, or hierarchical datastore. This is a dead-simple, quick, and rather ugly hack of a CLI built in Python and largely inspired by the `Hashicorp Vault <https://www.vaultproject.io/>`_ CLI, plus shell completion for parameter paths. This doesn't write parameters or do other "fancy" things. It's mainly intended for teams who are also using Parameter Store to replace human-centered secret stores (i.e. Vault, KeePass, random encrypted files, etc.) and often have only a vague idea of the exact parameter name they're looking for.

Status
------

This is a somewhat-tipsy Friday evening quarantine project. There are (it's almost painful to write this) no unit tests, and it's largely cargo-culted from previous work of mine. I'll gladly accept PRs assuming they look correct, meet PEP8/PyFlakes style, and are relatively straightforward and working. That's about the end of "support".

Requirements
------------

This project **requires** Python 3.6 or later, as it makes use of both `PEP484 type hints <https://www.python.org/dev/peps/pep-0484/>`_ and `PEP498 f-strings <https://www.python.org/dev/peps/pep-0498/>`_. It also requires `boto3 <https://pypi.org/project/boto3/>`_, `argcomplete <https://pypi.org/project/argcomplete/>`__, and `appdirs <https://pypi.org/project/appdirs/>`_.

Installation
------------

psread can be installed with ``pip install psread`` or ``python -mpip install psread``

To set up autocompletion in your shell, either `activate global completion for argcomplete <https://pypi.org/project/argcomplete/#activating-global-completion>`_, or for bash, set up completion for this project specifically. To do that in just your current shell:

.. code-block:: bash

    eval "$(psread --bash-wrapper)"

To do that permanently (recommended):

.. code-block:: bash

    echo -e "eval \"\$($(which psread) --bash-wrapper)\"" >> ~/.bashrc

Usage
-----

There are two main functionalities: listing parameters and reading parameters. Shell tab completion is included, primarily for **bash**, via the `argcomplete <https://pypi.org/project/argcomplete/>`__ package.

.. code-block:: bash

    $ psread -h
    usage: psread [-h] [-v] [-w] [-V] [-R] [--called-from-wrapper] [{ls,list,read,get}] [PARAM]

    Quick, simple AWS Parameter Store CLI for listing/reading params with tab completion

    positional arguments:
      {ls,read,get}         Action to perform
      PARAM                 Parameter (or parameter path) to list or read

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         verbose output. specify twice for debug-level output.
      -w, --bash-wrapper    print bash wrapper function to STDOUT and exit
      -V, --version         Print version number and exit
      -R, --recache         re-cache parameters for this region of this account
      --called-from-wrapper
                            DO NOT USE

Parameter Caching
+++++++++++++++++

psread caches the Names (and only the names) of all parameters in each region of each account that you use it with; this is effectively required for sane tab-completion speeds. The parameters are cached in a Pickle file at a platform-specific path, which can be seen in the ``psread -V`` output. This path can be overridden with the ``PSREAD_CACHE_PATH`` environment variable, which should specify the absolute path to write the pkl file at.

By default, parameter names are cached for 86400 seconds (1 day); this can be overridden by setting the ``PSREAD_CACHE_TTL`` environment variable to an integer cache TTL in seconds.

Re-caching of the current region of the current account can be forced by running psread with the ``-R`` or ``--recache`` option.

Debugging
---------

In order to enable debug logging before normal command-line options and arguments are parsed, such as during tab completion: ``export PSREAD_LOG=DEBUG``

Release Process
---------------

Completely manual right now:

1. Bump the version in ``psread.py`` and update the Changelog.
2. ``python setup.py sdist && python setup.py bdist_wheel``
3. ``twine upload dist/*``
4. ``git push``
5. ``git tag -s -a X.Y.Z -m 'X.Y.Z released YYYY-mm-dd' && git tag -v X.Y.Z && git push origin X.Y.Z``

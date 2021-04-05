psread
======

Quick, simple AWS Parameter Store CLI for listing/reading params with tab completion

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

Parameter Caching
+++++++++++++++++

``PSREAD_CACHE_PATH`` defaults to ``psread.pkl`` within your platform-specific user cache directory (your cache file path is included in the ``psread -V`` output).

``PSREAD_CACHE_TTL`` in seconds; defaults to 86400 (1 day).

Debugging
---------

``export PSREAD_LOG=DEBUG``

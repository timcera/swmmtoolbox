.. image:: https://github.com/timcera/swmmtoolbox/actions/workflows/pypi-package.yml/badge.svg
    :alt: Tests
    :target: https://github.com/timcera/swmmtoolbox/actions/workflows/pypi-package.yml
    :height: 20

.. image:: https://img.shields.io/coveralls/github/timcera/swmmtoolbox
    :alt: Test Coverage
    :target: https://coveralls.io/r/timcera/swmmtoolbox?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/swmmtoolbox.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/swmmtoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/l/swmmtoolbox.svg
    :alt: BSD-3 clause license
    :target: https://pypi.python.org/pypi/swmmtoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/dd/swmmtoolbox.svg
    :alt: swmmtoolbox downloads
    :target: https://pypi.python.org/pypi/swmmtoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/pyversions/swmmtoolbox
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/swmmtoolbox/
    :height: 20

swmmtoolbox - Overview
----------------------
The swmmtoolbox is a Python script to read the Storm Water Management Model
(SWMM) version 5 binary output files.

Requirements
============
Python - of course, version 3.7+.

Installation
============
The swmmtoolbox is available via pip or conda.

pip
~~~
.. code-block:: bash

    pip install swmmtoolbox

conda
~~~~~
.. code-block:: bash

    conda install -c conda-forge swmmtoolbox

Usage
-----

Command Line
============
Just run 'swmmtoolbox --help' to get a list of subcommands and options::

    usage: swmmtoolbox [-h]
                       {about,catalog,extract,listdetail,listvariables,stdtoswmm5}
                       ...

    positional arguments:
      {about,catalog,extract,listdetail,listvariables,stdtoswmm5}
        about               Display version number and system information.
        catalog             List the catalog of objects in output file.
        extract             Get the time series data for a particular object and
                            variable.
        listdetail          List nodes and metadata in output file.
        listvariables       List variables available for each type.
        stdtoswmm5          Take the toolbox standard format and return SWMM5
                            format.

    options:
      -h, --help            show this help message and exit

Python API
==========
Simply import swmmtoolbox::

    import swmmtoolbox

    ntsd = swmmtoolbox.extract("tests/frutal.out", "node,45,Hydraulic_head")

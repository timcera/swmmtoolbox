SWMMToolbox - Overview
----------------------

IMPORTANT: Versions before 0.4 did NOT work correctly on output that had
pollutants.

The swmmtoolbox is a Python script to read the Storm Water Management Model
(SWMM) version 5 binary output files.

Requirements
============

Python - of course

The 'baker' library which should have been installed as a requirement.

Installation
============

Should be easy as ``pip install swmmtoolbox`` OR ``easy_install swmmtoolbox``
depending on your choice of Python package managers.

Running
=======

Just run 'swmmtoolbox' from a command line to get a list of subcommands::

    swmmtoolbox

.. program-output:: swmmtoolbox

Sub-command Detail
''''''''''''''''''

getdata
~~~~~~~
.. program-output:: swmmtoolbox getdata --help
 
list
~~~~
.. program-output:: swmmtoolbox list --help

listdetail
~~~~~~~~~~
.. program-output:: swmmtoolbox listdetail --help

listvariables
~~~~~~~~~~~~~
.. program-output:: swmmtoolbox listvariables --help

stdtoswmm5
~~~~~~~~~~
.. program-output:: swmmtoolbox stdtoswmm5 --help

Author
======

Tim Cera, P.E.

tim at cerazone dot net

SWMMTOOLBOX
===========

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

Just run 'swmmtoolbox' from a command line to get a list of subcomamnds::

    Usage: /sjr/beodata/local/python_linux/bin/swmmtoolbox COMMAND <options>
    
    Available commands:
    
     getdata        Get the time series data for a particular object and
                    variable
     list           List objects in output file
     listdetail     List nodes and metadata in output file
     listvariables  List variables available for each type
    
    Use "/sjr/beodata/local/python_linux/bin/swmmtoolbox <command> --help" for individual command help.

You can follow up with help for each subcommand to get a list of required and optional arguments.

For example::

 'swmmtoolbox getdata --help'
 
    Usage: /sjr/beodata/local/python_linux/bin/swmmtoolbox getdata <filename> [<labels>...]
    
    Get the time series data for a particular object and variable
    
    Required Arguments:
    
      filename   Filename of SWMM output file.
    
    Variable arguments:
    
       *labels   The remaining arguments uniquely identify a time-series in the
                 binary file. The format is 'TYPE,NAME,VARINDEX'. For example:
                 'node,C64,1 node,C63,1 ...' TYPE and NAME can be retrieved with
                 'swmmtoolbox list filename.out' VARINDEX can be retrieved with
                 'swmmtoolbox listvariables filename.out'
    
    (specifying a double hyphen (--) in the argument list means all
    subsequent arguments are treated as bare arguments, not options)

Author
======

Tim Cera, P.E.

tim at cerazone dot net

Please send me a note if you find this useful, found a bug, submit a patch,
...etc.


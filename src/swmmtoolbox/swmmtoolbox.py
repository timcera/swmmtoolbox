# -*- coding: utf-8 -*-
# Example package with a console entry point
"""Reads and formats data from the SWMM 5 output file."""

from __future__ import absolute_import, print_function

import copy
import datetime
import os
import struct
import sys
import warnings
from builtins import object, range, str, zip

import mando
import numpy as np
import pandas as pd
from mando.rst_text_formatter import RSTHelpFormatter
from tstoolbox import tsutils

PROPCODE = {
    0: {1: "Area"},
    1: {0: "Type", 2: "Inv_elev", 3: "Max_depth"},
    2: {0: "Type", 4: "Inv_offset", 3: "Max_depth", 5: "Length"},
}

# Names for the 'Node type' and 'Link type' codes above
TYPECODE = {
    0: {1: "Area"},
    1: {0: "Junction", 1: "Outfall", 2: "Storage", 3: "Divider"},  # nodes
    2: {0: "Conduit", 1: "Pump", 2: "Orifice", 3: "Weir", 4: "Outlet"},  # links
}

VARCODE = {
    0: {
        0: "Rainfall",
        1: "Snow_depth",
        2: "Evaporation_loss",
        3: "Infiltration_loss",
        4: "Runoff_rate",
        5: "Groundwater_outflow",
        6: "Groundwater_elevation",
        7: "Soil_moisture",
    },
    1: {
        0: "Depth_above_invert",
        1: "Hydraulic_head",
        2: "Volume_stored_ponded",
        3: "Lateral_inflow",
        4: "Total_inflow",
        5: "Flow_lost_flooding",
    },
    2: {
        0: "Flow_rate",
        1: "Flow_depth",
        2: "Flow_velocity",
        3: "Froude_number",
        4: "Capacity",
    },
    4: {
        0: "Air_temperature",
        1: "Rainfall",
        2: "Snow_depth",
        3: "Evaporation_infiltration",
        4: "Runoff",
        5: "Dry_weather_inflow",
        6: "Groundwater_inflow",
        7: "RDII_inflow",
        8: "User_direct_inflow",
        9: "Total_lateral_inflow",
        10: "Flow_lost_to_flooding",
        11: "Flow_leaving_outfalls",
        12: "Volume_stored_water",
        13: "Evaporation_rate",
        14: "Potential_PET",
    },
}

# Prior to 5.10.10
VARCODE_OLD = {
    0: {
        0: "Rainfall",
        1: "Snow_depth",
        2: "Evaporation_loss",
        3: "Runoff_rate",
        4: "Groundwater_outflow",
        5: "Groundwater_elevation",
    },
    1: {
        0: "Depth_above_invert",
        1: "Hydraulic_head",
        2: "Volume_stored_ponded",
        3: "Lateral_inflow",
        4: "Total_inflow",
        5: "Flow_lost_flooding",
    },
    2: {
        0: "Flow_rate",
        1: "Flow_depth",
        2: "Flow_velocity",
        3: "Froude_number",
        4: "Capacity",
    },
    4: {
        0: "Air_temperature",
        1: "Rainfall",
        2: "Snow_depth",
        3: "Evaporation_infiltration",
        4: "Runoff",
        5: "Dry_weather_inflow",
        6: "Groundwater_inflow",
        7: "RDII_inflow",
        8: "User_direct_inflow",
        9: "Total_lateral_inflow",
        10: "Flow_lost_to_flooding",
        11: "Flow_leaving_outfalls",
        12: "Volume_stored_water",
        13: "Evaporation_rate",
    },
}

# swmm_flowunits is here, but currently not used.
_SWMM_FLOWUNITS = {0: "CFS", 1: "GPM", 2: "MGD", 3: "CMS", 4: "LPS", 5: "LPD"}


_LOCAL_DOCSTRINGS = tsutils.docstrings
_LOCAL_DOCSTRINGS[
    "filename"
] = """filename : str
        Filename of SWMM output file.  The SWMM model must complete
        successfully for "swmmtoolbox" to correctly read it.
        """
_LOCAL_DOCSTRINGS[
    "itemtype"
] = """itemtype : str
        One of 'system', 'node', 'link', or 'pollutant' to identify the
        type of data you want to extract.
        """
_LOCAL_DOCSTRINGS[
    "labels"
] = """labels : str
        The remaining arguments uniquely identify a time-series
        in the binary file.  The format is::

            'TYPE,NAME,VAR'

        For example: 'link,41a,Flow_rate node,C63,1 ...'

        The VAR part of the label can be the name of the variable or the index.
        The available variables and their indices can be found using::

            'swmmtoolbox listvariables filename.out'

        All of the available labels can be listed with::

            'swmmtoolbox catalog filename.out'

        There is a wild card feature for the labels, where leaving the part out
        will return all labels that match all other parts.  For example,

        +-----------------+-------------------------------------+
        | link,b52,       | Return all variables for link "b52" |
        +-----------------+-------------------------------------+
        | link,,Flow_rate | Return "Flow_rate" for all links    |
        +-----------------+-------------------------------------+

        Note that all labels require two commas and no spaces.

        """


def tupleSearch(findme, haystack):
    """Partial search of list of tuples.

    The "findme" argument is a tuple and this will find matches in "haystack"
    which is a list of tuples of the same size as "findme".  An empty string as
    an item in "findme" is used as a wildcard for that item when searching
    "haystack".
    """
    match = []
    for words in haystack:
        testmatch = []
        for i, j in zip(findme, words):
            if not i:
                testmatch.append(True)
                continue
            if i == j:
                testmatch.append(True)
                continue
            testmatch.append(False)
        if all(testmatch):
            match.append(words)
    return match


class SwmmExtract(object):
    """The class that handles all extraction of data from the out file."""

    def __init__(self, filename):

        self.RECORDSIZE = 4

        self.fp = open(filename, "rb")

        self.fp.seek(-6 * self.RECORDSIZE, 2)

        (
            self.Namesstartpos,
            self.offset0,
            self.startpos,
            self.swmm_nperiods,
            errcode,
            magic2,
        ) = struct.unpack("6i", self.fp.read(6 * self.RECORDSIZE))

        self.fp.seek(0, 0)
        magic1 = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]

        if magic1 != 516114522:
            raise ValueError(
                """
*
*   Beginning magic number incorrect.
*
"""
            )
        if magic2 != 516114522:
            raise ValueError(
                """
*
*   Ending magic number incorrect.
*
"""
            )
        if errcode != 0:
            raise ValueError(
                """
*
*   Error code "{0}" in output file indicates a problem with the run.
*
""".format(
                    errcode
                )
            )
        if self.swmm_nperiods == 0:
            raise ValueError(
                """
*
*   There are zero time periods in the output file.
*
"""
            )

        # --- otherwise read additional parameters from start of file
        (
            version,
            self.swmm_flowunits,
            self.swmm_nsubcatch,
            self.swmm_nnodes,
            self.swmm_nlinks,
            self.swmm_npolluts,
        ) = struct.unpack("6i", self.fp.read(6 * self.RECORDSIZE))

        if version < 5100:
            varcode = VARCODE_OLD
        else:
            varcode = VARCODE

        self.itemlist = ["subcatchment", "node", "link", "pollutant", "system"]

        # Read in the names
        self.fp.seek(self.Namesstartpos, 0)
        self.names = {0: [], 1: [], 2: [], 3: [], 4: []}
        number_list = [
            self.swmm_nsubcatch,
            self.swmm_nnodes,
            self.swmm_nlinks,
            self.swmm_npolluts,
        ]
        for i, j in enumerate(number_list):
            for _ in range(j):
                stringsize = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
                self.names[i].append(
                    struct.unpack("{0}s".format(stringsize), self.fp.read(stringsize))[
                        0
                    ]
                )

        # Stupid Python 3
        for key in self.names:
            collect_names = []
            for name in self.names[key]:
                # Why would SWMM allow spaces in names?  Anyway...
                try:
                    rname = str(name, "ascii", "replace")
                except TypeError:
                    rname = name.decode("ascii", "replace")
                try:
                    collect_names.append(rname.decode())
                except AttributeError:
                    collect_names.append(rname)
            self.names[key] = collect_names

        # Update self.varcode to add pollutant names to subcatchment,
        # nodes, and links.
        self.varcode = copy.deepcopy(varcode)
        for itemtype in ["subcatchment", "node", "link"]:
            typenumber = self.type_check(itemtype)
            start = len(varcode[typenumber])
            end = start + len(self.names[3])
            nlabels = list(range(start, end))
            ndict = dict(list(zip(nlabels, self.names[3])))
            self.varcode[typenumber].update(ndict)

        # Read pollutant concentration codes
        # = Number of pollutants * 4 byte integers
        self.pollutant_codes = struct.unpack(
            "{0}i".format(self.swmm_npolluts),
            self.fp.read(self.swmm_npolluts * self.RECORDSIZE),
        )

        self.propcode = {}

        # self.prop[0] contain property codes and values for
        # subcatchments
        # self.prop[1] contain property codes and values for nodes
        # self.prop[2] contain property codes and values for links
        self.prop = {0: [], 1: [], 2: []}

        # subcatchments
        nsubprop = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.propcode[0] = struct.unpack(
            "{0}i".format(nsubprop), self.fp.read(nsubprop * self.RECORDSIZE)
        )
        for i in range(self.swmm_nsubcatch):
            rprops = struct.unpack(
                "{0}f".format(nsubprop), self.fp.read(nsubprop * self.RECORDSIZE)
            )
            self.prop[0].append(list(zip(self.propcode[0], rprops)))

        # nodes
        nnodeprop = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.propcode[1] = struct.unpack(
            "{0}i".format(nnodeprop), self.fp.read(nnodeprop * self.RECORDSIZE)
        )
        for i in range(self.swmm_nnodes):
            rprops = struct.unpack(
                "{0}f".format(nnodeprop), self.fp.read(nnodeprop * self.RECORDSIZE)
            )
            self.prop[1].append(list(zip(self.propcode[1], rprops)))

        # links
        nlinkprop = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.propcode[2] = struct.unpack(
            "{0}i".format(nlinkprop), self.fp.read(nlinkprop * self.RECORDSIZE)
        )
        for i in range(self.swmm_nlinks):
            rprops = struct.unpack(
                "{0}f".format(nlinkprop), self.fp.read(nlinkprop * self.RECORDSIZE)
            )
            self.prop[2].append(list(zip(self.propcode[2], rprops)))

        self.vars = {}
        self.swmm_nsubcatchvars = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.vars[0] = struct.unpack(
            "{0}i".format(self.swmm_nsubcatchvars),
            self.fp.read(self.swmm_nsubcatchvars * self.RECORDSIZE),
        )

        self.nnodevars = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.vars[1] = struct.unpack(
            "{0}i".format(self.nnodevars),
            self.fp.read(self.nnodevars * self.RECORDSIZE),
        )

        self.nlinkvars = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.vars[2] = struct.unpack(
            "{0}i".format(self.nlinkvars),
            self.fp.read(self.nlinkvars * self.RECORDSIZE),
        )

        self.vars[3] = [0]

        self.nsystemvars = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.vars[4] = struct.unpack(
            "{0}i".format(self.nsystemvars),
            self.fp.read(self.nsystemvars * self.RECORDSIZE),
        )

        # System vars do not have names per se, but made names = number labels
        self.names[4] = [self.varcode[4][i] for i in self.vars[4]]

        self.startdate = struct.unpack("d", self.fp.read(2 * self.RECORDSIZE))[0]
        days = int(self.startdate)
        seconds = (self.startdate - days) * 86400
        self.startdate = datetime.datetime(1899, 12, 30) + datetime.timedelta(
            days=days, seconds=seconds
        )

        self.reportinterval = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.reportinterval = datetime.timedelta(seconds=self.reportinterval)

        # Calculate the bytes for each time period when
        # reading the computed results
        self.bytesperperiod = self.RECORDSIZE * (
            2
            + self.swmm_nsubcatch * self.swmm_nsubcatchvars
            + self.swmm_nnodes * self.nnodevars
            + self.swmm_nlinks * self.nlinkvars
            + self.nsystemvars
        )

    def type_check(self, itemtype):
        if itemtype in [0, 1, 2, 3, 4]:
            return itemtype
        try:
            typenumber = self.itemlist.index(itemtype)
        except ValueError:
            raise ValueError(
                """
*
*   Type argument "{0}" is incorrect.
*   Must be in "{1}".
*
""".format(
                    itemtype, list(range(5)) + self.itemlist
                )
            )
        return typenumber

    def name_check(self, itemtype, itemname):
        self.itemtype = self.type_check(itemtype)
        try:
            itemindex = self.names[self.itemtype].index(str(itemname))
        except (ValueError, KeyError):
            raise ValueError(
                """
*
*   {0} was not found in "{1}" list.
*
""".format(
                    itemname, itemtype
                )
            )
        return (itemname, itemindex)

    def get_swmm_results(self, itemtype, name, variableindex, period):
        if itemtype not in [0, 1, 2, 4]:
            raise ValueError(
                """
*
*   Type must be one of subcatchment (0), node (1). link (2), or system (4).
*   You gave "{0}".
*
""".format(
                    itemtype
                )
            )

        _, itemindex = self.name_check(itemtype, name)

        date_offset = self.startpos + period * self.bytesperperiod

        # Rewind
        self.fp.seek(date_offset, 0)

        date = struct.unpack("d", self.fp.read(2 * self.RECORDSIZE))[0]

        offset = date_offset + 2 * self.RECORDSIZE  # skip the date

        if itemtype == 0:
            offset = offset + self.RECORDSIZE * (itemindex * self.swmm_nsubcatchvars)
        elif itemtype == 1:
            offset = offset + self.RECORDSIZE * (
                self.swmm_nsubcatch * self.swmm_nsubcatchvars
                + itemindex * self.nnodevars
            )
        elif itemtype == 2:
            offset = offset + self.RECORDSIZE * (
                self.swmm_nsubcatch * self.swmm_nsubcatchvars
                + self.swmm_nnodes * self.nnodevars
                + itemindex * self.nlinkvars
            )
        elif itemtype == 4:
            offset = offset + self.RECORDSIZE * (
                self.swmm_nsubcatch * self.swmm_nsubcatchvars
                + self.swmm_nnodes * self.nnodevars
                + self.swmm_nlinks * self.nlinkvars
            )
        offset = offset + self.RECORDSIZE * variableindex

        self.fp.seek(offset, 0)
        value = struct.unpack("f", self.fp.read(self.RECORDSIZE))[0]
        return (date, value)

    def get_dates(self):
        """Return start and end date tuple."""
        begindate = datetime.datetime(1899, 12, 30)
        ntimes = list(range(self.swmm_nperiods))
        periods = [ntimes[0], ntimes[-1]]
        st_end = []
        for period in periods:
            date_offset = self.startpos + period * self.bytesperperiod
            self.fp.seek(date_offset, 0)
            day = struct.unpack("d", self.fp.read(2 * self.RECORDSIZE))[0]
            st_end.append(begindate + datetime.timedelta(days=int(day)))
        return st_end


@mando.command()
def about():
    """Display version number and system information."""
    tsutils.about(__name__)


@mando.command("catalog", formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(_LOCAL_DOCSTRINGS)
def catalog_cli(filename, itemtype="", tablefmt="csv_nos", header="default"):
    """List the catalog of objects in output file.

    This catalog list is all of the labels that can be used in the extract
    routine.

    Parameters
    ----------
    {filename}
    {itemtype}
    {tablefmt}
    {header}
    """
    if header == "default":
        header = ["TYPE", "NAME", "VARIABLE"]
    tsutils._printiso(
        catalog(filename, itemtype=itemtype), headers=header, tablefmt=tablefmt
    )


def catalog(filename, itemtype=""):
    """List the catalog of objects in output file."""
    obj = SwmmExtract(filename)
    if itemtype:
        typenumber = obj.type_check(itemtype)
        plist = [typenumber]
    else:
        plist = list(range(len(obj.itemlist)))
    collect = []
    for i in plist:
        typenumber = obj.type_check(obj.itemlist[i])
        for oname in obj.names[i]:
            if obj.itemlist[i] == "pollutant":
                continue
            if obj.itemlist[i] == "system":
                collect.append(["system", oname, oname])
                continue
            for j in obj.vars[typenumber]:
                collect.append([obj.itemlist[i], oname, obj.varcode[typenumber][j]])
    return collect


@mando.command("listdetail", formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(_LOCAL_DOCSTRINGS)
def listdetail_cli(filename, itemtype, name="", tablefmt="simple", header="default"):
    """List nodes and metadata in output file.

    Parameters
    ----------
    {filename}
    {itemtype}
    name : str
        [optional, default is '']

        Specific name to print only that entry.  This can be
        looked up using 'listvariables'.
    {tablefmt}
    {header}
    """
    tsutils._printiso(
        listdetail(filename, itemtype, name=name, header=header), tablefmt=tablefmt
    )


def listdetail(filename, itemtype, name="", header="default"):
    """List nodes and metadata in output file."""
    obj = SwmmExtract(filename)
    typenumber = obj.type_check(itemtype)
    if name:
        objectlist = [obj.name_check(itemtype, name)[0]]
    else:
        objectlist = obj.names[typenumber]

    propnumbers = obj.propcode[typenumber]
    if header == "default":
        header = ["#Name"] + [PROPCODE[typenumber][i] for i in propnumbers]

    collect = []
    for i, oname in enumerate(objectlist):
        printvar = [oname]
        for j in obj.prop[typenumber][i]:
            if j[0] == 0:
                try:
                    printvar.append(TYPECODE[typenumber][j[1]])
                except KeyError:
                    printvar.append(TYPECODE[typenumber][0])
            else:
                printvar.append(j[1])
        collect.append(printvar)
    df = pd.DataFrame(collect)
    cheader = []
    for head in header:
        if head not in cheader:
            cheader.append(head)
        else:
            cnt = cheader.count(head)
            cheader.append("{0}.{1}".format(head, cnt))
    df.columns = cheader
    return df


@mando.command("listvariables", formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(_LOCAL_DOCSTRINGS)
def listvariables_cli(filename, tablefmt="csv_nos", header="default"):
    """List variables available for each type.

    The type are "subcatchment", "node", "link", "pollutant", "system".

    Parameters
    ----------
    {filename}
    {tablefmt}
    {header}
    """

    tsutils._printiso(listvariables(filename, header=header), tablefmt=tablefmt)


def listvariables(filename, header="default"):
    """List variables available for each type."""
    obj = SwmmExtract(filename)
    if header == "default":
        header = ["TYPE", "DESCRIPTION", "VARINDEX"]
    # 'pollutant' really isn't it's own itemtype
    # but part of subcatchment, node, and link...
    collect = []
    for itemtype in ["subcatchment", "node", "link", "system"]:
        typenumber = obj.type_check(itemtype)

        for i in obj.vars[typenumber]:
            try:
                collect.append([itemtype, obj.varcode[typenumber][i].decode(), i])
            except (TypeError, AttributeError):
                collect.append([itemtype, str(obj.varcode[typenumber][i]), str(i)])
    return collect


@mando.command("stdtoswmm5", formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(_LOCAL_DOCSTRINGS)
def stdtoswmm5_cli(start_date=None, end_date=None, input_ts="-"):
    """Take the toolbox standard format and return SWMM5 format.

    Toolbox standard::

       Datetime, Column_Name
       2000-01-01 00:00:00 ,  45.6
       2000-01-01 01:00:00 ,  45.2
       ...

    SWMM5 format::

       ; comment line
       01/01/2000 00:00, 45.6
       01/01/2000 01:00, 45.2
       ...

    Parameters
    ----------
    {input_ts}
    {start_date}
    {end_date}
    """
    tsutils._printiso(
        stdtoswmm5(start_date=start_date, end_date=end_date, input_ts=input_ts)
    )


def stdtoswmm5(start_date=None, end_date=None, input_ts="-"):
    """Take the toolbox standard format and return SWMM5 format."""
    import csv

    sys.tracebacklimit = 1000
    tsd = tsutils.read_iso_ts(input_ts)[start_date:end_date]
    try:
        # Header
        print(";Datetime,", ", ".join(str(i) for i in tsd.columns))

        # Data
        cols = tsd.columns.tolist()
        tsd["date_tmp_tstoolbox"] = tsd.index.format(
            formatter=lambda x: x.strftime("%m/%d/%Y")
        )
        tsd["time_tmp_tstoolbox"] = tsd.index.format(
            formatter=lambda x: x.strftime("%H:%M:%S")
        )
        tsd.to_csv(
            sys.stdout,
            float_format="%g",
            header=False,
            index=False,
            cols=["date_tmp_tstoolbox", "time_tmp_tstoolbox"] + cols,
            sep=" ",
            quoting=csv.QUOTE_NONE,
        )
    except IOError:
        return


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(_LOCAL_DOCSTRINGS)
def getdata(filename, *labels):
    """DEPRECATED: Use 'extract' instead."""
    return extract(filename, *labels)


@mando.command("extract", formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(_LOCAL_DOCSTRINGS)
def extract_cli(filename, *labels):
    """Get the time series data for a particular object and variable.

    Parameters
    ----------
    {filename}
    {labels}

    """
    tsutils._printiso(extract(filename, *labels))


def extract(filename, *labels):
    """Get the time series data for a particular object and variable."""
    obj = SwmmExtract(filename)
    nlabels = []

    if isinstance(labels, (list, tuple)) and len(labels) == 1:
        labels = labels[0]

    for label in labels:
        words = tsutils.make_list(label, n=3)
        if None not in words:
            nlabels.append(words)
            continue
        try:
            words[2] = int(words[2])
            typenumber = obj.type_check(words[2])
            words[2] = obj.varcode[typenumber][words[2]]
        except (ValueError, TypeError):
            pass
        words = [str(i) if i is not None else None for i in words]
        res = tupleSearch(words, catalog(filename))
        nlabels = nlabels + res

    jtsd = []

    for itemtype, name, variablename in nlabels:
        typenumber = obj.type_check(itemtype)

        name = obj.name_check(itemtype, name)[0]

        inv_varcode_map = dict(
            zip(obj.varcode[typenumber].values(), obj.varcode[typenumber].keys())
        )
        try:
            variableindex = inv_varcode_map[int(variablename)]
        except ValueError:
            variableindex = inv_varcode_map[variablename]

        begindate = datetime.datetime(1899, 12, 30)
        dates = []
        values = []
        for time in range(obj.swmm_nperiods):
            date, value = obj.get_swmm_results(typenumber, name, variableindex, time)
            days = int(date)
            seconds = int((date - days) * 86400)
            extra = seconds % 10
            if extra != 0:
                if extra == 9:
                    seconds = seconds + 1
                if extra == 1:
                    seconds = seconds - 1
            date = begindate + datetime.timedelta(days=days, seconds=seconds)
            dates.append(date)
            values.append(value)
        if itemtype == "system":
            name = ""
        jtsd.append(
            pd.DataFrame(
                pd.Series(values, index=dates),
                columns=[
                    "{0}_{1}_{2}".format(
                        itemtype, name, obj.varcode[typenumber][variableindex]
                    )
                ],
            )
        )
    result = pd.concat(jtsd, axis=1).reindex(jtsd[0].index)
    return result


@tsutils.doc(_LOCAL_DOCSTRINGS)
def extract_arr(filename, *labels):
    """DEPRECATED: Extract and return the raw numpy array.

    DEPRECATED: Will be removed in future version. Instead use the following.

    >>> from swmmtoolbox import swmmtoolbox
    >>> na = swmmtoolbox.extract("filename.out", "link,41a,Flow_rate")[0].to_array()

    The `extract_arr` function will return the numpy array for the last entry
    in "*labels".

    Parameters
    ----------
    {filename}
    {labels}

    """
    warnings.warn(
        tsutils.error_wrapper(
            """
DEPRECATED: Will be removed in future version. Instead use the following.

>>> from swmmtoolbox import swmmtoolbox

>>> na = swmmtoolbox.extract("filename.out", "link,41a,Flow_rate")[0].to_array()
"""
        )
    )
    obj = SwmmExtract(filename)
    for label in labels:
        itemtype, name, variableindex = tsutils.make_list(label, n=3)
        typenumber = obj.type_check(itemtype)
        if itemtype != "system":
            name = obj.name_check(itemtype, name)[0]

        data = np.zeros(len(list(range(obj.swmm_nperiods))))

        for time in range(obj.swmm_nperiods):
            _, value = obj.get_swmm_results(typenumber, name, int(variableindex), time)
            data[time] = value

    return data


def main():
    if not os.path.exists("debug_swmmtoolbox"):
        sys.tracebacklimit = 0
    mando.main()


if __name__ == "__main__":
    main()

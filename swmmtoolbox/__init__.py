
from __future__ import print_function

# Example package with a console entry point
"""
Reads and formats data from the SWMM 5 output file.
"""

import sys
import struct
import datetime

import baker
import pandas as pd

import tstoolbox.tsutils as tsutils

PROPCODE = {0: {1: 'Area',
                },
            1: {0: 'Type',
                2: 'Inv_elev',
                3: 'Max_depth'
                },
            2: {0: 'Type',
                4: 'Inv_offset',
                3: 'Max_depth',
                5: 'Length'
                }
            }

# Names for the 'Node type' and 'Link type' codes above
TYPECODE = {0: {1: 'Area',
                },
            1: {0: 'Junction',  # nodes
                1: 'Outfall',
                2: 'Storage',
                3: 'Divider'
                },
            2: {0: 'Conduit',   # links
                1: 'Pump',
                2: 'Orifice',
                3: 'Weir',
                4: 'Outlet'
                }
            }

VARCODE = {0: {0: 'Rainfall',
               1: 'Snow_depth',
               2: 'Evaporation',
               3: 'Runoff_rate',
               4: 'Groundwater_outflow',
               5: 'Groundwater_elevation'
               },
           1: {0: 'Depth_above_invert',
               1: 'Hydraulic_head',
               2: 'Volume_stored_ponded',
               3: 'Lateral_inflow',
               4: 'Total_inflow',
               5: 'Flow_lost_flooding',
               },
           2: {0: 'Flow_rate',
               1: 'Flow_depth',
               2: 'Flow_velocity',
               3: 'Froude_number',
               4: 'Capacity',
               },
           3: {0: 'Concentration',  # Pollutant - not sure will use
               },
           4: {0: 'Air_temperature',
               1: 'Rainfall',
               2: 'Snow_depth',
               3: 'Evaporation_infiltration',
               4: 'Runoff',
               5: 'Dry_weather_inflow',
               6: 'Groundwater_inflow',
               7: 'RDII_inflow',
               8: 'User_direct_inflow',
               9: 'Total_lateral_inflow',
               10: 'Flow_lost_to_flooding',
               11: 'Flow_leaving_outfalls',
               12: 'Volume_stored_water',
               13: 'Evaporation_rate',
               }
           }

class SwmmExtract():
    def __init__(self, filename):

        self.RECORDSIZE = 4

        self.fp = open(filename, 'rb')

        self.fp.seek(-6*self.RECORDSIZE, 2)
        self.NamesStartPos, self.PropertiesStartPos, self.ResultsStartPos, self.nperiods, errcode, magic2 = struct.unpack('6i', self.fp.read(6*self.RECORDSIZE))

        self.fp.seek(0, 0)
        magic1 = struct.unpack('i', self.fp.read(self.RECORDSIZE))[0]

        if magic1 != 516114522:
            print('First magic number incorrect.')
            sys.exit(1)
        if magic2 != 516114522:
            print('Second magic number incorrect.')
            sys.exit(1)
        if errcode != 0:
            print('Error code in the output file indicates a problem with the run')
            sys.exit(1)
        if self.nperiods == 0:
            print('There are zero time periods in the output file')
            sys.exit(1)

        version, self.flowunits, self.nsubcatch, self.nnodes, self.nlinks, self.npolluts = struct.unpack('6i', self.fp.read(6*self.RECORDSIZE))

        self.itemlist = ['subcatchment', 'node', 'link', 'pollutant', 'system']

        # Read in the names
        self.fp.seek(self.NamesStartPos, 0)
        self.names = {0:[], 1:[], 2:[], 3:[], 4:[]}
        number_list = [self.nsubcatch, self.nnodes, self.nlinks, self.npolluts, self.npolluts]
        for i,j in enumerate(number_list):
            for k in range(j):
                stringsize = struct.unpack('i', self.fp.read(self.RECORDSIZE))[0]
                self.names[i].append(struct.unpack('{0}s'.format(stringsize), self.fp.read(stringsize))[0])

        # Read pollutant concentration codes = Number of pollutants * 4 byte integers
        self.pollutant_codes = struct.unpack('{0}i'.format(self.npolluts), self.fp.read(self.npolluts*self.RECORDSIZE))

        self.propcode = {}
        self.prop = {0: [], 1: [], 2: []}
        nsubprop = struct.unpack('i', self.fp.read(self.RECORDSIZE))[0]
        self.propcode[0] = struct.unpack('{0}i'.format(nsubprop), self.fp.read(nsubprop*self.RECORDSIZE))
        for i in range(self.nsubcatch):
            rprops = struct.unpack('{0}f'.format(nsubprop), self.fp.read(nsubprop*self.RECORDSIZE))
            self.prop[0].append(zip(self.propcode[0], rprops))

        nnodeprop = struct.unpack('i', self.fp.read(self.RECORDSIZE))[0]
        self.propcode[1] = struct.unpack('{0}i'.format(nnodeprop), self.fp.read(nnodeprop*self.RECORDSIZE))
        for i in range(self.nnodes):
            rprops = struct.unpack('i{0}f'.format(nnodeprop - 1), self.fp.read(nnodeprop*self.RECORDSIZE))
            self.prop[1].append(zip(self.propcode[1], rprops))

        nlinkprop = struct.unpack('i', self.fp.read(self.RECORDSIZE))[0]
        self.propcode[2] = struct.unpack('{0}i'.format(nlinkprop), self.fp.read(nlinkprop*self.RECORDSIZE))
        for i in range(self.nlinks):
            rprops = struct.unpack('i{0}f'.format(nlinkprop - 1), self.fp.read(nlinkprop*self.RECORDSIZE))
            self.prop[2].append(zip(self.propcode[2], rprops))

        self.vars = {}
        self.nsubcatchvars = struct.unpack('i', self.fp.read(self.RECORDSIZE))[0]
        self.vars[0] = struct.unpack('{0}i'.format(self.nsubcatchvars), self.fp.read(self.nsubcatchvars*self.RECORDSIZE))

        self.nnodevars = struct.unpack('i', self.fp.read(self.RECORDSIZE))[0]
        self.vars[1] = struct.unpack('{0}i'.format(self.nnodevars), self.fp.read(self.nnodevars*self.RECORDSIZE))

        self.nlinkvars = struct.unpack('i', self.fp.read(self.RECORDSIZE))[0]
        self.vars[2] = struct.unpack('{0}i'.format(self.nlinkvars), self.fp.read(self.nlinkvars*self.RECORDSIZE))

        self.vars[3] = [0]

        self.nsystemvars = struct.unpack('i', self.fp.read(self.RECORDSIZE))[0]
        self.vars[4] = struct.unpack('{0}i'.format(self.nsystemvars), self.fp.read(self.nsystemvars*self.RECORDSIZE))

        # System vars do not have names per se, but made names = number labels
        self.names[4] = [str(i) for i in self.vars[4]]

        self.startdate = struct.unpack('d', self.fp.read(2*self.RECORDSIZE))[0]
        days = int(self.startdate)
        seconds = (self.startdate - days)*86400
        self.startdate = datetime.datetime(1899,12,30) + datetime.timedelta(days = days, seconds = seconds)

        self.reportinterval = struct.unpack('i', self.fp.read(self.RECORDSIZE))[0]
        self.reportinterval = datetime.timedelta(seconds = self.reportinterval)

        # Calculate the bytes for each time period when reading the computed results
        self.bytesperperiod = 2*self.RECORDSIZE + self.RECORDSIZE*(
                                         self.nsubcatch*(self.nsubcatchvars + self.npolluts) +
                                         self.nnodes*(self.nnodevars + self.npolluts) +
                                         self.nlinks*(self.nlinkvars + self.npolluts) + self.nsystemvars)

    def TypeCheck(self, itemtype):
        if itemtype in [0, 1, 2, 3, 4]:
            return itemtype
        try:
            typenumber = self.itemlist.index(itemtype)
        except ValueError:
            print('Type argument is incorrect')
            sys.exit(1)
        return typenumber

    def NameCheck(self, itemtype, itemname):
        self.itemtype = self.TypeCheck(itemtype)
        try:
            itemindex = self.names[self.itemtype].index(itemname)
        except (ValueError, KeyError):
            print('%s was not found in %s list' % (itemname, itemtype))
            sys.exit(1)
        return (itemname, itemindex)

    def GetSwmmResults(self, type, name, variableindex, period):
        if type not in [0, 1, 2, 4]:
            print('Type must be one of subcatchment, node. link, or system')
            sys.exit(1)

        itemname, itemindex = self.NameCheck(type, name)

        date_offset = self.ResultsStartPos + period*self.bytesperperiod

        self.fp.seek(date_offset, 0)
        date = struct.unpack('d', self.fp.read(2*self.RECORDSIZE))[0]

        offset = date_offset + 2*self.RECORDSIZE  # skip the date

        if type == 0:
            offset = offset + self.RECORDSIZE*(
                               itemindex*(self.nsubcatchvars + self.npolluts)
                               )
        if type == 1:
            offset = offset + self.RECORDSIZE*(
                               self.nsubcatch*(self.nsubcatchvars + self.npolluts) +
                               itemindex*(self.nnodevars + self.npolluts)
                               )
        elif type == 2:
            offset = offset + self.RECORDSIZE*(
                               self.nsubcatch*(self.nsubcatchvars + self.npolluts) +
                               self.nnodes*(self.nnodevars + self.npolluts) +
                               itemindex*(self.nlinkvars + self.npolluts)
                               )
        elif type == 4:
            offset = offset + self.RECORDSIZE*(
                               self.nsubcatch*(self.nsubcatchvars + self.npolluts) +
                               self.nnodes*(self.nnodevars + self.npolluts) +
                               self.nlinks*(self.nlinkvars + self.npolluts)
                               )

        offset = offset + self.RECORDSIZE*variableindex

        self.fp.seek(offset, 0)
        value = struct.unpack('f', self.fp.read(self.RECORDSIZE))[0]
        return (date, value)

@baker.command
def list(filename, type=''):
    ''' List objects in output file
    :param filename: Filename of SWMM output file.
    '''
    obj = SwmmExtract(filename)
    if type:
        typenumber = obj.TypeCheck(type)
        plist = [typenumber]
    else:
        plist = range(len(obj.itemlist))
    print('TYPE, NAME')
    for i in plist:
        for oname in obj.names[i]:
            print('{0},{1}'.format(obj.itemlist[i],oname))

@baker.command
def listdetail(filename, type, name=''):
    ''' List nodes and metadata in output file
    :param filename: Filename of SWMM output file.
    :param type: Type to print out the table of (subcatchment, node, or link)
    :param name: Optional specfic name to print only that entry.
    '''
    obj = SwmmExtract(filename)
    typenumber = obj.TypeCheck(type)
    if name:
        objectlist = [obj.NameCheck(type, name)[0]]
    else:
        objectlist = obj.names[typenumber]
    propnumbers = obj.propcode[typenumber]
    headstr = ['#Name'] + [PROPCODE[typenumber][i] for i in propnumbers]
    headfmtstr = '{0:<25},{1:<8},' + ','.join(
            ['{'+str(i)+':>10}' for i in range(2,1+len(propnumbers))])
    print(headfmtstr.format(*tuple(headstr)))
    fmtstr = '{0:<25},{1:<8},' + ','.join(
            ['{'+str(i)+':10.2f}' for i in range(2,1+len(propnumbers))])
    for i,oname in enumerate(objectlist):
        printvar = [oname]
        for j in obj.prop[typenumber][i]:
            if j[0] == 0:
                printvar.append(TYPECODE[typenumber][j[1]])
            else:
                printvar.append(j[1])
        print(fmtstr.format(*tuple(printvar)))

@baker.command
def listvariables(filename):
    ''' List variables available for each type
    :param filename: Filename of SWMM output file.
    :param type: Type to print out the table of (subcatchment, node, link, pollutant, system)
    '''
    obj = SwmmExtract(filename)
    print('TYPE, DESCRIPTION, VARINDEX')
    for type in ['subcatchment', 'node', 'link', 'pollutant', 'system']:
        typenumber = obj.TypeCheck(type)
        for i in obj.vars[typenumber]:
            print('{0},{1},{2}'.format(type, VARCODE[typenumber][i], i))


@baker.command
def getdata(filename, *labels):
    ''' Get the time series data for a particular object and variable
    :param filename: Filename of SWMM output file.
    :param labels: The remaining arguments uniquely identify a time-series
        in the binary file.  The format is
        'TYPE,NAME,VARINDEX'.
        For example: 'node,C64,1 node,C63,1 ...'
        TYPE and NAME can be retrieved with
            'swmmtoolbox list filename.out'
        VARINDEX can be retrieved with
            'swmmtoolbox listvariables filename.out'
    '''
    obj = SwmmExtract(filename)
    for label in labels:
        type, name, variableindex = label.split(',')
        typenumber = obj.TypeCheck(type)
        if type != 'system':
            name = obj.NameCheck(type, name)[0]
        begindate = datetime.datetime(1899,12,30)

        dates = []
        values = []
        for time in range(obj.nperiods):
            date, value = obj.GetSwmmResults(typenumber, name, int(variableindex), time)
            days = int(date)
            seconds = (date - days)*86400
            date = begindate + datetime.timedelta(days = days, seconds = seconds)
            dates.append(date)
            values.append(value)
        jtsd = pd.DataFrame(pd.Series(values, index=dates),
                columns=['{0}_{1}_{2}'.format(type,name,VARCODE[typenumber][int(variableindex)])])
        try:
            result = result.join(jtsd)
        except NameError:
            result = jtsd
    tsutils.printiso(result)


def main():
    baker.run()

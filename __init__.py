#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright notice
# ----------------
#
# Copyright (C) 2014 Daniel Jung
# Contact: djungbremen@gmail.com
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
#
"""Create and display tables from various data structures.

Various data structures are considered: Lists containing lists, dictionaries
containing lists, lists containing dictionaries etc. The idea of this package
is to find the natural table-like representation for each of the considered
data structures.  The ultimate goal is to provide a function that can infer
an appropiate table form for the given data structure.

For each data structure one can think of, functions to create a table-like
representation shall be implemented, following a specific naming scheme:

    docl:
        dictionary of lists, each representing a column of data

    dorl:
        dictionary of lists, each representing a row of data

    dod:
        dictionary of dictionaries, forming a matrix with row and column titles

    lord:
        list of dictionaries, where each dictionary represents a row

    locd:
        list of dictionaries, where each dictionary represents a column

    ... to be continued ...

It is not planned to implement any sorting or filter functions. The user has to
pass data structures that are already ordered in the way he wishes. In the case
of dictionaries, :class:`collections.OrderedDict` can be used."""
# 2013-08-12 - 2013-08-13


"""

Conceptual thoughts
-------------------

Which possibilities do we have?

Say, a list of lists is given. What can we do with it to present it in a
reasonable way?
--> Either it is a list of rows or a list of columns.    locl, lorl

Then, if a list of dictionaries is given, what can we do?
--> Either it is a list of rows, with names columns, or a list of columns, with
    named rows.                                          lord, locd

How about a dictionary of lists?
--> Either it is a dictionary of named rows or a dictionary of named columns.
                                                         dorl, docl

If a dictionary of dictionaries is given:
--> Dictionary of named rows, for which the columns are named as well.
                                                         dord, docd

If only one dictionary is given, and the keys are 2-tuples:
--> Each 2-tuple contains the names of row and of column (like indices), and
    the data is arranged accordingly in a sparse matrix style.
                                                         do2t

Sets can be treated like lists, but the elements will be unordered. (The
responsibility remains with the user to first make a sorted list out of it.)
Frozen sets and tuples are of course treated like their ``unfrozen''
counterparts.

There could be a general function "table" that chooses an appropriate table
format automatically for the given data structure.

All functions just return the string that would draw the table on the screen if
printed. The terminal width can be set.

Could colors play some role?

A remapping of the row and column titles could be done.

A ``LaTeX output mode'' could be implemented (as well as a HTML mode).

Numbers should be formattable and right-aligned.

There could be support to print tree-like (hierarchical) data structures
(although it does not really fall under tables).

Think about configurable row and column separators, major as well as minor
ones, margin and padding, and frames.

Option to print titles in uppercase.

collections.OrderedDict may be used to force a specific row or column order
when using dictionaries.



"""

default_cellformat = {float: '% *g', int: '% *g', long: '% *g'}
csep = ' '


def formatted(obj, width=0):
    """Return string representation of obj, according to the formats
    specification."""
    f = default_cellformat.get(type(obj), '%- *s')
    return f % (width, obj) if '*' in f else f % obj


def docl(dict_of_lists, titles=False, cellformat=None):
    """Return table representation of the given dictionary of lists, where each
    list represents a named **column**. Include headrow if *titles* is
    *True*."""

    coltitles, columns = zip(*dict_of_lists.iteritems())
    rowcount = len(max(columns, key=len)) if columns else 0
    colcount = len(coltitles)

    # collect table data, row by row
    tabdata = []
    rind = 0
    for rind in xrange(rowcount):
        rowdata = []
        for clist in columns:
            cell = clist[rind] if rind < len(clist) else ''
            rowdata.append(cell)
        tabdata.append(rowdata)

    # determine maximum width of each column
    maxcolwidths = []
    data = tabdata + [coltitles] if titles else tabdata
    for cind in xrange(colcount):
        maxcwidth = len(max(data,
                            key=lambda rdata: len(formatted(rdata[cind], cellformat))))
        maxcolwidths.append(maxcwidth)

    # build string
    rowstrings = []
    if titles:
        titlestrings = []
        for title, maxcwidth in zip(coltitles, maxcolwidths):
            titlestrings.append(formatted(title, maxcwidth))
        rowstring = csep.join(titlestrings)
        rowstrings.append(rowstring)
    for rdata in tabdata:
        cellstrings = []
        for cell, maxcwidth in zip(rdata, maxcolwidths):
            cellstrings.append(formatted(cell, maxcwidth))
        rowstring = csep.join(cellstrings)
        rowstrings.append(rowstring)
    out = '\n'.join(rowstrings)
    return out


def lod(list_of_dicts, head=False, sort=None, reverse=False, sep=' ',
             columns=None):
    """Create a table out of a given list of dictionaries *list_of_dicts*,
    where each dictionary represents one table row. The dictionary keys contain
    the column titles. Return string.

    If *head* is *True*, show head row containing the column titles. *sep* is
    the string used for vertical separation between the cells. Filter columns
    by specifying a list *columns* of specific column titles.

    The rows can be sorted by setting *sort* to a certain column title. Higher
    order sort criteria can be set by setting *sort* with a list of column
    titles. The sort direction can be reversed using *reverse*."""

    # find all dictionary keys
    if columns is not None:
        allkeys = columns
    else:
        allkeys = []
        for d in list_of_dicts:
            for key in d.keys():
                if key not in allkeys:
                    allkeys.append(key)

    # find width of each column
    widths = {}
    for key in allkeys:
        if key not in widths:
            widths[key] = 0
        if head:
            widths[key] = len(str(key))
        for d in list_of_dicts:
            if key in d:
                width = len(str(d[key]))
                if width > widths[key]:
                    widths[key] = width

    # sort
    if sort is not None:
        if not isiterable(sort):
            sort = [sort]
        for key in sort:
            list_of_dicts.sort(key=items_of(key), reverse=reverse)

    # construct the table
    rows = []
    if head:
        row = sep.join(str(key).ljust(widths[key]) for key in allkeys)
        rows.append(row)
    for d in list_of_dicts:
        cells = []
        for key in allkeys:
            if key in d:
                cells.append(str(d[key]).ljust(widths[key]))
            else:
                cells.append(' '*widths[key])
        row = sep.join(cells)
        rows.append(row)
    out = '\n'.join(rows)
    return out


def tol(list_of_lists, sortind=None, floatformat='%g', intformat='%g'):

    """Create a table from a given tuple of lists. Each list represents one
    column. Return string."""
    raise NotImplementedError


def lot(list_of_tuples, sortind=None, floatformat='%g', intformat='%g'):

    """Create a table from the given list of tuples. Each tuple represents one
    line of the table. Return string."""
    raise NotImplementedError


def dod(dict_of_dicts, cols=None, rows=None, coltitles=True, fformat='%g',
             iformat='%g', lformat='%g', cformat='%g+%gj', colsep=' ',
             maxwidth=None):

    """Create a table from a given dictionary containing dictionaries, each
    nested dictionary representing a row. The keys of the outer dictionary
    become the row titles, while the keys of the nested dictionaries become the
    column titles. Return string.

    By default, rows and columns are sorted by column title (alphabetically).
    Alternatively, a certain order (and subset) can be defined using "cols" and
    "rows" (list of strings). Column titles can be switched off using
    "coltitles".

    The arguments "fformat", "iformat", "lformat" and "cformat" control the
    formatting of floats, integers, longs and complex numbers, respectively.
    The columns are separated by one space by default, which can be changed
    using "colsep". With "maxwidth", the output can be cut after a certain
    number of characters in each line, e.g. setting it to 80 could improve the
    output in most shell windows, but certain columns that do not fit into this
    width may then not be visible.

    """
    # 2013-08-12 - 2013-08-13

    # find string representation and alignment for all data
    strrep = {}
    align_right = {}
    for rowtit, row in dict_of_dicts.iteritems():
        strrep[rowtit] = {}
        align_right[rowtit] = {}
        for coltit, cell in row.iteritems():
            strrep[rowtit][coltit], align_right[rowtit][coltit] = \
                _formatcell(cell, fformat=fformat, iformat=iformat,
                            lformat=lformat, cformat=cformat)

    # get column titles
    if cols is None:
        coltits = set()
        for row in dict_of_dicts.values():
            coltits.update(row.keys())
        coltits = list(coltits)
        coltits.sort(key=lambda tit: tit.lower())
    else:
        coltits = cols

    # determine column widths
    rowtitw = len(max(strrep.keys(), key=len)) if strrep else 0
    colw = {}
    for coltit in coltits:
        if not coltit in colw:
            colw[coltit] = 0
        for row in strrep.values():
            if coltit in row:
                if coltitles and len(coltit) > colw[coltit]:
                    colw[coltit] = len(coltit)
                if len(row[coltit]) > colw[coltit]:
                    colw[coltit] = len(row[coltit])

    # build the table
    tablines = []

    if coltitles:
        rowcells = [' '*rowtitw]
        for coltit in coltits:
            cellstr = '%-*s' % (colw[coltit], coltit)
            rowcells.append(cellstr)
        tablines.append(colsep.join(rowcells))

    # get row titles
    if rows is None:
        rowtits = strrep.keys()
        rowtits.sort(key=lambda tit: tit.lower())
    else:
        rowtits = rows

    for rowtit in rowtits:
        if not rowtit in strrep:
            continue
        row = strrep[rowtit]
        rowcells = ['%-*s' % (rowtitw, rowtit)]
        for coltit in coltits:
            if coltit in row:
                if align_right[rowtit][coltit]:
                    cellstr = '%*s' % (colw[coltit], row[coltit])
                else:
                    cellstr = '%-*s' % (colw[coltit], row[coltit])
            else:
                cellstr = ' '*colw[coltit]
            rowcells.append(cellstr)
        tablines.append(colsep.join(rowcells)[:maxwidth])

    return '\n'.join(tablines)


def _formatcell(cell, fformat='%g', iformat='%g', cformat='%g+%gj',
                lformat='%g'):
    """Return string representation and alignment of cell data."""
    # 2013-08-12

    kwargs = dict(fformat=fformat, iformat=iformat, cformat=cformat,
                  lformat=lformat)
    if isinstance(cell, float):
        return fformat % cell, True
    elif isinstance(cell, int):
        return iformat % cell, True
    elif isinstance(cell, long):
        return lformat % cell, True
    elif isinstance(cell, complex):
        return cformat % (cell.real, cell.imag), True
    elif isinstance(cell, (list, tuple, set, frozenset)):
        return ', '.join([_formatcell(item, **kwargs)[0] for item in cell]), \
               False
    elif isinstance(cell, dict):
        return ', '.join(_formatcell(key, **kwargs)[0] +
                         '=' + _formatcell(value, **kwargs)[0]
                         for key, value in cell.iteritems()), False
    else:
        return str(cell), False



def isiterable(obj):
    """Check if an object is iterable. Return True for lists, tuples,
    dictionaries and numpy arrays (all objects that possess an __iter__
    method).  Return False for scalars (float, int, etc.), strings, bool and
    None."""
    # 2011-09-13
    # copied from tb.misc.isiterable on 2014-07-10
    # former tb.isiterable from 2011-01-27
    # former mytools.isiterable
    # Initial idea from
    # http://bytes.com/topic/python/answers/514838-how-test-if-object-sequence-
    # iterable:
    # return isinstance(obj, basestring) or getattr(obj, '__iter__', False)
    # I found this to be better:
    return not getattr(obj, '__iter__', False) is False


class items_of(object):
    """Instances of this class are callables which get a certain item of each
    element of a given iterable, and returns all items in form of a new
    iterable. If item does not exist and a default value is given, return that
    value."""
    # copied from frog.items_of on 2014-07-10

    def __init__(self, itemname, default=None, dtype=None):
        self.itemname = itemname
        self.default = default
        self.dtype = dtype

    def __call__(self, iterable):
        dtype = self.dtype or type(iterable)
        newiter = []
        for item in iterable:
            if self.default is not None:
                try:
                    value = item[self.itemname]
                except:
                    value = self.default
            else:
                print self.itemname
                value = item[self.itemname]
            newiter.append(value)
        return dtype(newiter)




import collections


class RowList(list):

    def append(self, value):
        if not isinstance(value, Row):
            raise TypeError, 'must be of type Row'
        list.append(self, value)

    def __setitem__(self, index, value):
        if not isinstance(value, Row):
            raise TypeError, 'must be of type Row'
        list.__setitem__(self, index, value)

    def __iadd__(self, other):
        if not isinstance(value, RowList):
            raise TypeError, 'must be of type RowList'
        list.__iadd__(self, other)


class ColumnList(list):

    def append(self, value):
        if not isinstance(value, Column):
            raise TypeError, 'must be of type Column'
        list.append(self, value)

    def __setitem__(self, index, value):
        if not isinstance(value, Column):
            raise TypeError, 'must be of type Column'
        list.__setitem__(self, index, value)

    def __iadd__(self, other):
        if not isinstance(value, ColumnList):
            raise TypeError, 'must be of type ColumnList'
        list.__iadd__(self, other)


class CellList(list):

    def append(self, value):
        if not isinstance(value, Cell):
            raise TypeError, 'must be of type Cell'
        list.append(self, value)

    def __setitem__(self, index, value):
        if not isinstance(value, Cell):
            raise TypeError, 'must be of type Cell'
        list.__setitem__(self, index, value)

    def __iadd__(self, other):
        if not isinstance(value, CellList):
            raise TypeError, 'must be of type CellList'
        list.__iadd__(self, other)


class Table(object):

    def __init__(self):
        self._rows = RowList()
        self._columns = ColumnList()

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, rowlist):
        if not isinstance(rowlist, RowList):
            raise TypeError, 'must be of type RowList'
        self._rows = rowlist

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, columnlist):
        if not isinstance(columnlist, ColumnList):
            raise TypeError, 'must be of type ColumnList'
        self._cells = columnlist


class Row(object):

    def __init__(self, table, cells=CellList(), title=None):
        self.table = table
        self.cells = cells
        self.title = title

    @property
    def cells(self):
        return self._cells

    @cells.setter
    def cells(self, celllist):
        if not isinstance(celllist, CellList):
            raise TypeError, 'must be of type CellList'
        self._cells = celllist

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, new):
        self._title = new

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, t):
        if not isinstance(t, Table):
            raise TypeError, 'must be of type Table'
        t.rows.append(self)  # but always append at the end?
        self._table = t

    def next(self):
        try:
            rows = self.table.rows
            index = rows.index(self)
            index += 1
            return rows[index]
        except:
            return None

    def previous(self):
        try:
            rows = self.table.rows
            index = rows.index(self)
            index -= 1
            if index < 0:
                return None
            else:
                return rows[index]
        except:
            return None


class Column(object):

    def __init__(self, table, cells=CellList(), title=None, align='left'):
        self.table = table
        self.cells = cells
        self.title = title
        self.align = align

    @property
    def cells(self):
        return self._cells

    @cells.setter
    def cells(self, celllist):
        if not isinstance(celllist, CellList):
            raise TypeError, 'must be of type CellList'
        self._cells = celllist

    @property
    def align(self):
        return self._align

    @align.setter
    def align(self, value):
        if value not in ['left', 'right', 'center', 'point']:
            raise ValueError, 'must be "left", "right", "center", or "point"'
        self._align = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, new):
        self._title = new

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, t):
        if not isinstance(t, Table):
            raise TypeError, 'must be of type Table'
        t.columns.append(self)  # but always append at the end?
        self._table = t

    def next(self):
        try:
            columns = self.table.columns
            index = columns.index(self)
            index += 1
            return columns[index]
        except:
            return None

    def previous(self):
        try:
            columns = self.table.columns
            index = columns.index(self)
            index -= 1
            if index < 0:
                return None
            else:
                return columns[index]
        except:
            return None

    def add_cell(self):

        # find row
        #if not self.cells or self.cells[-1].row.next



        #cell = Cell(row, self)
        pass


class Cell(object):

    def __init__(self, row, column, obj=None):
        self.obj = obj
        self.row = row
        self.column = column

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, row):
        if not isinstance(row, Row):
            raise TypeError, 'must be of type Row'
        row.cells.append(self)  # but always append at the end?
        self._row = row

    @property
    def column(self):
        return self._column

    @column.setter
    def column(self, column):
        if not isinstance(column, Column):
            raise TypeError, 'must be of type Column'
        column.cells.append(self)  # but always append at the end?
        self._column = column

    def __str__(self):
        return str(self.obj)

    def __len__(self):
        return len(str(self.obj))

    def width(self):
        return len(str(self.obj))

    def bottom(self):
        try:
            cells = self.row.cells
            index = cells.index(self)
            index += 1
            return cells[index]
        except:
            return None

    def top(self):
        try:
            cells = self.row.cells
            index = cells.index(self)
            index -= 1
            if index < 0:
                return None
            else:
                return cells[index]
        except:
            return None

    def right(self):
        try:
            cells = self.column.cells
            index = cells.index(self)
            index += 1
            return cells[index]
        except:
            return None

    def left(self):
        try:
            cells = self.column.cells
            index = cells.index(self)
            index -= 1
            if index < 0:
                return None
            else:
                return cells[index]
        except:
            return None

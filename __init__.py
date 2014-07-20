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

import collections


#default_cellformat = {float: '% *g', int: '% *g', long: '% *g'}
#csep = ' '
#
#
#def formatted(obj, width=0):
#    """Return string representation of obj, according to the formats
#    specification."""
#    f = default_cellformat.get(type(obj), '%- *s')
#    return f % (width, obj) if '*' in f else f % obj


#def docl(dict_of_lists, titles=False, cellformat=None):
#    """Return table representation of the given dictionary of lists, where
#    each list represents a named **column**. Include headrow if *titles* is
#    *True*."""
#
#    coltitles, columns = zip(*dict_of_lists.iteritems())
#    rowcount = len(max(columns, key=len)) if columns else 0
#    colcount = len(coltitles)
#
#    # collect table data, row by row
#    tabdata = []
#    rind = 0
#    for rind in xrange(rowcount):
#        rowdata = []
#        for clist in columns:
#            cell = clist[rind] if rind < len(clist) else ''
#            rowdata.append(cell)
#        tabdata.append(rowdata)
#
#    # determine maximum width of each column
#    maxcolwidths = []
#    data = tabdata + [coltitles] if titles else tabdata
#    for cind in xrange(colcount):
#        maxcwidth = len(max(data,
#                            key=lambda rdata: len(formatted(rdata[cind],
#                            cellformat))))
#        maxcolwidths.append(maxcwidth)
#
#    # build string
#    rowstrings = []
#    if titles:
#        titlestrings = []
#        for title, maxcwidth in zip(coltitles, maxcolwidths):
#            titlestrings.append(formatted(title, maxcwidth))
#        rowstring = csep.join(titlestrings)
#        rowstrings.append(rowstring)
#    for rdata in tabdata:
#        cellstrings = []
#        for cell, maxcwidth in zip(rdata, maxcolwidths):
#            cellstrings.append(formatted(cell, maxcwidth))
#        rowstring = csep.join(cellstrings)
#        rowstrings.append(rowstring)
#    out = '\n'.join(rowstrings)
#    return out


def docl(dict_of_lists, titles=False):
    """Return table representation of the given dictionary of lists, where each
    list represents a named **column**. Include headrow if *titles* is
    *True*."""

    table = Table()
    for title, data in dict_of_lists.iteritems():
        table.append_column(data, title)
    return table.display(titles=titles)


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


def autotable(data_structure, **kwargs):
    pass


#def _formatcell(cell, fformat='%g', iformat='%g', cformat='%g+%gj',
#                lformat='%g'):
#    """Return string representation and alignment of cell data."""
#    # 2013-08-12
#
#    kwargs = dict(fformat=fformat, iformat=iformat, cformat=cformat,
#                  lformat=lformat)
#    if isinstance(cell, float):
#        return fformat % cell, True
#    elif isinstance(cell, int):
#        return iformat % cell, True
#    elif isinstance(cell, long):
#        return lformat % cell, True
#    elif isinstance(cell, complex):
#        return cformat % (cell.real, cell.imag), True
#    elif isinstance(cell, (list, tuple, set, frozenset)):
#        return ', '.join([_formatcell(item, **kwargs)[0] for item in cell]), \
#               False
#    elif isinstance(cell, dict):
#        return ', '.join(_formatcell(key, **kwargs)[0] +
#                         '=' + _formatcell(value, **kwargs)[0]
#                         for key, value in cell.iteritems()), False
#    else:
#        return str(cell), False


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
                value = item[self.itemname]
            newiter.append(value)
        return dtype(newiter)


def all_of_type(seq, dtype):
    """Check if all items of the given sequence *seq* are of the type
    *dtype*. *dtype* can also be a list of possible types."""
    for item in seq:
        if not isinstance(item, dtype):
            return False
    return True


DEFAULT_ALIGN = 'left'


class CellDict(dict):
    """A mapping ``(row index, column index) --> cell object``."""

    def __init__(self, mapping_or_iterable=None, **kwargs):
        self._check_mapping_or_iterable(kwargs)
        if mapping_or_iterable:
            self._check_mapping_or_iterable(mapping_or_iterable)
            dict.__init__(self, mapping_or_iterable, **kwargs)
        else:
            dict.__init__(self, **kwargs)

    def __setitem__(self, key, value):
        self._check_key(key)
        self._check_value(value)
        dict.__setitem__(self, key, value)

    def __delitem__(self, inds):
        self.cells[inds].table = None
        dict.__delitem__(self, key)

    def _check_key(self, key):
        if not isiterable(key):
            raise TypeError('key must be iterable')
        if len(key) != 2:
            raise ValueError('key must have length 2')
        if not isinstance(key[0], int) \
                or not isinstance(key[1], int):
            raise TypeError('key must contain integers')

    def _check_value(self, value):
        if not isinstance(value, Cell):
            raise TypeError('value must be of type Cell')

    def _check_mapping_or_iterable(self, mapping_or_iterable):
        if isinstance(mapping_or_iterable, dict):
            for key, value in mapping_or_iterable.iteritems():
                self._check_key(key)
                self._check_value(value)
        else:
            for key, value in mapping_or_iterable:
                self._check_key(key)
                self._check_value(value)

    def index(self, cell):
        """Return indices (row, column) of the given cell object. Raise
        ValueError if the cell is not present."""
        if cell not in self.values():
            raise ValueError('%s is not in %s' % (cell, self))
        for inds, c in self.iteritems():
            if c is cell:
                return inds


class TitleDict(dict):
    """A mapping ``integer --> title``. Keys must be integer."""

    def __init__(self, mapping_or_iterable=None, **kwargs):
        self._check_mapping_or_iterable(kwargs)
        if mapping_or_iterable:
            self._check_mapping_or_iterable(mapping_or_iterable)
            dict.__init__(self, mapping_or_iterable, **kwargs)
        else:
            dict.__init__(self, **kwargs)

    def __setitem__(self, key, value):
        self._check_key(key)
        dict.__setitem__(self, key, value)

    def _check_key(self, key):
        if not isinstance(key, int):
            raise TypeError('key must be integer')

    def _check_mapping_or_iterable(self, mapping_or_iterable):
        if isinstance(mapping_or_iterable, dict):
            for key, value in mapping_or_iterable.iteritems():
                self._check_key(key)
        else:
            for key, value in mapping_or_iterable:
                self._check_key(key)


class AlignDict(dict):
    """A mapping ``integer --> string``. Keys must be integer, values must be
    one of the strings "left", "right", "center", or "point"."""

    def __init__(self, mapping_or_iterable=None, **kwargs):
        self._check_mapping_or_iterable(kwargs)
        if mapping_or_iterable:
            self._check_mapping_or_iterable(mapping_or_iterable)
            dict.__init__(self, mapping_or_iterable, **kwargs)
        else:
            dict.__init__(self, **kwargs)

    def __setitem__(self, key, value):
        self._check_key(key)
        self._check_value(value)
        dict.__setitem__(self, key, value)

    def _check_key(self, key):
        if not isinstance(key, int):
            raise TypeError('key must be integer')

    def _check_value(self, value):
        msg = 'value must be one of the strings "left", "right", ' + \
              '"center", or "point"'
        if not isinstance(value, basestring):
            raise TypeError(msg)
        if value not in ['left', 'right', 'center', 'point']:
            raise ValueError(msg)

    def _check_mapping_or_iterable(self, mapping_or_iterable):
        if isinstance(mapping_or_iterable, dict):
            for key, value in mapping_or_iterable.iteritems():
                self._check_key(key)
                self._check_value(value)
        else:
            for key, value in mapping_or_iterable:
                self._check_key(key)
                self._check_value(value)


class Table(object):

    def __init__(self, cells=CellDict(), rowtitles=TitleDict(),
                 coltitles=TitleDict(), colalign=AlignDict()):
        self._cells = cells
        self._rowtitles = rowtitles
        self._coltitles = coltitles
        self._colalign = colalign

    @property
    def cells(self):
        return self._cells

    @cells.setter
    def cells(self, celldict):
        if not isinstance(celldict, CellDict):
            raise TypeError('must be of type CellDict')
        self._cells = celldict

    @property
    def rowtitles(self):
        return self._rowtitles

    @rowtitles.setter
    def rowtitles(self, titles):
        if not isinstance(titles, TitleDict):
            raise TypeError('must be of type TitleDict')
        self._rowtitles = titles

    @property
    def coltitles(self):
        return self._coltitles

    @coltitles.setter
    def coltitles(self, titles):
        if not isinstance(titles, TitleDict):
            raise TypeError('must be of type TitleDict')
        self._coltitles = titles

    @property
    def colalign(self):
        return self._colalign

    @colalign.setter
    def colalign(self, alignments):
        if not isinstance(colalign, AlignDict):
            raise TypeError('must be of type AlignDict')
        self._colalign = alignments

    def nrows(self):
        rowinds = self.rowinds()
        h = max(rowinds) - min(rowinds) + 1 if rowinds else 0
        return h

    def ncols(self):
        colinds = self.colinds()
        w = max(colinds) - min(colinds) + 1 if colinds else 0
        return w

    def size(self):
        """Return size of the table in the form (number of rows, number of
        columns), excluding titles."""
        rowinds, colinds = self.rowinds_and_colinds()
        h = max(rowinds) - min(rowinds) + 1 if rowinds else 0
        w = max(colinds) - min(colinds) + 1 if colinds else 0
        return h, w

    def top(self):
        rowinds = self.rowinds()
        return min(rowinds) if rowinds else None

    def bottom(self):
        rowinds = self.rowinds()
        return max(rowinds) if rowinds else None

    def left(self):
        colinds = self.colinds()
        return min(colinds) if colinds else None

    def right(self):
        colinds = self.colinds()
        return max(colinds) if colinds else None

    def rowinds(self):
        keys = self.cells.keys()
        rowinds, colinds = zip(*keys) if keys else ((), ())
        rowinds = list(rowinds)
        rowinds.sort()
        return rowinds

    def colinds(self):
        keys = self.cells.keys()
        rowinds, colinds = zip(*keys) if keys else ((), ())
        colinds = list(colinds)
        colinds.sort()
        return colinds

    def rowinds_and_colinds(self):
        keys = self.cells.keys()
        rowinds, colinds = zip(*keys) if keys else ((), ())
        rowinds = list(rowinds)
        rowinds.sort()
        colinds = list(colinds)
        colinds.sort()
        return rowinds, colinds

    def column(self, index):
        out = []
        for (r, c), cell in self.cells.iteritems():
            if c == index:
                out.append(cell)
        out.sort(key=lambda cell: cell.row)
        return out

    def row(self, index):
        out = []
        for (r, c), cell in self.cells.iteritems():
            if r == index:
                out.append(cell)
        out.sort(key=lambda cell: cell.column)
        return out

    def insert_cell(self, (row, column), data=None):
        c = Cell(self, (row, column), data=data)
        self.cells[(row, column)] = c

    def insert_column(self, index, data, title=None, align=None, startrow=0):
        colind = index
        for i, d in enumerate(data):
            self.insert_cell((startrow+i, colind), d)
        if title is not None:
            self.coltitles[colind] = title
        if align is not None:
            self.colalign[colind] = align

    def append_column(self, data, title=None, align=None, startrow=0):
        right = self.right()
        colind = right+1 if right is not None else 0
        self.insert_column(colind, data=data, title=title, align=align,
                           startrow=startrow)

    def insert_row(self, index, data, title=None, startcol=0):
        rowind = index
        for i, d in enumerate(data):
            self.insert_cell((rowind, startcol+i), d)
        if title is not None:
            self.rowtitles[rowind] = title

    def append_row(self, data, title=None, startcol=0):
        bottom = self.bottom()
        rowind = bottom + 1 if bottom is not None else 0
        self.insert_row(rowind, data=data, title=title, startcol=startcol)

    _mergedefault = {('-', ' '): '-', ('=', ' '): '=',
                     ('-', ''): '-', ('=', ''): '='}
    _mergetop = _mergedefault.copy()
    _mergetop.update({})
    _mergebottom = _mergedefault.copy()
    _mergebottom.update({})
    _mergeleft = _mergedefault.copy()
    _mergeleft.update({})
    _mergeright = _mergedefault.copy()
    _mergeright.update({})

    _mergebottomleft = _mergedefault.copy()
    _mergebottomleft.update({})
    _mergebottomright = _mergedefault.copy()
    _mergebottomright.update({})
    _mergetopleft = _mergedefault.copy()
    _mergetopleft.update({})
    _mergetopright = _mergedefault.copy()
    _mergetopright.update({})

    _mergecenter = _mergedefault.copy()
    _mergecenter.update({('-', '|'): '+', ('=', '|'): '#'})

    def _merge(self, hsep, vsep, pos='center'):
        mergedict = getattr(self, '_merge'+pos)
        return mergedict.get((hsep, vsep), ' ')

    def make(self, titles=False, bh='', bv='', padding=0, ph=0, pv=0,
             autoalign=True, rowtitles=False, coltitles=False, vcsep=' ',
             hcsep='', vtsep=' ', htsep='', borderleft='', borderright='',
             bordertop='', borderbottom='', paddingleft=0, paddingright=0,
             paddingtop=0, paddingbottom=0):

        #
        # to do:
        # - respect vertical padding
        # - cut table representation according to terminal width
        #

        if titles:
            rowtitles = True
            coltitles = True

        if bh:
            bordertop = bh
            borderbottom = bh

        if bv:
            borderleft = bv
            borderright = bv

        if pv:
            paddingtop = pv
            paddingbottom = pv

        if ph:
            paddingleft = ph
            paddingright = ph

        if padding:
            paddingleft = padding
            paddingright = padding
            paddingtop = padding
            paddingbottom = padding

        if not isinstance(vcsep, basestring) or len(vcsep) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(vtsep, basestring) or len(vtsep) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(hcsep, basestring) or len(hcsep) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(htsep, basestring) or len(htsep) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(borderleft, basestring) or len(borderleft) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(borderright, basestring) or len(borderright) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(bordertop, basestring) or len(bordertop) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(borderbottom, basestring) or len(borderbottom) > 1:
            raise ValueError, 'must be a string no longer than one character'

        startcol = self.left()
        if startcol is None:
            return ''
        endcol = self.right()
        if endcol is None:
            return ''
        startrow = self.top()
        if startrow is None:
            return ''
        endrow = self.bottom()
        if endrow is None:
            return ''

        rowtitlescolwidth = self.rowtitlescolwidth()

        # automatically infer alignment from data
        colalign = self.colalign
        if autoalign:
            for colind in xrange(startcol, endcol+1):
                if colind in colalign:
                    continue
                cells = self.column(colind)
                data = [cell.data for cell in cells]
                if all_of_type(data, float):
                    colalign[colind] = 'point'
                elif all_of_type(data, (int, float, long, complex)):
                    colalign[colind] = 'right'

        # create matrix of table cells
        allcolstrings = [self.colstrings(colind, withtitle=coltitles,
                                         colalign=colalign)
                         for colind in xrange(startcol, endcol+1)]

        # change datastructure to represent a list of rows instead of a list of
        # columns
        allrowstrings = []
        for r in xrange(len(allcolstrings[0])):
            rowstrings = []
            for c in xrange(len(allcolstrings)):
                rowstrings.append(allcolstrings[c][r])
            allrowstrings.append(rowstrings)

        # start constructing the table
        rows = []

        # top border
        if bordertop:
            row = self._bordertopstring(allrowstrings, borderleft, borderright,
                                        bordertop, rowtitles, paddingleft,
                                        paddingright, vcsep, vtsep)
            rows.append(row)

        # column titles
        if coltitles:
            row = self._coltitlesrowstring(rowtitles, borderleft,
                                            borderright, paddingleft,
                                            paddingright, vcsep, vtsep)
            rows.append(row)
            if htsep:
                row = self._coltitlessepstring(allrowstrings, rowtitles,
                                            borderleft, borderright,
                                            paddingleft, paddingright, htsep,
                                            vcsep, vtsep)
                rows.append(row)

        # main rows (first)
        if len(allrowstrings) > 0:
            rowtitle = self.rowtitles.get(self.top(), ' '*rowtitlescolwidth)
            row = self._datarowstring(allrowstrings[0], rowtitle, borderleft,
                                      borderright, rowtitles, paddingleft,
                                      paddingright, vcsep, vtsep)
            rows.append(row)

        # main rows (remaining)
        for rowind, rowstrings in enumerate(allrowstrings[1:], 1):
            rowtitle = self.rowtitles.get(rowind, ' '*rowtitlescolwidth)
            if hcsep:
                row = self._datasepstring(rowstrings, rowtitles, borderleft,
                                          borderright, paddingleft,
                                          paddingright, hcsep, vcsep, vtsep)


                rows.append(row)
            row = self._datarowstring(rowstrings, rowtitle, borderleft,
                                      borderright, rowtitles, paddingleft,
                                      paddingright, vcsep, vtsep)
            rows.append(row)

        # bottom border
        if borderbottom:
            row = self._borderbottomstring(allrowstrings, borderleft,
                                           borderright, borderbottom,
                                           rowtitles, paddingleft,
                                           paddingright, vcsep, vtsep)
            rows.append(row)

        # return complete string representation of the table
        return '\n'.join(rows)

    def dimensions(self, **kwargs):
        """Get table dimensions (the space needed to print the table) in the
        form (number of terminal rows, number of terminal columns). All keyword
        arguments are passed to :py:meth:`Table.make`."""
        strrep = self.make(**kwargs)
        if not strrep:
            return 0, 0
        lines = strrep.split('\n')
        return len(lines), len(lines[0]) if lines else 0

    def _coltitlessepstring(self, allrowstrings, rowtitles, borderleft,
                            borderright, paddingleft, paddingright, htsep,
                            vcsep, vtsep):
        row = ''

        # left
        if borderleft:
            row += self._merge(borderleft, htsep, 'left')
        if rowtitles:
            row += htsep*paddingleft
            row += htsep*self.rowtitlescolwidth()
            row += htsep*paddingright
            row += self._merge(htsep, vtsep, 'center')

        # main
        parts = []
        for rowstring in allrowstrings[0]:
            part = ''
            part += htsep*paddingleft
            part += htsep*len(rowstring)
            part += htsep*paddingright
            parts.append(part)
        sep = self._merge(htsep, vcsep, 'center')
        row += sep.join(parts)

        # right
        if borderright:
            row += self._merge(htsep, borderright, 'right')

        return row

    def _datasepstring(self, rowstrings, rowtitles, borderleft, borderright,
                       paddingleft, paddingright, hcsep, vcsep, vtsep):
        row = ''

        # left
        if borderleft:
            row += self._merge(borderleft, hcsep, 'left')
        if rowtitles:
            row += hcsep*paddingleft
            row += hcsep*self.rowtitlescolwidth()
            row += hcsep*paddingright
            row += self._merge(hcsep, vtsep, 'center')

        # main
        parts = []
        for rowstring in rowstrings:
            part = ''
            part += hcsep*paddingleft
            part += hcsep*len(rowstring)
            part += hcsep*paddingright
            parts.append(part)
        sep = self._merge(hcsep, vcsep, 'center')
        row += sep.join(parts)

        # right
        if borderright:
            row += self._merge(hcsep, borderright, 'right')

        return row

    def _coltitlesrowstring(self, rowtitles, borderleft, borderright,
                            paddingleft, paddingright, vcsep, vtsep):
        row = ''

        # left
        if borderleft:
            row += borderleft
        if rowtitles:
            row += ' '*paddingleft
            row += ' '*self.rowtitlescolwidth()
            row += ' '*paddingright
            row += vtsep

        # main
        parts = []
        for coltitle in self.coltitlestrings():
            part = ''
            part += ' '*paddingleft
            part += coltitle
            part += ' '*paddingright
            parts.append(part)
        row += vcsep.join(parts)

        # right
        if borderright:
            row += borderright

        return row

    def _bordertopstring(self, allrowstrings, borderleft, borderright,
                         bordertop, rowtitles, paddingleft, paddingright,
                         vcsep, vtsep):
        row = ''

        # left
        if borderleft:
            row += self._merge(bordertop, borderleft, 'topleft')
        if rowtitles:
            row += bordertop*paddingleft
            row += bordertop*self.rowtitlescolwidth()
            row += bordertop*paddingright
            row += self._merge(bordertop, vtsep, 'top')

        # main
        parts = []
        for rowstring in allrowstrings[0]:
            part = ''
            part += bordertop*paddingleft
            part += bordertop*len(rowstring)
            part += bordertop*paddingright
            parts.append(part)
        sep = self._merge(bordertop, vcsep, 'top')
        row += sep.join(parts)

        # right
        if borderright:
            row += self._merge(bordertop, borderright, 'topright')

        return row

    def _borderbottomstring(self, allrowstrings, borderleft, borderright,
                         borderbottom, rowtitles, paddingleft, paddingright,
                         vcsep, vtsep):
        row = ''

        # left
        if borderleft:
            row += self._merge(borderbottom, borderleft, 'bottomleft')
        if rowtitles:
            row += borderbottom*paddingleft
            row += borderbottom*self.rowtitlescolwidth()
            row += borderbottom*paddingright
            row += self._merge(borderbottom, vtsep, 'bottom')

        # main
        parts = []
        for rowstring in allrowstrings[0]:
            part = ''
            part += borderbottom*paddingleft
            part += borderbottom*len(rowstring)
            part += borderbottom*paddingright
            parts.append(part)
        sep = self._merge(borderbottom, vcsep, 'bottom')
        row += sep.join(parts)

        # right
        if borderright:
            row += self._merge(borderbottom, borderright, 'bottomright')

        return row

    def _datarowstring(self, rowstrings, rowtitle, borderleft, borderright,
                       rowtitles, paddingleft, paddingright, vcsep, vtsep):
        row = ''

        # left
        if borderleft:
            row += borderleft
        if rowtitles:
            row += ' '*paddingleft
            row += rowtitle
            row += ' '*paddingright
            row += vtsep

        # main
        parts = []
        for rowstring in rowstrings:
            part = ''
            part += ' '*paddingleft
            part += rowstring
            part += ' '*paddingright
            parts.append(part)
        row += vcsep.join(parts)

        # right
        if borderright:
            row += borderright

        return row

    def rowtitlescolwidth(self):
        return max(len(str(rowtitle))
                   for rowtitle in self.rowtitles.values()) \
            if self.rowtitles else 0

    def rowtitlescolstrings(self):
        start = self.top()
        end = self.bottom()
        out = []
        rowtitlescolwidth = self.rowtitlescolwidth()
        for rowind in xrange(start, end+1):
            if not rowind in self.rowtitles:
                out.append(' '*rowtitlescolwidth)
                continue
            rowtitle = str(self.rowtitles[rowind])
            out.append(rowtitle.ljust(rowtitlescolwidth))
        return out

    def coltitlestrings(self, colalign=None):
        start = self.left()
        end = self.right()
        out = []
        for colind in xrange(start, end+1):
            colwidth = self.colwidth(colind, withtitle=True, colalign=colalign)
            if not colind in self.coltitles:
                out.append(' '*colwidth)
                continue
            coltitle = str(self.coltitles[colind])
            out.append(coltitle.ljust(colwidth))
        return out

    def colstrings(self, index, withtitle=False, colalign=None):
        out = []
        if colalign is None:
            colalign is self.colalign
        align = colalign.get(index, DEFAULT_ALIGN)
        start = self.top()
        end = self.bottom()
        colwidth = self.colwidth(index, withtitle=withtitle, colalign=colalign)
        if align == 'point':
            colwidth_before = self.colwidth_before_point(index)
            colwidth_after = self.colwidth_after_point(index)
            for rowind in xrange(start, end+1):
                if (rowind, index) not in self.cells:
                    out.append(' '*colwidth)
                    continue
                cell = self.cells[rowind, index]
                before, after = cell.splitpoint()
                before = before.rjust(colwidth_before)
                after = after.ljust(colwidth_after)
                point = '.' if '.' in str(cell) else ' '
                out.append(before + point + after)
        elif align == 'left':
            for rowind in xrange(start, end+1):
                if (rowind, index) not in self.cells:
                    out.append(' '*colwidth)
                    continue
                cell = self.cells[rowind, index]
                out.append(str(cell).ljust(colwidth))
        elif align == 'right':
            for rowind in xrange(start, end+1):
                if (rowind, index) not in self.cells:
                    out.append(' '*colwidth)
                    continue
                cell = self.cells[rowind, index]
                out.append(str(cell).rjust(colwidth))
        elif align == 'center':
            for rowind in xrange(start, end+1):
                if (rowind, index) not in self.cells:
                    out.append(' '*colwidth)
                    continue
                cell = self.cells[rowind, index]
                space = (colwidth - len(cell))
                first = len(cell) + space/2
                out.append(str(cell).ljust(first).rjust(colwidth))
        return out

    def colwidth_before_point(self, index):
        cells = self.column(index)
        return max(cell.width_before_point() for cell in cells) if cells else 0

    def colwidth_after_point(self, index):
        cells = self.column(index)
        return max(cell.width_after_point() for cell in cells) if cells else 0

    def colwidth(self, index, withtitle=False, colalign=None):
        cells = self.column(index)
        if colalign is None:
            colalign = self.colalign
        align = colalign.get(index, DEFAULT_ALIGN)
        if align == 'point':
            maxcellwidth = self.colwidth_before_point(index) + 1 \
                + self.colwidth_after_point(index)
        else:
            maxcellwidth = max(cell.width() for cell in cells) if cells else 0
        if withtitle and index in self.coltitles \
                and len(str(self.coltitles[index])) > maxcellwidth:
            maxcellwidth = len(str(self.coltitles[index]))
        return maxcellwidth

    def colwidths(self, withtitle=False, colalign=None):
        start = self.left()
        end = self.right()
        out = []
        for colind in xrange(start, end+1):
            out.append(self.colwidth(colind, withtitle=withtitle,
                                     colalign=colalign))
        return out


class Cell(object):

    _instance_count = 0

    def __init__(self, table, (row, column), data=None):
        self._data = data
        self._table = table
        self.table.cells[(row, column)] = self
        self._instance_id = self._instance_count
        self.__class__._instance_count += 1

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, t):
        if not isinstance(t, (Table, type(None))):
            raise TypeError('must be of type Table or None')
        try:
            inds = self._table.cells.index(self)
            del self._table.cells[inds]
        except:
            pass
        self._table = t
        if t is not None:
            t.cells[inds] = self

    @property
    def instance_count(self):
        return self.__class__._instance_count

    @property
    def instance_id(self):
        return self._instance_id

    def inds(self):
        return self.table.cells.index(self)

    def rowind(self):
        return self.table.cells.index(self)[0]

    def colind(self):
        return self.table.cells.index(self)[1]

    def column(self):
        return self.table.column(self.colind())

    def row(self):
        return self.table.row(self.rowind())

    def align(self):
        return self.table.colalign.get(self.colind(), DEFAULT_ALIGN)

    def __str__(self):
        return str(self.data).strip()

    def __len__(self):
        return len(str(self))

    def width(self):
        return len(self)

    def splitpoint(self):
        parts = str(self).split('.', 1)
        if len(parts) < 2:
            parts.append('')
        return parts

    def width_before_point(self):
        return len(self.splitpoint()[0])

    def width_after_point(self):
        return len(self.splitpoint()[1])

    def width_before_and_after_point(self):
        parts = self.splitpoint()
        return len(parts[0]), len(parts[1])

    def __repr__(self):
        return '<Cell%i>' % self.instance_id

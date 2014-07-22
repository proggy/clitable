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
"""Create table representations from various data structures.

Various data structures are considered: Lists containing lists, dictionaries
containing lists, lists containing dictionaries etc. The idea of this package
is to find the natural table-like representation for each of the considered
data structures.  The function :func:`autotable` is provided that can infer an
appropiate table form the given data structure.

It has been attempted to find the natural tabular representation of many
possible data structures. For each kind of data structure, specialized
functions exist:

    :func:`docl`:
        dictionary of lists, where each list represents a named column

    :func:`dorl`:
        dictionary of lists, where each list represents a named row

    :func:`locl`:
        list of lists, where each list represents a column

    :func:`lorl`:
        list of lists, where each list represents a row

    :func:`locd`:
        list of dictionaries, where each dictionary represents a column

    :func:`lord`:
        list of dictionaries, where each dictionary represents a row

    :func:`docd`:
        dictionary of dictionaries, where each dictionary represents a named
        column

    :func:`dord`:
        dictionary of dictionaries, where each dictionary represents a named
        row

There are no ambitions to implement any sorting or filter options.  Data
structures have to be passed already in an ordered way. Tip: In the case of
dictionaries, :class:`collections.OrderedDict` can be used to force a certain
row or column order.

For absolute fine control, the :class:`Table` class can be used directly to
construct the table by hand."""
# 2013-08-12 - 2013-08-13

import presets

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

If three lists are given, the first could contain the row index, the second the
column index, and the third the respective data value.

Sets can be treated like lists, but the elements will be unordered. (The
responsibility remains with the user to first make a sorted list out of it.)
Frozen sets and tuples are of course treated like their ``unfrozen''
counterparts.

There could be a general function "autotable" that chooses an appropriate table
format automatically for a given data structure.

All functions return just the string that would draw the table on the screen if
printed. The terminal width can be set to cut the table.

Could colors play some role? Should the module :mod:`ansicolor` be used to
compute the actual length of the strings? (unwanted dependency...)

A remapping of the row and column titles could be done.

A LaTeX output mode could be implemented (as well as a HTML mode).

Numbers should be formattable and right-aligned.

There could be support to print tree-like (hierarchical) data structures
(although it is not really a table).

Think about configurable row and column separators, major as well as minor
ones, margin and padding, and frames.

Option to print titles in uppercase? No, the user can do that himself.

collections.OrderedDict can be used to force a specific row or column order
when using dictionaries. No sorting options are neccessary.

"""


DEFAULT_ALIGN = 'left'


def autotable(data_structure, **kwargs):
    """Generate table representation of the given data structure. Choose one of
    the specialized functions *docl*, *dorl*, etc. based on the given data
    structure. Keyword arguments are passed to :py:meth:`Table.make`."""
    if isdict(data_structure):
        if alldict(data_structure.values()):
            # decide if rowwise or columnwise is best
            func1 = docd
            func2 = dord
        elif alliter(data_structure.values()):
            # decide if rowwise or columnwise is best
            func1 = docl
            func2 = dorl
        else:
            raise TypeError('must contain dictionaries or iterables')
    elif isiter(data_structure):
        if alldict(data_structure):
            # decide if rowwise or columnwise is best
            func1 = locd
            func2 = lord
        elif alliter(data_structure):
            # decide if rowwise or columnwise is best
            func1 = locl
            func2 = lorl
        else:
            raise TypeError('must contain dictionaries or iterables')
    else:
        raise TypeError('must be of type dict or iterable')
    s1 = func1(data_structure, **kwargs)
    s2 = func2(data_structure, **kwargs)
    width1 = len(s1.split('\n')[0])
    width2 = len(s2.split('\n')[0])
    if width1 > 80 and width2 <= 80:
        func = func2
    elif width2 > 80 and width1 <= 80:
        func = func1
    elif width1 > 80 and width2 > 80:
        if width1 > width2:
            func = func2
        else:
            func = func1
    else:
        if width1 > width2:
            func = func1
        else:
            func = func2
    return func(data_structure, **kwargs)


def docl(dict_of_lists, **kwargs):
    """Return table representation of the given dictionary of lists, where each
    list represents a named **column**. Keyword arguments are passed to
    :py:meth:`Table.make`."""

    table = Table()
    for title, data in dict_of_lists.iteritems():
        table.append_column(data, title)
    return table.make(**kwargs)


def dorl(dict_of_lists, **kwargs):
    """Return table representation of the given dictionary of lists, where each
    list represents a named **row**. Keyword arguments are passed to
    :py:meth:`Table.make`."""

    table = Table()
    for title, data in dict_of_lists.iteritems():
        table.append_row(data, title)
    return table.make(**kwargs)


def locl(list_of_lists, **kwargs):
    """Return table representation of the given list of lists, where each list
    represents a **column**. Keyword arguments are passed to
    :py:meth:`Table.make`."""

    table = Table()
    for data in list_of_lists:
        table.append_column(data)
    return table.make(**kwargs)


def lorl(list_of_lists, **kwargs):
    """Return table representation of the given list of lists, where each list
    represents a **row**. Keyword arguments are passed to
    :py:meth:`Table.make`."""

    table = Table()
    for data in list_of_lists:
        table.append_row(data)
    return table.make(**kwargs)


def locd(list_of_dicts, **kwargs):
    """Return table representation of the given list of dictionaries, where
    each dictionary represents a **column**. Keyword arguments are passed to
    :py:meth:`Table.make`."""
    allrowtitles = []
    for coldata in list_of_dicts:
        for rowtitle in coldata.keys():
            if not rowtitle in allrowtitles:
                allrowtitles.append(rowtitle)
    table = Table()
    for colind, coldata in enumerate(list_of_dicts):
        for rowind, rowtitle in enumerate(allrowtitles):
            if rowtitle in coldata:
                table.insert_cell((rowind, colind), coldata[rowtitle])
    for rowind, rowtitle in enumerate(allrowtitles):
        table.rowtitles[rowind] = rowtitle
    return table.make(**kwargs)


def lord(list_of_dicts, **kwargs):
    """Return table representation of the given list of dictionaries, where
    each dictionary represents a **row**. Keyword arguments are passed to
    :py:meth:`Table.make`."""
    allcoltitles = []
    for rowdata in list_of_dicts:
        for coltitle in rowdata.keys():
            if not coltitle in allcoltitles:
                allcoltitles.append(coltitle)
    table = Table()
    for rowind, rowdata in enumerate(list_of_dicts):
        for colind, coltitle in enumerate(allcoltitles):
            if coltitle in rowdata:
                table.insert_cell((rowind, colind), rowdata[coltitle])
    for colind, coltitle in enumerate(allcoltitles):
        table.coltitles[colind] = coltitle
    return table.make(**kwargs)


def docd(dict_of_dicts, **kwargs):
    """Return table representation of the given dictionary of dictionaries,
    where each dictionary represents a **column**. Keyword arguments are passed
    to :py:meth:`Table.make`."""
    allrowtitles = []
    for coldata in dict_of_dicts.values():
        for rowtitle in coldata.keys():
            if not rowtitle in allrowtitles:
                allrowtitles.append(rowtitle)
    table = Table()
    allcoltitles = dict_of_dicts.keys()
    for colind, (coltitle, coldata) in enumerate(dict_of_dicts.iteritems()):
        table.coltitles[colind] = coltitle
        for rowtitle, celldata in coldata.iteritems():
            rowind = allrowtitles.index(rowtitle)
            table.insert_cell((rowind, colind), celldata)
    for rowind, rowtitle in enumerate(allrowtitles):
        table.rowtitles[rowind] = rowtitle
    return table.make(**kwargs)


def dord(dict_of_dicts, **kwargs):
    """Return table representation of the given dictionary of dictionaries,
    where each dictionary represents a **row**. Keyword arguments are passed to
    :py:meth:`Table.make`."""
    allcoltitles = []
    for rowdata in dict_of_dicts.values():
        for coltitle in rowdata.keys():
            if not coltitle in allcoltitles:
                allcoltitles.append(coltitle)
    table = Table()
    allrowtitles = dict_of_dicts.keys()
    for rowind, (rowtitle, rowdata) in enumerate(dict_of_dicts.iteritems()):
        table.rowtitles[rowind] = rowtitle
        for coltitle, celldata in rowdata.iteritems():
            colind = allcoltitles.index(coltitle)
            table.insert_cell((rowind, colind), celldata)
    for colind, coltitle in enumerate(allcoltitles):
        table.coltitles[colind] = coltitle
    return table.make(**kwargs)


def isiter(obj):
    """Check if an object is iterable. Return True for lists, tuples,
    dictionaries and numpy arrays (all objects that possess an __iter__
    method).  Return False for scalars (float, int, etc.), strings, bool and
    None."""
    # 2011-09-13 - 2014-07-20
    # copied from tb.misc.isiterable on 2014-07-10
    # former tb.isiterable from 2011-01-27
    # former mytools.isiterable
    # Initial idea from
    # http://bytes.com/topic/python/answers/514838-how-test-if-object-sequence-
    # iterable:
    # return isinstance(obj, basestring) or getattr(obj, '__iter__', False)
    # I found this to be better:
    return not getattr(obj, '__iter__', False) is False


def alliter(seq):
    for item in seq:
        if not isiter(item):
            return False
    return True


def isdict(obj):
    """Check if the given object *obj* is a dictionar."""
    return hasattr(obj, 'iteritems')


def alldict(seq):
    for item in seq:
        if not isdict(item):
            return False
    return True


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
        if not isiter(key):
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

    def __init__(self, cells=None, rowtitles=None, coltitles=None,
                 colalign=None):
        self._cells = CellDict() if cells is None else cells
        self._rowtitles = TitleDict() if rowtitles is None else rowtitles
        self._coltitles = TitleDict() if coltitles is None else coltitles
        self._colalign = AlignDict() if colalign is None else colalign

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

    _mergedefault = {('|', '-'): '+',
                     ('|', '='): '+',
                     ('|', '~'): '+',
                     (':', '-'): '+',
                     (':', '='): '+',
                     (':', '~'): '+',
                     (';', '-'): '+',
                     (';', '='): '+',
                     (';', '~'): '+',
                     ('!', '-'): '+',
                     ('!', '='): '+',
                     ('!', '~'): '+',
                     ('I', '-'): '+',
                     ('I', '='): '+',
                     ('I', '~'): '+',
                     ('*', '*'): '*',
                     ('#', '#'): '#',
                     ('@', '@'): '@',
                     ('+', '+'): '+',
                     ('/', '/'): '/',
                     ('\\', '\\'): '\\',
                     ('>', '>'): '>',
                     ('<', '<'): '<',
                     ('.', '.'): '.',
                     (':', ':'): ':',
                     (';', ';'): ';',
                     (':', '.'): ':',
                     ('"', '"'): '"',
                     ('z', 'z'): 'z',
                     ('Z', 'Z'): 'Z',
                     ('o', 'o'): 'o',
                     ('O', 'O'): 'O',
                     ('\'', '\''): '\''}

    _mergetopleft = _mergedefault.copy()
    _mergetopright = _mergedefault.copy()
    _mergebottomleft = _mergedefault.copy()
    _mergebottomright = _mergedefault.copy()
    _mergeleft = _mergedefault.copy()
    _mergeright = _mergedefault.copy()
    _mergetop = _mergedefault.copy()
    _mergebottom = _mergedefault.copy()
    _mergecenter = _mergedefault.copy()

    _pieces_light_horizontal = [unichr(9474), unichr(9478),
                                unichr(9482), unichr(9550)]
    _pieces_light_vertical = [unichr(9472), unichr(9476),
                              unichr(9480), unichr(9548)]
    _pieces_heavy_horizontal = [unichr(9475), unichr(9479),
                                unichr(9483), unichr(9551)]
    _pieces_heavy_vertical = [unichr(9473), unichr(9477),
                              unichr(9481), unichr(9549)]
    _pieces_double_horizontal = [unichr(9553)]
    _pieces_double_vertical = [unichr(9552)]

    for hpiece in _pieces_light_horizontal:
        for vpiece in _pieces_light_vertical:
            _mergetopleft[(hpiece, vpiece)] = unichr(9484)
            _mergetopright[(hpiece, vpiece)] = unichr(9488)
            _mergebottomleft[(hpiece, vpiece)] = unichr(9492)
            _mergebottomright[(hpiece, vpiece)] = unichr(9496)
            _mergeleft[(hpiece, vpiece)] = unichr(9500)
            _mergeright[(hpiece, vpiece)] = unichr(9508)
            _mergetop[(hpiece, vpiece)] = unichr(9516)
            _mergebottom[(hpiece, vpiece)] = unichr(9524)
            _mergecenter[(hpiece, vpiece)] = unichr(9532)
    for hpiece in _pieces_light_horizontal:
        for vpiece in _pieces_heavy_vertical:
            _mergetopleft[(hpiece, vpiece)] = unichr(9485)
            _mergetopright[(hpiece, vpiece)] = unichr(9489)
            _mergebottomleft[(hpiece, vpiece)] = unichr(9493)
            _mergebottomright[(hpiece, vpiece)] = unichr(9497)
            _mergeleft[(hpiece, vpiece)] = unichr(9501)
            _mergeright[(hpiece, vpiece)] = unichr(9509)
            _mergetop[(hpiece, vpiece)] = unichr(9519)
            _mergebottom[(hpiece, vpiece)] = unichr(9527)
            _mergecenter[(hpiece, vpiece)] = unichr(9535)
    for hpiece in _pieces_heavy_horizontal:
        for vpiece in _pieces_light_vertical:
            _mergetopleft[(hpiece, vpiece)] = unichr(9486)
            _mergetopright[(hpiece, vpiece)] = unichr(9490)
            _mergebottomleft[(hpiece, vpiece)] = unichr(9494)
            _mergebottomright[(hpiece, vpiece)] = unichr(9498)
            _mergeleft[(hpiece, vpiece)] = unichr(9504)
            _mergeright[(hpiece, vpiece)] = unichr(9512)
            _mergetop[(hpiece, vpiece)] = unichr(9520)
            _mergebottom[(hpiece, vpiece)] = unichr(9528)
            _mergecenter[(hpiece, vpiece)] = unichr(9538)
    for hpiece in _pieces_heavy_horizontal + _pieces_double_horizontal:
        for vpiece in _pieces_heavy_vertical + _pieces_double_vertical:
            _mergetopleft[(hpiece, vpiece)] = unichr(9487)
            _mergetopright[(hpiece, vpiece)] = unichr(9491)
            _mergebottomleft[(hpiece, vpiece)] = unichr(9495)
            _mergebottomright[(hpiece, vpiece)] = unichr(9499)
            _mergeleft[(hpiece, vpiece)] = unichr(9507)
            _mergeright[(hpiece, vpiece)] = unichr(9515)
            _mergetop[(hpiece, vpiece)] = unichr(9523)
            _mergebottom[(hpiece, vpiece)] = unichr(9531)
            _mergecenter[(hpiece, vpiece)] = unichr(9547)

    for hpiece in _pieces_double_horizontal:
        for vpiece in _pieces_double_vertical:
            _mergetopleft[(hpiece, vpiece)] = unichr(9556)
            _mergetopright[(hpiece, vpiece)] = unichr(9559)
            _mergebottomleft[(hpiece, vpiece)] = unichr(9562)
            _mergebottomright[(hpiece, vpiece)] = unichr(9565)
            _mergeleft[(hpiece, vpiece)] = unichr(9568)
            _mergeright[(hpiece, vpiece)] = unichr(9571)
            _mergetop[(hpiece, vpiece)] = unichr(9574)
            _mergebottom[(hpiece, vpiece)] = unichr(9577)
            _mergecenter[(hpiece, vpiece)] = unichr(9580)
    for hpiece in _pieces_double_horizontal:
        for vpiece in _pieces_light_vertical:
            _mergetopleft[(hpiece, vpiece)] = unichr(9555)
            _mergetopright[(hpiece, vpiece)] = unichr(9558)
            _mergebottomleft[(hpiece, vpiece)] = unichr(9561)
            _mergebottomright[(hpiece, vpiece)] = unichr(9564)
            _mergeleft[(hpiece, vpiece)] = unichr(9567)
            _mergeright[(hpiece, vpiece)] = unichr(9570)
            _mergetop[(hpiece, vpiece)] = unichr(9573)
            _mergebottom[(hpiece, vpiece)] = unichr(9576)
            _mergecenter[(hpiece, vpiece)] = unichr(9579)
    for hpiece in _pieces_light_horizontal:
        for vpiece in _pieces_double_vertical:
            _mergetopleft[(hpiece, vpiece)] = unichr(9554)
            _mergetopright[(hpiece, vpiece)] = unichr(9557)
            _mergebottomleft[(hpiece, vpiece)] = unichr(9560)
            _mergebottomright[(hpiece, vpiece)] = unichr(9563)
            _mergeleft[(hpiece, vpiece)] = unichr(9566)
            _mergeright[(hpiece, vpiece)] = unichr(9569)
            _mergetop[(hpiece, vpiece)] = unichr(9572)
            _mergebottom[(hpiece, vpiece)] = unichr(9575)
            _mergecenter[(hpiece, vpiece)] = unichr(9578)

    def _merge(self, hsep, vsep, pos='center'):
        if not hsep:
            return ''
        if not vsep:
            return ''
        if hsep == ' ':
            return vsep
        if vsep == ' ':
            return hsep
        mergedict = getattr(self, '_merge'+pos)
        return mergedict.get((hsep, vsep), ' ')

    def make(self, titles=False, hb='', vb='', padding=0, hp=0, vp=0,
             autoalign=True, rowtitles=False, coltitles=False, hc=' ', vc='',
             ht=' ', vt='', border='', borderleft='', borderright='',
             bordertop='', borderbottom='', paddingleft=0, paddingright=0,
             paddingtop=0, paddingbottom=0, width=None, box=True):

        """Create table representation.


        The following formatting options exist:

            *rowtitles*:
                Show row titles. Default: False

            *coltitles*:
                Show column titles. Default: False

            *hc*:
                Horizontal cell delimiter. Default: ' '

            *vc*:
                Vertical cell delimiter. Default: ''

            *ht*:
                Horizontal delimiter between row titles and data cells.
                Default: ' '

            *vt*:
                Vertical delimiter between column titles and data cells.
                Default: ''

            *borderleft*:
                Character used as the left table border. Default: ''

            *borderright*:
                Character used as the right table border. Default: ''

            *bordertop*:
                Character used as the top table border. Default: ''

            *borderbottom*:
                Character used as the bottom table border. Default: ''

            *paddingleft*:
                Left cell padding (number of space characters). Default: 0

            *paddingright*:
                Right cell padding (number of space characters). Default: 0

            *paddingtop*:
                Top cell padding (number of space characters). Default: 0

            *paddingbottom*:
                Bottom cell padding (number of space characters). Default: 0

            *autoalign*:
                If *True*, infer alignment of columns from the column data.
                only for those columns for which no alignment has been set.
                Default: *True*

            *width*:
                If not *None*, set the width of the table. The rest of the
                characters will be cut from each line. Should be set to the
                terminal width for wide tables. Default: *None*

            *box*:
                If *True*, interpret certain characters in the options *hc*,
                *vc*, *ht*, *vt*, *borderleft*, *borderright*, *bordertop*,
                *borderbottom*, *hb* and *vb* as unicode box drawing characters
                (0x2500..0x2580). May not be available on all systems. See the
                section "special delimiters" for a list of characters that are
                interpreted. Default: *True*


        The following shortcuts exist:

            *titles*:
                Show row and column titles. Overrides *rowtitles* and
                *coltitles*. Default: False

            *hb*:
                Set horizontal borders. Overrides *bordertop* and
                *borderbottom*. Default: ''

            *vb*:
                Set vertical borders. Overrides *borderleft* and *borderright*.
                Default: ''

            *padding*:
                Set cell padding (number of space characters). Overrides
                *paddingtop*, *paddingbottom*, *paddingleft* and
                *paddingright*. Default: 0

            *hp*:
                Set horizontal cell padding (number of space characters).
                Overrides *paddingleft* and *paddingright*. Default: 0

            *vp*:
                Set vertical cell padding (number of space characters).
                Overrides *paddingtop* and *paddingbottom*. Default: 0

            *border*:
                Set borders. Overrides *borderleft*, *borderright*, *bordertop*
                and *borderbottom*. Default: ''


        Special delimiters:

        As long as *box* is *True* (default), certain characters in the options
        *hc*, *vc*, *ht*, *vt*, *borderleft*, *borderright*, *bordertop*,
        *borderbottom*, *hb* and *vb* are interpreted as unicode box drawing
        characters (0x2500..0x2580). May not be available on all systems.

        Further information can be found at
        http://en.wikipedia.org/wiki/Box-drawing_character
        http://unicode.org/charts/PDF/U2500.pdfhttp://unicode.org/charts/PDF
        /U2500.pdfhttp://unicode.org/charts/PDF/U2500.pdf

        The following characters are interpreted:

            "l":
                light single line

            "h":
                heavy single line

            "d":
                double line

            "2":
                light double dash

            "u":
                heavy double dash

            "3":
                light triple dash

            "t":
                heavy triple dash

            "4":
                light quadruple dash

            "q":
                heavy quadruple dash
        """

        #
        # to do:
        # - enable prettyprinting using box-drawing unicode characters
        # - support alignment for complex numbers
        # - support scientific number format
        # - support alignment for scientific number format
        #

        if titles:
            rowtitles = True
            coltitles = True

        if hb:
            bordertop = hb
            borderbottom = hb

        if vb:
            borderleft = vb
            borderright = vb

        if vp:
            paddingtop = vp
            paddingbottom = vp

        if hp:
            paddingleft = hp
            paddingright = hp

        if padding:
            paddingleft = padding
            paddingright = padding
            paddingtop = padding
            paddingbottom = padding

        if border:
            borderleft = border
            borderright = border
            bordertop = border
            borderbottom = border

        if not isinstance(hc, basestring) or len(hc) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(vc, basestring) or len(vc) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(ht, basestring) or len(ht) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(vt, basestring) or len(vt) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(borderleft, basestring) or len(borderleft) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(borderright, basestring) or len(borderright) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(bordertop, basestring) or len(bordertop) > 1:
            raise ValueError, 'must be a string no longer than one character'
        if not isinstance(borderbottom, basestring) or len(borderbottom) > 1:
            raise ValueError, 'must be a string no longer than one character'

        # interpret shortcuts for unicode box drawing characters
        _boxchars_horizontal = {'l': unichr(9472), 'h': unichr(9473),
                                'd': unichr(9552), '2': unichr(9548),
                                'u': unichr(9549), '3': unichr(9476),
                                't': unichr(9477), '4': unichr(9480),
                                'q': unichr(9481)}
        _boxchars_vertical = {'l': unichr(9474), 'h': unichr(9475),
                              'd': unichr(9553), '2': unichr(9550),
                              'u': unichr(9551), '3': unichr(9478),
                              't': unichr(9479), '4': unichr(9482),
                              'q': unichr(9483)}
        hc = _boxchars_vertical.get(str(hc), hc)
        ht = _boxchars_vertical.get(str(ht), ht)
        vc = _boxchars_horizontal.get(str(vc), vc)
        vt = _boxchars_horizontal.get(str(vt), vt)
        borderleft = _boxchars_vertical.get(str(borderleft), borderleft)
        borderright = _boxchars_vertical.get(str(borderright), borderright)
        bordertop = _boxchars_horizontal.get(str(bordertop), bordertop)
        borderbottom = _boxchars_horizontal.get(str(borderbottom),
                                                borderbottom)

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
                                        paddingright, hc, ht)
            rows.append(row)

        # column titles
        colwidths = self.colwidths(withtitle=coltitles, colalign=colalign)
        if coltitles:
            for i in xrange(paddingtop):
                row = self._padrow(rowtitles, borderleft, borderright,
                                   paddingleft, paddingright, hc, ht,
                                   colwidths)
                rows.append(row)
            row = self._coltitlesrowstring(rowtitles, borderleft,
                                            borderright, paddingleft,
                                            paddingright, hc, ht)
            rows.append(row)
            for i in xrange(paddingtop):
                row = self._padrow(rowtitles, borderleft, borderright,
                                   paddingleft, paddingright, hc, ht,
                                   colwidths)
                rows.append(row)
            if vt:
                row = self._coltitlessepstring(allrowstrings, rowtitles,
                                            borderleft, borderright,
                                            paddingleft, paddingright, vt,
                                            hc, ht)
                rows.append(row)

        # main rows (first)
        if len(allrowstrings) > 0:
            rowtitle = self.rowtitles.get(self.top(), ' '*rowtitlescolwidth)
            if not rowtitle:
                rowtitle = ' '*rowtitlescolwidth
            for i in xrange(paddingtop):
                row = self._padrow(rowtitles, borderleft, borderright,
                                   paddingleft, paddingright, hc, ht,
                                   colwidths)
                rows.append(row)
            row = self._datarowstring(allrowstrings[0], rowtitle, borderleft,
                                      borderright, rowtitles, paddingleft,
                                      paddingright, hc, ht)
            rows.append(row)
            for i in xrange(paddingtop):
                row = self._padrow(rowtitles, borderleft, borderright,
                                   paddingleft, paddingright, hc, ht,
                                   colwidths)
                rows.append(row)

        # main rows (remaining)
        for rowind, rowstrings in enumerate(allrowstrings[1:], 1):
            rowtitle = self.rowtitles.get(rowind, ' '*rowtitlescolwidth)
            if vc:
                row = self._datasepstring(rowstrings, rowtitles, borderleft,
                                          borderright, paddingleft,
                                          paddingright, vc, hc, ht)
                rows.append(row)
            for i in xrange(paddingtop):
                row = self._padrow(rowtitles, borderleft, borderright,
                                   paddingleft, paddingright, hc, ht,
                                   colwidths)
                rows.append(row)
            row = self._datarowstring(rowstrings, rowtitle, borderleft,
                                      borderright, rowtitles, paddingleft,
                                      paddingright, hc, ht)
            rows.append(row)
            for i in xrange(paddingtop):
                row = self._padrow(rowtitles, borderleft, borderright,
                                   paddingleft, paddingright, hc, ht,
                                   colwidths)
                rows.append(row)

        # bottom border
        if borderbottom:
            row = self._borderbottomstring(allrowstrings, borderleft,
                                           borderright, borderbottom,
                                           rowtitles, paddingleft,
                                           paddingright, hc, ht)
            rows.append(row)

        # cut rows according to terminal width
        if width is not None:
            for i in xrange(len(rows)):
                rows[i] = rows[i][:width]

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
                            borderright, paddingleft, paddingright, vt,
                            hc, ht):
        row = ''

        # left
        if borderleft:
            row += self._merge(borderleft, vt, 'left')
        if rowtitles:
            row += vt*paddingleft
            row += vt*self.rowtitlescolwidth()
            row += vt*paddingright
            row += self._merge(ht, vt, 'center')

        # main
        parts = []
        for rowstring in allrowstrings[0]:
            part = ''
            part += vt*paddingleft
            part += vt*len(rowstring)
            part += vt*paddingright
            parts.append(part)
        sep = self._merge(hc, vt, 'center')
        row += sep.join(parts)

        # right
        if borderright:
            row += self._merge(borderright, vt, 'right')

        return row

    def _datasepstring(self, rowstrings, rowtitles, borderleft, borderright,
                       paddingleft, paddingright, vc, hc, ht):
        row = ''

        # left
        if borderleft:
            row += self._merge(borderleft, vc, 'left')
        if rowtitles:
            row += vc*paddingleft
            row += vc*self.rowtitlescolwidth()
            row += vc*paddingright
            row += self._merge(ht, vc, 'center')

        # main
        parts = []
        for rowstring in rowstrings:
            part = ''
            part += vc*paddingleft
            part += vc*len(rowstring)
            part += vc*paddingright
            parts.append(part)
        sep = self._merge(hc, vc, 'center')
        row += sep.join(parts)

        # right
        if borderright:
            row += self._merge(borderright, vc, 'right')

        return row

    def _padrow(self, rowtitles, borderleft, borderright, paddingleft,
                paddingright, hc, ht, colwidths):
        row = ''

        # left
        if borderleft:
            row += borderleft
        if rowtitles:
            row += ' '*paddingleft
            row += ' '*self.rowtitlescolwidth()
            row += ' '*paddingright
            row += ht

        # main
        parts = []
        for colwidth in colwidths:
            part = ''
            part += ' '*paddingleft
            part += ' '*colwidth
            part += ' '*paddingright
            parts.append(part)
        row += hc.join(parts)

        # right
        if borderright:
            row += borderright

        return row

    def _coltitlesrowstring(self, rowtitles, borderleft, borderright,
                            paddingleft, paddingright, hc, ht):
        row = ''

        # left
        if borderleft:
            row += borderleft
        if rowtitles:
            row += ' '*paddingleft
            row += ' '*self.rowtitlescolwidth()
            row += ' '*paddingright
            row += ht

        # main
        parts = []
        for coltitle in self.coltitlestrings():
            part = ''
            part += ' '*paddingleft
            part += str(coltitle)
            part += ' '*paddingright
            parts.append(part)
        row += hc.join(parts)

        # right
        if borderright:
            row += borderright

        return row

    def _bordertopstring(self, allrowstrings, borderleft, borderright,
                         bordertop, rowtitles, paddingleft, paddingright,
                         hc, ht):
        row = ''

        # left
        if borderleft:
            row += self._merge(borderleft, bordertop, 'topleft')
        if rowtitles:
            row += bordertop*paddingleft
            row += bordertop*self.rowtitlescolwidth()
            row += bordertop*paddingright
            row += self._merge(ht, bordertop, 'top')

        # main
        parts = []
        for rowstring in allrowstrings[0]:
            part = ''
            part += bordertop*paddingleft
            part += bordertop*len(rowstring)
            part += bordertop*paddingright
            parts.append(part)
        sep = self._merge(hc, bordertop, 'top')
        row += sep.join(parts)

        # right
        if borderright:
            row += self._merge(borderright, bordertop, 'topright')

        return row

    def _borderbottomstring(self, allrowstrings, borderleft, borderright,
                         borderbottom, rowtitles, paddingleft, paddingright,
                         hc, ht):
        row = ''

        # left
        if borderleft:
            row += self._merge(borderleft, borderbottom, 'bottomleft')
        if rowtitles:
            row += borderbottom*paddingleft
            row += borderbottom*self.rowtitlescolwidth()
            row += borderbottom*paddingright
            row += self._merge(ht, borderbottom, 'bottom')

        # main
        parts = []
        for rowstring in allrowstrings[0]:
            part = ''
            part += borderbottom*paddingleft
            part += borderbottom*len(rowstring)
            part += borderbottom*paddingright
            parts.append(part)
        sep = self._merge(hc, borderbottom, 'bottom')
        row += sep.join(parts)

        # right
        if borderright:
            row += self._merge(borderright, borderbottom, 'bottomright')

        return row

    def _datarowstring(self, rowstrings, rowtitle, borderleft, borderright,
                       rowtitles, paddingleft, paddingright, hc, ht):
        row = ''

        # left
        if borderleft:
            row += borderleft
        if rowtitles:
            row += ' '*paddingleft
            row += str(rowtitle)
            row += ' '*paddingright
            row += ht

        # main
        parts = []
        for rowstring in rowstrings:
            part = ''
            part += ' '*paddingleft
            part += rowstring
            part += ' '*paddingright
            parts.append(part)
        row += hc.join(parts)

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

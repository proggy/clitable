#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright notice
# ----------------
#
# Copyright (C) 2014-2023 Daniel Jung
# Contact: proggy-contact@mailbox.org
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
"""This module contains presets for formatting tables.

The presets are dictionaries which contain keyword arguments. To apply a
preset, the dictionary of the user's choice has to be passed to
:py:meth:`clitable.Table.make` or one of the shortcut functions
:func:`clitable.autotable`, :func:`clitable.docl` etc. using a double-star
notation (**). Example:

    >>> data = dict(a=[1, 2, 3], b=[1, 2], c=[1])
    >>> print clitable.docl(d, coltitles=1, **clitable.presets.asciielegant)
    ===========
     a   c   b
    -----------
     1   1   1
     2       2
     3
    ===========
"""

plain = dict(hc=' ', vc='', ht=' ', vt='', border='', padding=0)

# using ASCII characters only
asciielegant = dict(hb='=', vt='-', hp=1)
asciimatrix = dict(hb='-', vb='|', ht='|', vt='-', hc='|', vc='-', hp=1)
asciibox = dict(hb='-', vb='|', hp=1)
asciicross = dict(hc='|', vc='-', ht='|', vt='-', border='', hp=1)
asciicross2 = dict(hc='|', vc='-', ht='|', vt='=', border='', hp=1)
asciidense = dict(hc='|', vc='-', ht='|', vt='=', hb='=', vb='|', hp=1)
asciiheader = dict(ht='|', vt='-', hb='-', vb='|', hp=1)
asciiheadercross = dict(ht='|', vt='-', border='', hp=1)

# using unicode box drawing characters (0x2500..0x2580)
elegant = dict(hb='d', vt='l', hp=1)
elegant2 = dict(hb='h', vt='l', hp=1)
matrix = dict(border='l', ht='l', vt='l', hc='l', vc='l', hp=1)
box = dict(border='l', hp=1)
fatbox = dict(border='h', hp=1)
doublebox = dict(border='d', hp=1)
cross = dict(hc='l', vc='l', ht='l', vt='l', border='', hp=1)
cross2 = dict(hc='l', vc='l', ht='d', vt='d', border='', hp=1)
dense = dict(hc='l', vc='l', ht='d', vt='d', border='h', hp=1)
header = dict(ht='l', vt='l', border='l', hp=1)
headercross = dict(ht='l', vt='l', border='', hp=1)

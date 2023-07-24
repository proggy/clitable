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

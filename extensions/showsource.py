# showsource.py --- Show source page with a given place highlighted

## Copyright (C) 2005, 2006 Brailcom, o.p.s.
##
## Author: Milan Zamazal <pdm@brailcom.org>
##
## COPYRIGHT NOTICE
##
## This program is free software; you can redistribute it and/or modify it
## under the terms of the GNU General Public License as published by the Free
## Software Foundation; either version 2 of the License, or (at your option)
## any later version.
##
## This program is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
## more details.
##
## You should have received a copy of the GNU General Public License along with
## this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

import cgi
import string
import sys

import wachecker.charseq
import wachecker.location

def showsource (url, line, column):
    if url is None:
        return 'No URL given'
    row = line and int (line) or 0
    col = column and int (column) or 0
    location = wachecker.location.Location (url)
    source_lines = location.open ().readlines ()
    row_ = max (row-1, 0)
    col_ = max (col-1, 0)
    before_lines = source_lines[:row_] + [source_lines[row_][:col_]]
    after_lines = [source_lines[row_][col_:]] + source_lines[row_+1:]
    return ('<pre>%s</pre>\n<a name="point"><strong>***here***</strong></a>\n<pre>%s</pre>' %
            (wachecker.charseq.str (cgi.escape (string.join (before_lines, ''))),
             wachecker.charseq.str (cgi.escape (string.join (after_lines, ''))),))

def init (instance):
    instance.registerUtil ('showsource', showsource)

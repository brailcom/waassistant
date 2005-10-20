### quicktest.py --- Quick page accessibility test

## Copyright (C) 2005 Brailcom, o.p.s.
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

import wachecker.location
import wachecker.test

wachecker.test.load_tests ()

class _Test (object):

    def __init__ (self, test, issues):
        self.title = test.name ()
        self.description = test.description ()
        self.url = test.location () and test.location ().url ()
        self.issues = issues

class _Issue (object):

    def __init__ (self, issue):
        self.description = issue.description ()
        self.data = issue.data ()
        input_position = issue.input_position ()
        if input_position:
            self.line, self.column = input_position
        else:
            self.line = self.column = 0
        self.kind = issue.classification ()

def quicktest (db, form):
    # Retrieve form data
    url = form.getfirst ('location')
    if url is None:
        raise Exception ('No URL given')
    testset_ids = []
    prefix = 'testsetx'
    prefixlen = len (prefix)
    for k in form.keys ():
        if k[:prefixlen] == prefix:
            testset_ids.append (k[prefixlen:])
    cache = form.getfirst ('cache')
    # Create WAchecker instances
    location = wachecker.location.Location (url, refresh_cache=(not cache))
    tests = []
    for testset in [db.testsetx.get (id, 'klass') for id in testset_ids]:
        for t in [t for t in getattr (wachecker.test, testset).tests ()]:
            if t not in tests:
                tests.append (t)
    # Run the tests
    test_issues = []
    def sortfunc (test1, test2):
        return cmp (test1.name (), test2.name ())
    tests.sort (sortfunc)
    for t in tests:
        try:
            issues = [_Issue (i) for i in t ().run (location)]
        except wachecker.exception.System_Error, e:
            raise Exception ("System error: %s: %s" % (e.message (), str (e.exception ()),))
        # Process issues
        def sortfunc (issue1, issue2):
            return (cmp (issue1.description, issue2.description) or
                    cmp (issue1.line, issue2.line) or
                    cmp (issue1.column, issue2.column))
        issues.sort (sortfunc)
        test_issues.append (_Test (t, issues))
    # Return the resulting data structures
    return test_issues

def init (instance):
    instance.registerUtil ('quicktest', quicktest)

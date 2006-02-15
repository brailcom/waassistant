### runtests.py --- Running WAchecker tests when needed

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

from roundup.exceptions import Reject

import wachecker.document
import wachecker.exception
import wachecker.location
import wachecker.test

wachecker.test.load_tests ()

# Common utilities

def _testset_tests (testset):
    test_classes = getattr (wachecker.test, testset).tests ()
    return [t.__name__ for t in test_classes]

def _active_testsets (db):
    dbcl = db.testset
    return [dbcl.get (id, 'klass') for id in dbcl.list ()
            if dbcl.get (id, 'enabled')]

def _active_tests (db):
    sets = _active_testsets (db)
    tests = []
    for s in sets:
        for t in _testset_tests (s):
            if t not in tests:
                tests.append (t)
    return tests

def _active_urls (db):
    dbcl = db.location
    return [dbcl.get (id, 'url') for id in dbcl.list ()]

def _run_test (db, url, test, refresh=False):
    location = wachecker.location.Location (url, refresh_cache=refresh)
    test_instance = getattr (wachecker.test, test) ()
    try:
        test_issues = test_instance.run (location)
    except wachecker.exception.System_Error, e:
        raise Reject, ("System error: %s: %s" % (e.message (), str (e.exception ()),))
    for issue in test_issues:
        line, column = (issue.input_position () or (0, 0,))
        classification = issue.classification ()
        if classification == 'ERROR':
            kind = 'error'
        elif classification == 'ERR??':
            kind = 'maybe-error'
        elif classification == 'CHECK':
            kind = 'check'
        else:
            raise Reject, "Invalid issue kind", classification
        data = issue.data () or ''
        db.issue.create (title='',
                         description=issue.description (),
                         data=data,
                         kind=kind,
                         url=url,
                         test=test,
                         status='unhandled',
                         active=True,
                         line=str (line),
                         column=str (column),
                         generated=True)

def _rerun_tests (db, tests=None):
    for url in _active_urls (db):
        if tests is None:
            tests = _active_tests (db)
        for test in tests:
            _run_test (db, url, test, refresh=True)

def _activate_issues (db, urls, tests):
    seen = {}
    for t in tests:
        seen[t] = []
    # Activate all related issues
    for issue_id in db.issue.list ():
        i_url = db.issue.get (issue_id, 'url')
        i_test_id = db.issue.get (issue_id, 'test')
        if i_test_id:
            i_test = db.test.get (i_test_id, 'title')
        else:
            i_test = None
        i_active = db.issue.get (issue_id, 'active')
        i_generated = db.issue.get (issue_id, 'generated')
        if i_url in urls and i_test in tests:
            if not i_active:
                db.issue.set (issue_id, active=True)
            if i_generated and i_url not in seen[i_test]:
                seen[i_test].append (i_url)
    # Run new test/location pairs
    for url in urls:
        for test in tests:
            if url not in seen[test]:
                _run_test (db, url, test)

def _disable_issues (db, url=None, tests=[]):
    test_ids = [db.test.lookup (t) for t in tests]
    for issue_id in db.issue.list ():
        if ((url and db.issue.get (issue_id, 'url') == url) or
            (tests and db.issue.get (issue_id, 'test') in test_ids)):
            db.issue.set (issue_id, active=False)

# Locations

def _check_location_values (db, c, nodeid, newvalues):
    # Empty URL?
    url = newvalues.get ('url')
    if url == '' or (url is None and nodeid is None):
        raise Reject, "No URL given"
    if url[:len ('http://')] != 'http://' and url[:len ('https://')] != 'https://':
        raise Reject ('URL does not start with http:// nor https://')

def _run_location_tests (db, c, nodeid, newvalues):
    url = newvalues.get ('url')
    old_url = nodeid and c.get (nodeid, 'url')
    # If URL is not changed, do nothing
    if not url:
        return
    if old_url == url:
        return
    # Add new location issues
    _activate_issues (db, urls=(url,), tests=_active_tests (db))
    # Disable old location issues
    if old_url:
        _disable_issues (db, url=old_url)
    
def audit_location (db, c, nodeid, newvalues):
    _check_location_values (db, c, nodeid, newvalues)
    _run_location_tests (db, c, nodeid, newvalues)

def retire_location (db, c, nodeid, newvalues):
    url = c.get (nodeid, 'url')
    _disable_issues (db, url=url)

# Test sets

def _run_testset_tests (db, c, nodeid, newvalues):
    enabled = newvalues.get ('enabled')
    if c.get (nodeid, 'enabled') != enabled:
        testset = c.get (nodeid, 'klass')
        testset_tests = _testset_tests (testset)
        if enabled:
            tests = _active_tests (db)
            new_tests = []
            for t in testset_tests:
                if t not in tests:
                    new_tests.append (t)
            _activate_issues (db, urls=_active_urls (db), tests=new_tests)
        else:
            tests = []
            for s in _active_testsets (db):
                if s != testset:
                    tests = tests + _testset_tests (s)
            old_tests = []
            for t in _testset_tests (testset):
                if t not in tests:
                    old_tests.append (t)
            _disable_issues (db, tests=old_tests)

def audit_testset (db, c, nodeid, newvalues):
    _run_testset_tests (db, c, nodeid, newvalues)

# Tests

def audit_test (db, c, nodeid, newvalues):
    if newvalues.get ('rerun'):
        newvalues['rerun'] = False
        # Delete test issues
        test_id = c.get (nodeid, 'id')
        for id in db.issue.list ():
            if db.issue.get (id, 'generated') and db.issue.get (id, 'test') == test_id:
                db.issue.retire (id)
        # Rerun the test
        test = c.get (nodeid, 'klass')
        _rerun_tests (db, tests=[test])

# Checkpoints

def audit_checkpoint (db, c, nodeid, newvalues):
    if (db.checkpoint.get (nodeid, 'title') == 'Resolve Issues' and
        newvalues.has_key ('status') and
        db.checkpoint.get (nodeid, 'status') != newvalues['status'] and
        db.cstatus.get (newvalues['status'], 'title') == 'done'):
        for id in db.issue.list ():
            if db.issue.get (id, 'generated'):
                db.issue.retire (id)
        _rerun_tests (db)
    
# Interface

def init (db):
    db.testset.audit ('set', audit_testset)
    db.test.audit ('set', audit_test)
    db.location.audit ('create', audit_location)
    db.location.audit ('set', audit_location)
    db.location.audit ('retire', retire_location)
    db.checkpoint.audit ('set', audit_checkpoint)

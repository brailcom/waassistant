### initial_data.py --- Initial WAassistant data to store into database

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

# System default users
user = db.getclass ('user')
user.create (username='admin', password=adminpw, address=admin_email,
             roles='Admin', allroles='Admin,Supervisor,Tester,User')
user.create (username='anonymous', roles='Anonymous')

# Issue statuses and kinds
istatus = db.getclass ('istatus')
istatus.create (title='unhandled', order='1')
istatus.create (title='ok', order='2')
istatus.create (title='error', order='3')
istatus.create (title='n/a', order='4')
istatus.create (title='clone', order='5')
ikind = db.getclass ('ikind')
ikind.create (title='error', order='1')
ikind.create (title='maybe-error', order='2')
ikind.create (title='check', order='3')

# Checkpoint statuses
cstatus = db.getclass ('cstatus')
cstatus.create (title='open', order='1')
cstatus.create (title='done', order='2')
cstatus.create (title='n/a', order='3')
cstatus.create (title='inactive', order='4')

## Checkpoints
checkpoint = db.getclass ('checkpoint')
def make_cp (title, description, status='inactive', role='Tester', **kwargs):
    return checkpoint.create (title=title, description=description, status=status, role=role, **kwargs)
# setup actions
cp_users = \
    make_cp ('Create Users', "Create Supervisors and Testers in section [User].  Then log in as a user with Supervisor role and continue with other tasks.",
             status='open', assignedto=db.user.lookup ('admin'))
cp_tasks = \
    make_cp ('Define Tasks', "Define aims of the project in section [Tasks].",
             prereq=[cp_users], role='Supervisor')
cp_locations = \
    make_cp ('Define Locations', "Define pages to check in section [Locations].",
             prereq=[cp_tasks], role='Supervisor')
cp_testsets = \
    make_cp ('Enable Test Sets', "Enable test sets to use in section [Test Sets].",
             prereq=[cp_tasks], role='Supervisor')
# making Preliminary Report
cp_issues1 = \
    make_cp ('Review Issues', "Review all issues in section [Issues] and set their status.",
             prereq=[cp_locations, cp_testsets])
cp_report1 = \
    make_cp ('Review Preliminary Report', "Review Preliminary Report in section [Report].",
             prereq=[cp_issues1])
cp_report1_done = \
    make_cp ('Publish Preliminary Report', "Check this to publish final version of Preliminary Report.",
             prereq=[cp_report1], role='Supervisor')
# resolving Preliminary Report issues
cp_resolve = \
    make_cp ('Resolve Issues', "Check this to indicate issues from Preliminary Report have been reviewed by webmasters.",
             prereq=[cp_report1_done], role='Supervisor')
# making Final Report
cp_issues2 = \
    make_cp ('Review New Issues', "Review all issues in section [Issues] and set their status.",
             prereq=[cp_resolve])
cp_report2 = \
    make_cp ('Write Final Report', "Write Final Report in section [Report].",
             prereq=[cp_resolve])
cp_test_w3m = \
    make_cp ('Test in w3m', "Test [Locations] in w3m and Emacs/w3m with assistive technologies.",
             prereq=[cp_resolve])
cp_test_ie = \
    make_cp ('Test in IE', "Test [Locations] in Internet Explorer with assistive technologies.",
             prereq=[cp_resolve])
cp_report2_done = \
    make_cp ('Publish Final Report', "Check this to publish final version of Final Report.",
             prereq=[cp_issues2, cp_report2, cp_test_w3m, cp_test_ie], role='Supervisor')

# Tests & test sets
import wachecker.test
import wachecker.util
wachecker.test.load_tests ()
# Tests
test = db.getclass ('test')
for name, class_ in wachecker.test.all_tests ():
    location = class_.location ()
    url = (location and location.url ()) or ''
    aliasof = ''
    if class_.__name__ != name:
        aliasof = class_.__name__
    test.create (title=class_.name (), klass=name, description=class_.description (), url=url, aliasof=aliasof)
# Test sets
testset = db.getclass ('testset')
testsetx = db.getclass ('testsetx')
for name, class_ in wachecker.test.all_test_sets ():
    testset.create (title=class_.name (), description=class_.description (),
                    klass=name, tests=[t.__name__ for t in class_.tests ()],
                    enabled=False)
    testsetx.create (title=class_.name (), klass=name)
# Report
report = db.getclass ('report')
report.create (title='Summary')
reference = db.getclass ('reference')
reference.create (title="Web Content Accessibility Guidelines 1.0", url='http://www.w3.org/TR/1999/WAI-WEBCONTENT-19990505/', order='1')
reference.create (title="U.S. Section 508 Web Standards", url='http://www.section508.gov/index.cfm?FuseAction=Content&ID=12#Web', order='2')
reference.create (title="Brailcom, o.p.s.", url='http://www.brailcom.org', order='3')

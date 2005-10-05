### schema.py --- WAassistant database schema

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

# Class automatically gets these properties:
#   creation = Date()
#   activity = Date()
#   creator = Link('user')
#   actor = Link('user')

# IssueClass automatically gets these properties in addition to the Class ones:
#   title = String()
#   messages = Multilink("msg")
#   files = Multilink("file")
#   nosy = Multilink("user")
#   superseder = Multilink("issue")

# FileClass automatically gets this property in addition to the Class ones:
#   content = String()    [saved to disk in <tracker home>/db/files/]

# Tasks
task = IssueClass (db, 'task',
                   description=String (),
                   )

# Locations
location = Class (db, 'location',
                  title=String (),
                  url=String (),
                  )
location.setkey ('url')

# Tests
test = Class (db, 'test',
              title=String (),
              description=String (),
              klass=String (),
              url=String (),
              aliasof=String (),
              report=String (),
              rerun=Boolean (),
              )
test.setkey ('klass')

# Test sets
testset = Class (db, 'testset',
                 title=String (),
                 description=String (),
                 klass=String (),
                 tests=Multilink ('test'),
                 enabled=Boolean (),
                 report=String (),
                 )
testset.setkey ('title')

# IssueClass related entities
file = FileClass (db, 'file',
                  name=String (),
                  type=String (),
                  )
msg = FileClass (db, 'msg',
                 author=Link ('user', do_journal='no'),
                 recipients=Multilink ('user', do_journal='no'),
                 date=Date (),
                 summary=String (),
                 files=Multilink ('file'),
                 messageid=String (),
                 inreplyto=String (),
                 )

# Issue statuses and kinds
istatus = Class (db, 'istatus',
                 title=String (),
                 order=Number (),
                 )
istatus.setkey ('title')
ikind = Class (db, 'ikind',
               title=String (),
               order=Number (),
               )
ikind.setkey ('title')

# Issues
issue = IssueClass (db, 'issue',
                    description=String (),
                    data=String (),
                    kind=Link ('ikind'),
                    url=String (),
                    line=Number (),
                    column=Number (),
                    test=Link ('test', do_journal='no'),
                    status=Link ('istatus'),
                    report=String (),
                    active=Boolean (),
                    generated=Boolean (),
                    cloneof=Link ('issue'),
                    )

# Checkpoint statuses
cstatus = Class (db, 'cstatus',
                 title=String (),
                 order=Number (),
                 )
cstatus.setkey ('title')

# Checkpoints
checkpoint = IssueClass (db, 'checkpoint',
                         description=String (),
                         status=Link ('cstatus'),
                         report=String (),
                         prereq=Multilink ('checkpoint'),
                         assignedto=Link ('user'),
                         role=String ()
                         )
checkpoint.setkey ('title')

# Report
report = Class (db, 'report',
                title=String (),
                description=String ()
                )
report.setkey ('title')
problem = IssueClass (db, 'problem',
                      summary=String (),
                      description=String (),
                      impact=String (),
                      cure=String ()
                      )
recommendation = IssueClass (db, 'recommendation',
                             description=String ())
reference = Class (db, 'reference',
                   title=String (),
                   url=String (),
                   enabled=Boolean (),
                   order=Number ()
                   )

# Users
user = Class (db, 'user',
              username=String (),
              password=Password (),
              address=String (),
              realname=String (),
              phone=String (),
              organisation=String (),
              alternate_addresses=String (),
              roles=String (),  # comma-separated string of Role names
              timezone=String (),
              )
user.setkey ('username')

# Roles
# - Admin: administrator of the system and users
# - Supervisor: may do anything in the system except for managing users
# - Tester: may edit issues, write messages
# - User: anonymous user or customer, read-only access
db.security.addRole (name='Supervisor', description="Managing projects")
db.security.addRole (name='Tester', description="Accessibility testing")

## Permissions
for role in 'Admin', 'Supervisor', 'Tester', 'User',:
    db.security.addPermissionToRole (role, 'Web Access')
    db.security.addPermissionToRole (role, 'Email Access')
# common classes -- view
for c in 'location', 'issue', 'testset', 'test', 'istatus', 'cstatus', 'report', 'reference', 'problem', 'recommendation',:
    for role in 'Admin', 'Supervisor', 'Tester', 'User',:
        db.security.addPermissionToRole (role, 'View', c)
for c in 'task', 'file', 'checkpoint', 'msg', 'user',:
    for role in 'Admin', 'Supervisor', 'Tester',:
        db.security.addPermissionToRole (role, 'View', c)
# common classes -- edit
for c in 'task', 'location', 'file', 'msg', 'issue', 'reference', 'problem', 'recommendation',:
    for role in 'Admin', 'Supervisor',:
        db.security.addPermissionToRole (role, 'Edit', c)
        db.security.addPermissionToRole (role, 'Create', c)
for c in 'report',:
    for role in 'Admin', 'Supervisor',:
        db.security.addPermissionToRole (role, 'Edit', c)    
for c in 'issue',:
    db.security.addPermissionToRole ('Tester', 'Edit', c)
    db.security.addPermissionToRole ('Tester', 'Create', c)
for c in 'msg', 'file',:
    db.security.addPermissionToRole ('Tester', 'Create', c)
for c in 'testset', 'test',:
    properties = ('enabled', 'report', 'rerun',)
    db.security.addPermission (name='Edit', klass=c, properties=properties)
    for role in 'Admin', 'Supervisor',:
        db.security.addPermissionToRole (role, 'Edit', classname=c, properties=properties)
# checkpoints -- edit
for role in 'Admin', 'Supervisor', 'Tester',:
    db.security.addPermissionToRole (role, 'Create', 'checkpoint')
for role in 'Admin', 'Supervisor',:
    db.security.addPermissionToRole (role, 'Edit', 'checkpoint')
def permission_edit_checkpoint (db, userid, itemid):
    if db.user.get (userid, 'username') == 'admin':
        return True
    if db.checkpoint.get (itemid, 'creator') == userid:
        return True
    if db.checkpoint.get (itemid, 'assignedto') == userid:
        return True
    if db.checkpoint.get (itemid, 'role') == 'Tester':
        return True
    return False
db.security.addPermission (name='Edit', klass='checkpoint', check=permission_edit_checkpoint)
db.security.addPermissionToRole ('Tester', 'Edit', classname='checkpoint', check=permission_edit_checkpoint)
# problems & recommendations -- edit
def make_permission_edit_own_record (klass):
    def permission (db, userid, itemid):
        return userid == db.getclass (klass).get (itemid, 'creator')
    return permission
permission_edit_own_problem = make_permission_edit_own_record ('problem')
db.security.addPermission (name='Edit', klass='problem', check=permission_edit_own_problem)
db.security.addPermissionToRole ('Tester', 'Edit', classname='problem', check=permission_edit_own_problem)
permission_edit_own_recommendation = make_permission_edit_own_record ('recommendation')
db.security.addPermission (name='Edit', klass='recommendation', check=permission_edit_own_recommendation)
db.security.addPermissionToRole ('Tester', 'Edit', classname='recommendation',
                                 check=permission_edit_own_recommendation)
# users -- edit
db.security.addPermissionToRole ('Admin', 'Create', 'user')
db.security.addPermissionToRole ('Admin', 'Edit', 'user')
properties = ('password', 'address', 'realname', 'phone', 'alternate_addresses', 'timezone',)
def permission_edit_user (db, userid, itemid):
    return userid == itemid
db.security.addPermission (name='Edit', klass='user', properties=properties, check=permission_edit_user)
for role in 'Supervisor', 'Tester',:
    db.security.addPermissionToRole (role, 'Edit', classname='user', properties=properties,
                                     check=permission_edit_user)

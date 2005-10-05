### checkpoints.py --- Checkpoint auditors

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

from roundup.exceptions import Reject

_nested = False

def _audit_update_active (db, c, nodeid, newvalues):
    new_status = newvalues.get ('status')
    old_status = c.get (nodeid, 'status')
    if new_status == old_status:
        return
    # Prepare auxiliary data
    for id in db.cstatus.list ():
        title = db.cstatus.get (id, 'title')
        if title == 'open':
            s_open = id
        elif title == 'done':
            s_done = id
        elif title == 'n/a':
            s_na = id
        elif title == 'inactive':
            s_inactive = id
        else:
            raise Exception ('title: %s' % title)
    closed_statuses = (s_done, s_na,)
    # Find reverse dependencies
    dependencies = {}
    all_ids = c.list ()
    for id in all_ids:
        dependencies[id] = []
    for id in all_ids:
        for dep_id in c.get (id, 'prereq'):
            dependencies[dep_id].append (id)
    # If activated, check it doesn't break dependencies
    if old_status == s_inactive:
        for id in c.get (nodeid, 'prereq'):
            if c.get (id, 'status') not in closed_statuses:
                raise Reject ("Prerequisity checkpoint not yet completed: %s" % (c.get (id, 'title'),))
    # If deactivated, check it doesn't break dependencies
    if new_status == s_inactive:
        for id in dependencies[nodeid]:
            if c.get (id, 'status') in closed_statuses:
                raise Reject ("Dependent checkpoint already closed: %s" % (c.get (id, 'title'),))
    # If deactivated or reopened, deactivate open dependants
    if new_status in (s_inactive, s_open,):
        for id in dependencies[nodeid]:
            if c.get (id, 'status') == s_open:
                c.set (id, status=s_inactive)    
    # If closed, activate inactive dependants
    if new_status in closed_statuses and old_status not in closed_statuses:
        for id in dependencies[nodeid]:
            if c.get (id, 'status') == s_inactive:
                for dep_id in c.get (id, 'prereq'):
                    if dep_id != nodeid and c.get (dep_id, 'status') not in closed_statuses:
                        break
                else:
                    c.set (id, status=s_open)

def audit_update_active (db, c, nodeid, newvalues):
    global _nested
    if not _nested:
        _nested = True
        try:
            _audit_update_active (db, c, nodeid, newvalues)
        finally:
            _nested = False

def audit_fields (db, c, nodeid, newvalues):
    if ((not nodeid or not c.get (nodeid, 'status')) and
        not newvalues.get ('status')):
        newvalues['status'] = db.cstatus.filter (None, {'title': 'inactive'})[0]
            
def audit_retire (db, c, nodeid, newvalues):
    for id in c.list ():
        if id == nodeid:
            continue
        if id in c.get (nodeid, 'prereq'):
            raise Reject ("Deletion prevented since another checkpoint depends on this one: %s" % (id,))

def init (db):
    db.checkpoint.audit ('create', audit_fields)
    db.checkpoint.audit ('set', audit_fields)
    db.checkpoint.audit ('set', audit_update_active)
    db.checkpoint.audit ('retire', audit_retire)

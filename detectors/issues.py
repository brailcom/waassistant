### issue.py --- Issue auditors

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

_nested = False

def audit_issue_fields (db, c, nodeid, newvalues):
    for i in 'line', 'column',:
        if newvalues.has_key (i):
            newvalues[i] = newvalues[i] or '0'
        elif not nodeid:
            newvalues[i] = '0'
    if ((newvalues.has_key ('status') and not newvalues['status']) or
        (not nodeid and not newvalues.has_key ('status'))):
        newvalues['status'] = '1'

def _audit_issue_status (db, c, nodeid, newvalues):
    s_unhandled = '1'
    def issue_property (property):
        if newvalues.has_key (property):
            return newvalues[property]
        else:
            return db.issue.get (nodeid, property)
    # If an unhandled issue is handled, make clones of it
    if (db.issue.get (nodeid, 'status') == s_unhandled and
        newvalues.get ('status') and newvalues.get ('status') != s_unhandled and
        db.issue.get (nodeid, 'generated') and
        (not db.issue.get (nodeid, 'cloneof') or not newvalues.get ('cloneof', True))):
        properties = {}
        for p in 'test', 'kind', 'description',:
            properties[p] = issue_property (p)
        for id in db.issue.filter (None, properties):
            if id != nodeid and db.issue.get (id, 'generated') and not db.issue.get (id, 'cloneof'):
                db.issue.set (id, cloneof=nodeid)
    # If a clone is edited, it's no longer a clone
    elif (db.issue.get (nodeid, 'cloneof') and
          not newvalues.get ('cloneof')):
        newvalues['cloneof'] = None
    # If issue is set to unhandled, break its clones
    elif newvalues.get ('status') == s_unhandled:
        for id in db.issue.filter (None, {'cloneof': nodeid}):
            db.issue.set (id, cloneof=None)
        
def audit_issue_status (db, c, nodeid, newvalues):
    global _nested
    if not _nested:
        _nested = True
        try:
            _audit_issue_status (db, c, nodeid, newvalues)
        finally:
            _nested = False

def init (db):
    db.issue.audit ('create', audit_issue_fields)
    db.issue.audit ('set', audit_issue_fields)
    db.issue.audit ('set', audit_issue_status)

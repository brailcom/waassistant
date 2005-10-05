### misc.py --- Miscellaneous functions for use in page templates

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

def supervisors (db):
    users = []
    for id in db.user.list ():
        roles = db.user.get (id, 'roles').split (',')
        if 'Supervisor' in roles:
            users.append (db.user.get (id, 'username'))
    return users
    
def init (instance):
    instance.registerUtil ('supervisors', supervisors)

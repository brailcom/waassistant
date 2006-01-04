### misc.py --- Miscellaneous functions for use in page templates

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

import os

from roundup.configuration import UserConfig, CoreConfig, Option

CONFIGURATION_OPTIONS = (('wausers', ((Option, 'home', None, "Directory with the WAusers installation"),
                                      ),),)

def supervisors (db):
    users = []
    for id in db.user.list ():
        roles = db.user.get (id, 'allroles')
        if roles and 'Supervisor' in roles.split (','):
            users.append (db.user.get (id, 'username'))
    return users

def current_role (db, userid):
    return db.user.get (userid, 'roles')

def is_admin (db, username):
    userid = db.user.lookup (str (username))
    return userid and current_role (db, userid) == 'Admin'

def wausers_home (db):
    configuration = UserConfig (os.path.join (os.path.dirname (db.dir), 'configwa.ini'))
    return configuration.WAUSERS_HOME

def wausers_path (db):
    configuration = UserConfig (os.path.join (os.path.dirname (db.dir), 'configwa.ini'))
    home = configuration.WAUSERS_HOME
    if not home:
        return ''
    configuration = CoreConfig (home)
    return configuration.TRACKER_WEB
    
def init (instance):
    instance.registerUtil ('supervisors', supervisors)
    instance.registerUtil ('current_role', current_role)
    instance.registerUtil ('is_admin', is_admin)
    instance.registerUtil ('wausers_home', wausers_home)
    instance.registerUtil ('wausers_path', wausers_path)

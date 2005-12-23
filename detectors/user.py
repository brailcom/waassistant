### user.py --- User detectors

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

from roundup.configuration import UserConfig, Option
from roundup.exceptions import Reject

import os
import sys

CONFIGURATION_OPTIONS = (('wausers', ((Option, 'home', None, "Directory with the WAusers installation"),
                                      ),),)

def _react_registration (db, login, user, action):
    configuration = UserConfig (os.path.join (os.path.dirname (db.dir), 'configwa.ini'))
    wausers_path = configuration.WAUSERS_HOME
    if wausers_path and login not in ('admin', 'anonymous',):
        if wausers_path not in sys.path:
            sys.path.append (wausers_path)
        import waauth
        result = getattr (waauth, action) (db.config.TRACKER_NAME, login, user, configuration.WAUSERS_HOME)
        if result:
            raise Exception (result)

def react_register_user (db, c, nodeid, olddata):
    _react_registration (db, db.user.get (nodeid, 'username'), db.user.get (nodeid, 'wausername'), 'add_user')

def react_unregister_user (db, c, nodeid, olddata):
    _react_registration (db, olddata['username'], olddata['wausername'], 'remove_user')

def audit_register_user (db, c, nodeid, newvalues):
    configuration = UserConfig (os.path.join (os.path.dirname (db.dir), 'configwa.ini'))
    wausers_path = configuration.WAUSERS_HOME
    if wausers_path:
        if not nodeid and not newvalues.has_key ('wausername'):
            if newvalues.get ('username') not in ('admin', 'anonymous',):
                raise Reject ("No WAusers name given")
        if wausers_path not in sys.path:
            sys.path.append (wausers_path)
        import waauth
        if newvalues.has_key ('wausername'):
            if not waauth.check_user (newvalues['wausername'], configuration.WAUSERS_HOME):
                raise Reject ("WAusers name `%s' does not exist" % (newvalues['wausername'],))

def init (db):
    db.user.audit ('create', audit_register_user)
    db.user.audit ('set', audit_register_user)
    db.user.react ('create', react_register_user)
    db.user.react ('retire', react_unregister_user)

### login.py --- External authentication

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
import sys

import roundup.cgi.actions
import roundup.cgi.exceptions
from roundup.configuration import UserConfig, Option

CONFIGURATION_OPTIONS = (('wausers', ((Option, 'home', None, "Directory with the WAusers installation"),
                                      ),),)

class Login_Action (roundup.cgi.actions.LoginAction):

    def _verify_external_password (self, userid, password, tracker_home):
        import waauth
        user = self.db.user.get (userid, 'username')
        return waauth.authenticate (self.db.config.TRACKER_NAME, user, password, tracker_home)
        
    def verifyPassword (self, userid, password):
        configuration = UserConfig (os.path.join (os.path.dirname (self.db.dir), 'configwa.ini'))
        wausers_home = configuration.WAUSERS_HOME
        if wausers_home:
            if wausers_home not in sys.path:
                sys.path.append (wausers_home)
            return self._verify_external_password (userid, password, wausers_home)
        else:
            return roundup.cgi.actions.LoginAction.verifyPassword (self, userid, password)


class Chgrp_Action (roundup.cgi.actions.Action):

    def handle (self):
        try:
            role = self.form.getfirst ('role')
        except:
            role = None
        userid = self.userid
        db = self.db
        if role not in db.user.get (userid, 'allroles'):
            raise roundup.cgi.exceptions.Unauthorised ()
        db.user.set (userid, roles=role)
        db.commit ()
        self.client.ok_message.append ("Role changed")

def init (instance):
    instance.registerAction ('login', Login_Action)
    instance.registerAction ('chgrp', Chgrp_Action)

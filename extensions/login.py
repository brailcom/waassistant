### login.py --- External authentication and other login actions

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
import urllib

import roundup.cgi.actions
import roundup.cgi.client
import roundup.cgi.exceptions
from roundup.configuration import UserConfig, Option
import roundup.date

CONFIGURATION_OPTIONS = (('wausers', ((Option, 'home', None, "Directory with the WAusers installation",),
                                      (Option, 'auto_login', None, "Automatically login anonymous users",),
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

    def handle (self):
        roundup.cgi.actions.LoginAction.handle (self)
        self.client.opendb ('admin')
        db = self.client.db
        userclass = db.user
        username = self.client.user
        userid = userclass.lookup (username)
        lastlogin = userclass.get (userid, 'lastlogin')
        if not lastlogin:
            configuration = UserConfig (os.path.join (os.path.dirname (self.db.dir), 'configwa.ini'))
            wausers_home = configuration.WAUSERS_HOME
            if wausers_home:
                if wausers_home not in sys.path:
                    sys.path.append (wausers_home)
                import waauth
                user_data = waauth.user_data (username, wausers_home)
                userclass.set (userid, **user_data)
        userclass.set (userid, lastlogin=roundup.date.Date ())
        db.commit ()
        # Redirection
        try:
            redirect = self.form['__login_redirect'].value
        except:
            redirect = None
        if redirect:
            raise roundup.cgi.exceptions.Redirect (redirect)


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

    
def maybe_login (db, request):
    configuration = UserConfig (os.path.join (os.path.dirname (db.dir), 'configwa.ini'))
    if configuration.WAUSERS_AUTO_LOGIN:
        wausers_home = configuration.WAUSERS_HOME
        url = request.base
        query = request.env.get ('QUERY_STRING')
        if query:
            url = url + '?' + query
        if wausers_home:
            if configuration.WAUSERS_SAME_LOGIN:
                wu_configuration = UserConfig (os.path.join (wausers_home, 'config.ini'))
                raise roundup.cgi.exceptions.Redirect (
                    '%s?__login_redirect=%s&__login_project=%s' %
                    (wu_configuration.TRACKER_WEB, urllib.quote_plus (url), db.config.TRACKER_NAME,))
        else:
            base_url = url[:url.rfind ('/')+1]
            raise roundup.cgi.exceptions.Redirect ('%s?__login_redirect=%s' %
                                                   (base_url, urllib.quote_plus (url),))
    return ''


def init (instance):
    instance.registerAction ('login', Login_Action)
    instance.registerAction ('chgrp', Chgrp_Action)
    instance.registerUtil ('maybe_login', maybe_login)

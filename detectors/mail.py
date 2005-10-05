### mail.py --- E-mail sending reactors

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

import roundup.roundupdb

def supervisors (db):
    supervisors = []
    for id in db.user.list ():
        roles = db.user.get (id, 'roles')
        if roles and 'Supervisor' in roles.split (','):
            supervisors.append (id)
    return supervisors

def recipients (db, nosylist):
    recipients = supervisors (db)
    for id in nosylist:
        if id not in recipients:
            recipients.append (id)
    return recipients

def send_mail (db, recipient_ids, subject, text):
    import roundup.mailer
    author = (db.config.TRACKER_NAME, db.config.TRACKER_EMAIL,)
    recipients = [db.user.get (id, 'address') for id in recipient_ids]
    recipients = [address for address in recipients if address and address.find ('@') > 0]
    if not recipients:
        return
    try:
        mailer = roundup.mailer.Mailer (db.config)
        message, writer = mailer.get_standard_message (recipients, subject, author)
        body = writer.startbody ('text/plain')
        body.write (text)
        mailer.smtp_send (recipients, message)
    except Exception, e:
        raise roundup.roundupdb.DetectorError, e

def react_checkpoint (db, c, nodeid, olddata):
    # If the change was made by admin, don't report it.  This is mainly to
    # avoid reports during database setup.
    if db.user.get (c.get (nodeid, 'actor'), 'username') == 'admin':
        return
    if olddata and (not olddata.has_key ('status') or olddata['status'] == db.checkpoint.get (nodeid, 'status')):
        return
    recipients_ = recipients (db, c.get (nodeid, 'nosy'))
    if olddata:
        subject = "Checkpoint status changed"
        message = ("Checkpoint status was changed from `%s' to `%s':" %
                   (db.cstatus.get (olddata['status'], 'title'),
                    db.cstatus.get (db.checkpoint.get (nodeid, 'status'), 'title'),))
    else:
        subject = "New checkpoint created"
        message = "New checkpoint was created:"
    message = message + ('\n%scheckpoint%s' % (db.config.TRACKER_WEB, nodeid,))
    send_mail (db, recipients_, subject, message)

def react_msg (db, c, nodeid, olddata):
    old_messages = (olddata and olddata.get ('messages')) or []
    for id in c.get (nodeid, 'messages'):
        if id not in old_messages:
            try:
                c.nosymessage (nodeid, id, olddata)
            except Exception, e:
                raise roundupdb.DetectorError, message

def audit_nosy (db, c, nodeid, newvalues):
    if newvalues.has_key ('nosy'):
        nosylist = newvalues['nosy']
    elif nodeid:
        nosylist = c.get (nodeid, 'nosy')
    else:
        nosylist = []
    # Add Supervisors for new items
    if not nodeid:
        for id in supervisors (db):
            if id not in nosylist:
                nosylist.append (id)
    # Add creator for new items
    if not nodeid and newvalues.has_key ('creator'):
        nosylist.append (newvalues['creator'])
    # Add assignedto for new items or if changed
    assigned = newvalues.get ('assignedto')
    if (assigned and
        assigned not in nosylist and
        (not nodeid or c.get (nodeid, 'assignedto') != assigned)):
        nosylist.append (assigned)
    # Add new message authors
    if nodeid:
        old_messages = c.get (nodeid, 'messages')
    else:
        old_messages = []
    add_author = (db.config.NOSY_ADD_AUTHOR == 'yes' or
                  (db.config.NOSY_ADD_AUTHOR == 'new' and not nodeid))
    add_recipients = (db.config.NOSY_ADD_RECIPIENTS == 'yes' or
                      (db.config.NOSY_ADD_RECIPIENTS == 'new' and not nodeid))
    for mid in newvalues.get ('messages', []):
        if mid not in old_messages:
            if add_author:
                id = db.msg.get (mid, 'author')
                if id and id not in nosylist:
                    nosylist.append (id)
            if add_recipients:
                for id in (db.msg.get (id, 'recipients') or []):
                    if id not in nosylist:
                        nosylist.append (id)
    # Set the list
    nosylist = [id for id in nosylist if db.hasnode ('user', id)]
    newvalues['nosy'] = nosylist

def init (db):
    # Checkpoint status change notifications
    db.checkpoint.react ('create', react_checkpoint)
    db.checkpoint.react ('set', react_checkpoint)
    # Messages
    for cname in db.getclasses ():
        c = db.getclass (cname)
        if c.getprops ().has_key ('nosy'):
            c.react ('create', react_msg)
            c.react ('set', react_msg)
            c.audit ('create', audit_nosy)
            c.audit ('set', audit_nosy)


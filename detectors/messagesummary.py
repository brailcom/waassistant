from roundup.mailgw import parseContent

def audit_message (db, c, nodeid, newvalues):
    if newvalues.has_key ('summary') or not newvalues.has_key ('content'):
        return
    summary, _content = parseContent (newvalues['content'], 1, 1)
    newvalues['summary'] = summary

def init (db):
    db.msg.audit ('create', audit_message)

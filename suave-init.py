#!/usr/bin/env python
from flask.ext.suave import create_app, db

def init():
    print "We need to create a superuser..."
    SU_USERNAME = raw_input('\t username? ')
    SU_PASSWORD = raw_input('\t password? ')
    SU_EMAIL    = raw_input('\t email? ')
    SU_FIRSTNAME= raw_input('\t first name? ')
    SU_SURNAME  = raw_input('\t surname? ')
    print "Thanks! Doing things now..."

    db.app = create_app()
    print "Bound database."

    from flask.ext.suave.models import User, Group, Permission


    # Add permissions
    perms = [
        ('manage_users', 'Manage Users'),
        ('view_logs', 'View Log Entries'),
    ]

    permissions = {}
    for name, title in perms:
        p = Permission(name, title)
        permissions[name] = p
        db.session.add(p)

    db.session.commit()
    print "Added permissions."

    # Basic User
    g_user = Group(name='User')
    db.session.add(g_user)

    # Administrator
    g_admin = Group(name='Administrator')
    for name in ['view_logs']:
        g_admin.permissions.append(permissions[name])
    db.session.add(g_admin)

    # Super User
    g_su = Group(name='Super User')
    for name, _ in perms:
        g_su.permissions.append(permissions[name])
    db.session.add(g_su)

    # Commit users
    db.session.commit()
    print "Added groups."

    # Create our first SU
    u = User(
        g_su,
        username=SU_USERNAME,
        password=SU_PASSWORD,
        email=SU_EMAIL,
        firstname=SU_FIRSTNAME,
        surname=SU_SURNAME,
        status='active'
    )

    db.session.add(u)

    db.session.commit()
    print "Added superuser %s" % u

if __name__ == '__main__':
    init()
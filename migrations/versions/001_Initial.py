from sqlalchemy import *
from migrate import *

meta = MetaData()

permission = Table(
    'suave_permission', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(255), unique=True),
    Column('title', String(255))
)

group = Table(
    'suave_group', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(255), unique=True)
)

permissions = Table(
    'suave_permissions', meta,
    Column('suave_permission_id', Integer, ForeignKey('suave_permission.id')),
    Column('suave_group_id', Integer, ForeignKey('suave_group.id'))
)

user = Table(
    'suave_user', meta,
    Column('id', Integer, primary_key=True),
    Column('username', String(255), unique=True),
    Column('password', String(255), nullable=False),
    Column('firstname', String(80), nullable=False),
    Column('location', String(80)),
    Column('surname', String(80), nullable=False),
    Column('website', String(255)),
    Column('email', String(120), nullable=False),
    Column('phone', String(80)),
    Column('twitter', String(80)),
    Column('group_id', Integer, ForeignKey('suave_group.id'))
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    permission.create()
    group.create()
    permissions.create()
    user.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    user.drop()
    permissions.drop()
    group.drop()
    permission.drop()
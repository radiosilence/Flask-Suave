from sqlalchemy import *
from migrate import *

meta = MetaData()

log_entry = Table(
    'suave_log_entry', meta,
    Column('id', Integer, primary_key=True),
    Column('subject_id', Integer, ForeignKey('suave_user.id')),
    Column('target_id', Integer),
    Column('verb', String(255)),
    Column('when', DateTime),
    Column('class_name', String(255))
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    user = Table('suave_user', meta, autoload=True)
    log_entry.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    log_entry.drop()
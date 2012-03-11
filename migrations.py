#!/usr/bin/env python
from migrate.versioning.shell import main
import sys
import os
sys.path.insert(-1, os.getcwd())


def run_on(repo, db_url):
    main(url=db_url, debug='False', repository=repo, name=repo)


if __name__ == '__main__':

    from app import app

    db_url = app.config['SQLALCHEMY_DATABASE_URI']

    if sys.argv[1] == 'suave':
        repo = 'migrations_suave'
    elif sys.argv[1] == 'local':
        repo = 'migrations'
    else:
        exit("You must specify migrations as either suave or local.")
    del sys.argv[1]
    run_on(repo, db_url)

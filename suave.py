#!/usr/bin/env python
import sys
import os
from migrate.versioning.shell import main as migrate_main

sys.path.insert(-1, os.getcwd())

def create(app_name):
    print "Creating app %s in dir of same name..." % app_name
    # Generate folder layout
    # Create app.py
    # Create settings.py
    # Symlink suave migrations dir


def _migrate():
    def run_on(repo, db_url):
        migrate_main(url=db_url, debug='False', repository=repo, name=repo)


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

def main():
    try:
        if sys.argv[1] == 'create':
            if len(sys.argv) < 3:
                exit("Usage: suave create <app name>")
            create(sys.argv[2])
        elif sys.argv[1] == 'migrate':
            del sys.argv[0]
            _migrate()
    except IndexError:
        exit('Try a command?')

if __name__ == '__main__':
    main()
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

    from app import app

    db_url = app.config['SQLALCHEMY_DATABASE_URI']

    repo = 'migrations_%s' % sys.argv[1]
    if not os.path.exists(repo) and sys.argv[2] != 'create':
        exit("You must specify a valid migration repo.")
    del sys.argv[1]
    migrate_main(url=db_url, debug=False, repository=repo, name=repo)

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
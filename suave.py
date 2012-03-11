import sys


def create(app_name):
    print "Creating app %s in dir of same name..." % app_name


def main():
    if sys.argv[1] == 'create':
        if len(sys.argv) < 3:
            exit("Usage: suave create <app name>")
        create(sys.argv[2])

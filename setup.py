"""
Flask-SQLite3
-------------

This is the description for that library
"""
from setuptools import setup


setup(
    name='Flask-Suave',
    version='0.1',
    url='https://github.com/radiosilence/flask-suave/',
    license='BSD',
    author='James Cleveland',
    author_email='jamescleveland@gmail.com',
    description='Admin panel for Flask',
    long_description=__doc__,
    packages=['flask_suave'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_sqlite3'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask', 'Flask-SQLAlchemy', 'SQLAlchemy'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

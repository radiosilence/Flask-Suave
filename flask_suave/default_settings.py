# Default Configuration
DEBUG = False
SECRET_KEY = ''
LOG_LOCATION = 'error.log'
SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

# Get a key from http://code.google.com/apis/maps/signup.html
GMAPS_KEY = ''
STATIC_PATH = '/'

CACHE_TYPE = 'flask.ext.cache_pylibmc.pylibmc'
CACHE_KEY_PREFIX = 'btnfemcol'

CACHE_MEMCACHED_SERVERS = ['127.0.0.1']
CACHE_MEMCACHED_BINARY = True
CACHE_MEMCACHED_BEHAVIORS = {
    "tcp_nodelay": True,
    "ketama": True
}

MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = None
MAIL_PASSWORD = None

DEFAULT_MAIL_SENDER = ('Suave Application',
    'suave@localhost')

try:
    from .app_settings import *
except ImportError:
    pass
try:
    from .local_settings import *
except ImportError:
    pass

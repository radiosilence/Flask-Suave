from __future__ import absolute_import

from flask import _request_ctx_stack, Blueprint

from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail


admin = Blueprint('admin', __name__,
    template_folder='templates')

db = SQLAlchemy()
cache = Cache()
mail = Mail()


class Suave(object):
    def __init__(self, app=None, **kwargs):
        self.blueprint = admin
        if app is not None:
            self.app = app
            self.init_app(self.app, **kwargs)
        else:
            self.app = None

    def init_app(self, app, url_prefix='/admin'):
        self.app = app
        self.app.teardown_request(self.teardown_request)
        self.app.before_request(self.before_request)
        self.app.register_blueprint(self.blueprint, url_prefix=url_prefix)

        # Initialise database
        db.app = app
        db.init_app(app)

        # Initialise cache
        cache.init_app(app)

        # Initialise Mail
        mail.init_app(app)

        import flask.ext.suave.views

    def before_request(self):
        ctx = _request_ctx_stack.top

    def teardown_request(self, exception):
        ctx = _request_ctx_stack.top

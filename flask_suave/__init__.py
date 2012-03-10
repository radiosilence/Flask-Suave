from __future__ import absolute_import

from flask import _request_ctx_stack, Blueprint

admin = Blueprint('admin', __name__,
    template_folder='templates')

class Suave(object):
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app, url_prefix='/admin'):
        self.app = app
        self.app.teardown_request(self.teardown_request)
        self.app.before_request(self.before_request)

        app.register_blueprint(admin, url_prefix=url_prefix)

    def before_request(self):
        ctx = _request_ctx_stack.top

    def teardown_request(self, exception):
        ctx = _request_ctx_stack.top

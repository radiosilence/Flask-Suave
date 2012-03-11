from __future__ import absolute_import


from flask import Flask, render_template, flash, g, session, \
    _request_ctx_stack, Blueprint

from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.markdown import Markdown


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
                
        self.configure_base_views()
        self.configure_pre_post_request()
        
        if app.config['SECRET_KEY'] == '':
            print 'Please setup a secret key in local_settings.py!!!'

        # Initialise database
        db.app = app
        db.init_app(app)
        # Initialise cache
        cache.init_app(app)
        # Initialise Mail
        mail.init_app(app)


        # Initialise Markdown
        Markdown(app,
            extensions=[
                'extra',
                'wikilinks',
                'toc'
            ],
            output_format='html5',
            safe_mode=True
        )

        import flask.ext.suave.views
        self.app.register_blueprint(self.blueprint, url_prefix=url_prefix)

    def before_request(self):
        ctx = _request_ctx_stack.top

    def teardown_request(self, exception):
        ctx = _request_ctx_stack.top


    def configure_logging(self):
        file_handler = FileHandler(app.config['LOG_LOCATION'],
            encoding="UTF-8")
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(funcName)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)

    def configure_base_views(self):
        
        @self.app.errorhandler(401)
        def unauthorized(error):
            return self._status(error), 401

        @self.app.errorhandler(404)
        def not_found(error):
            return self._status(error), 404

        @self.app.errorhandler(500)
        def fuckup(error):
            return self._status("500: Internal Server Error"), 500

    def configure_pre_post_request(self):
        from .models import User

        @self.app.before_request
        def before_request():
            g.logged_in = False
            try:
                if session['logged_in']:
                    g.logged_in = True
                    key = 'user:id:%s' % session['logged_in']
                    user = cache.get(key)
                    if user:
                        user = db.session.merge(user, load=False)
                    else:
                        user = User.query.filter_by(id=session['logged_in']).first()
                        cache.set(key, user, 5)
                    g.user = user
            except KeyError:
                pass


        @self.app.after_request
        def after_request(response):
            """Closes the database again at the end of the request."""
            return response
            

    def _status(self, error):
        status = [x.strip() for x in str(error).split(":")]
        try:
            return render_template('status.html',
                _status=status[0],
                _message=status[1]
                )
        except:
            return """<h1>%s</h1><p>%s</p>""" % (status[0], status[1])


def create_app(debug=False):
    suave = Suave()
    # Change static path based on whether we're debugging.
    if debug:
        print "Debug mode."
        app = Flask(__name__, static_path='/static')

    else:
        app = Flask(__name__, static_path='')

    # Handle configuration
    app.config.from_object('settings')
    app.config.from_envvar('SUAVE_SETTINGS', silent=True)
    app.config['DEBUG'] = debug
    
    suave.init_app(app)

    return app
import random
from datetime import datetime
import urllib
import hashlib

from flask import g, url_for, render_template

from flaskext.mail import Message

from .auth import Hasher
from flask.ext.suave import db, cache, mail


class SiteEntity(object):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    title = db.Column(db.String(120), unique=True, nullable=False)
    status = db.Column(db.String(255))
    order = db.Column(db.Integer)

    def __init__(self, title=None, slug=None, body=None, order=0,
        status='draft'):

        self.slug = slug
        self.title = title
        self.status = status
        self.order = order

    def __unicode__(self):
        return unicode(self.title)


class Displayable(SiteEntity):
    body = db.Column(db.Text, nullable=False)

    def __init__(self, body=None, *args, **kwargs):
        self.body = body
        super(Displayable, self).__init__(*args, **kwargs)

    @property
    @cache.memoize(60)
    def excerpt(self):
        if not self.body:
            return ''
        if len(self.body) > 140:
            ellip = u'\u2026'
        else:
            ellip = ''
        chars = list('[]#*-=!')

        excerpt = self.body[:340]
        for char in chars:
            excerpt = excerpt.replace(char, '')
        return excerpt[:140] + ellip


class User(db.Model):
    __tablename__ = 'suave_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(80))
    surname = db.Column(db.String(80), nullable=False)
    website = db.Column(db.String(255))
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(80))
    twitter = db.Column(db.String(80))
    group_id = db.Column(db.Integer, db.ForeignKey('suave_group.id'))
    group = db.relationship('Group',
        backref=db.backref('users', lazy='dynamic'))
    status = db.Column(db.String(10))
    reg_code = db.Column(db.String(255))

    def __init__(self, group=None, username=None, email=None, firstname=None,
        surname=None, password=None, website=None, phone=None, twitter=None,
        status='pending',
        *args, **kwargs):

        if password:
            h = Hasher()
            self.password = h.hash(password)

        if not group:
            group = Group.query.filter_by(name='User').first()

        self.username = username
        self.firstname = firstname
        self.surname = surname
        self.email = email
        self.group = group
        self.group_id = group.id
        self.website = website
        self.twitter = twitter
        self.phone = phone
        self.status = status
        super(User, self).__init__(*args, **kwargs)

#    @cache.memoize(20)
    def allowed_to(self, name):
        """This will check if a user can do a certain action."""
        if self.status != 'active':
            return False
        permission = Permission.query.filter_by(name=name).first()
        return permission in self.group.permissions.all()

    def send_activation_email(self, view):
        """Send the e-mail that allows a user to activate their account."""
        if not self.reg_code:
            self._gen_reg_code()
            db.session.commit()

        msg = Message("Account Activation",
            recipients=[self.email])

        print self.reg_code
        activate_url = url_for(view, user_id=self.id,
            reg_code=self.reg_code, _external=True)
        msg.html = render_template('email_activate.html', user=self,
            activate_url=activate_url)
        msg.body = render_template('email_activate.txt', user=self,
            activate_url=activate_url)
        mail.send(msg)

    def _gen_reg_code(self):
        chrs = list(
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')

        string = ''
        for i in range(20):
            string += random.choice(chrs)
        self.reg_code = string

    @property
    @cache.memoize(20)
    def gravatar_url(self, size=100):
        size = int(size)
        default = url_for('static', filename='images/av_def_%s.png' % size)
        gravatar_url = "http://www.gravatar.com/avatar/" + \
            hashlib.md5(self.email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({
            'd': default,
            's': str(size)
        })
        return gravatar_url

    @property
    @cache.memoize(60)
    def displayed_name(self):
        return unicode(self.username)

    @property
    @cache.memoize(60)
    def fullname(self):
        return u'%s %s' % (self.firstname, self.surname)

    def __repr__(self):
        return '<User %r>' % self.username

    @cache.memoize(5)
    def __unicode__(self):
        return '%s (%s) <%s>' % (
            self.fullname,
            self.username,
            self.email
        )

    @property
    @cache.memoize(300)
    def url(self):
        return '#'

    @property
    @cache.memoize(5)
    def json_dict(self, exclude=[]):
        """This is a form of serialisation but specifically for the output to
        JSON for asyncronous requests."""
        d = {
            'id': self.id,
            'username': self.username,
            'firstname': self.firstname,
            'surname': self.surname,
            'location': self.location,
            'website': self.website,
            'twitter': self.twitter,
            'group': self.group.name,
            'status': self.status,
            'urls': {
                'edit': url_for('admin.edit_user', id=self.id),
                'bin': '#'
            }
        }
        for key in exclude:
            del d[key]
        return d


permissions = db.Table('suave_permissions',
    db.Column('permission_id', db.Integer, db.ForeignKey('suave_permission.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('suave_group.id'))
)


class Group(db.Model):
    __tablename__ = 'suave_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)

    def __init__(self, name=None):
        self.name = name

    @cache.memoize(6000)
    def __unicode__(self):
        return u'%s' % self.name

    def __repr__(self):
        return '<Group %r>' % self.name


class Permission(db.Model):
    __tablename__ = 'suave_permission'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(255))

    groups = db.relationship('Group', secondary=permissions,
        backref=db.backref('permissions', lazy='dynamic'))

    def __init__(self, name, title):
        self.name = name
        self.title = title

    def __repr__(self):
        return '<Permission %s:%r>' % (self.id, self.name)


class LogEntry(db.Model):
    __tablename__ = 'suave_log_entry'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('suave_user.id'))
    subject = db.relationship('User',
        backref=db.backref('actions', lazy='dynamic'))
    target_id = db.Column(db.Integer)
    verb = db.Column(db.String(255))
    when = db.Column(db.DateTime)
    class_name = db.Column(db.String(127))

    def __init__(self, verb, subject=None, class_name=None, target=None):
        if not subject:
            subject = g.user
        self.subject = subject
        self.verb = verb
        self.when = datetime.utcnow()
        self.class_name = class_name
        if target:
            self.class_name = target.__class__.__name__
            self.target_id = target.id

    @classmethod
    def log(cls, *args, **kwargs):
        log_entry = cls(*args, **kwargs)
        db.session.add(log_entry)
        db.session.commit()

    def __repr__(self):
        return '<LogEntry %s>' % self.id

    def __unicode__(self, date=True):
        if date:
            string = '[%s] ' % self.when
        else:
            string = ''

        if not self.subject_id:
            subject_name = "(not attributed)"
        else:
            subject_name = self.subject.username

        string += '%(subject)s %(verb)s' % {
            'when': self.when,
            'subject': subject_name,
            'verb': self.verb
        }

        if self.target_id:
            string += ' %s #%s' % (self.class_name, self.target_id)
        return string

    @property
#    @cache.memoize(500)
    def json_dict(self, exclude=[]):
        """This is a form of serialisation but specifically for the output to
        JSON for asyncronous requests."""

        if not self.subject_id:
            subject_url = '#'
        else:
            subject_url = self.subject.url

        d = {
            'id': self.id,
            'entry': self.__unicode__(date=False),
            'when': self.when.strftime('%Y/%m/%d %H:%m:%S'),
            'urls': {
                'user': subject_url
            }
        }
        for key in exclude:
            del d[key]
        return d

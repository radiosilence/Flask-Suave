from .models import User, Group

from flask.ext.wtf import Form, ValidationError, PasswordField, SelectField, \
    Required, url, TextField

from flask.ext.wtf.html5 import DateField
from wtforms.ext.sqlalchemy.orm import model_form

from .auth import Hasher


class Unique(object):
    """Validator that checks field uniqueness."""
    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = 'Must be unique.'
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data) \
            .filter(self.model.id != form._model.id) \
            .first()

        if check:
            raise ValidationError(self.message)


class PasswordValidator(object):
    """Validator that throws an error if the password is blank but only if it
    is a new object"""

    def __init__(self, message=None):
        if not message:
            message = "Password must be set."
        self.message = message

    def __call__(self, form, field):
        if not form._model.password and len(field.data) < 1:
            raise ValidationError(self.message)


class ForeignKeyField(SelectField):
    def __init__(self, query, **kwargs):
        super(ForeignKeyField, self).__init__(choices=query.all(), **kwargs)
        self.coerce = int

    def pre_validate(self, form):
        if not self.data:
            return False
        for v in self.choices:
            if self.coerce(self.data) == v.id:
                break
        else:
            raise ValueError(self.gettext(u'Not a valid choice'))

    def iter_choices(self):
        yield (None, 'Please select...', not self.data)
        if not self.data:
            self.data = -1
        for choice in self.choices:
            yield (choice.id, u'%s' %
                choice, choice.id == self.coerce(self.data))

    def process_formdata(self, valuelist):
        if not valuelist:
            return False
        if valuelist:
            try:
                self.data = self.coerce(valuelist[0])
            except ValueError:
                raise ValueError(self.gettext(u'Not a valid choice'))


class SectionField(ForeignKeyField):
    def iter_choices(self):
        if not self.data:
            self.data = 1
        for choice in self.choices:
            yield (choice.id, u'%s' %
                choice, choice.id == self.coerce(self.data))


# User Forms
UserFormBase = model_form(User, Form, exclude=['id', 'reg_code'], field_args={
    'username': {
        'validators': [
            Unique(User, User.username)
        ],
        'description': 'Eg. lady_derpington'
    },
    'firstname': {
        'label': u'First Name',
        'validators': [
            Required()
        ],
        'description': 'Eg. Jane'
    },
    'surname': {
        'validators': [
            Required()
        ],
        'description': 'Eg. Derp'
    },
    'website': {
        'label': u'URL',
        'validators': [
            url(),
        ],
        'description': 'Eg. http://www.derpsworth.com'
    },
    'email': {
        'validators': [
            Required(),
            Unique(User, User.email)
        ],
        'description': 'Eg. derping@gmail.com'
    },
    'phone': {
        'description': 'Eg. 07688283555'
    },
    'twitter': {
        'description': 'Eg. @derpslife'
    }
})


class UserEditForm(UserFormBase):
    password = PasswordField('Password',
        [PasswordValidator()])
    group_id = ForeignKeyField(Group.query, label='Group')
    status = SelectField(choices=[
        ('pending', 'Pending Activation'),
        ('active', 'Activated'),
        ('banned', 'Banned')
    ])

    def __init__(self, form, user, *args, **kwargs):
        self._model = user
        super(UserEditForm, self).__init__(form, user, *args, **kwargs)

    def populate_obj(self, user):
        if len(self.password.data) < 1:
            self.password.data = user.password
        else:
            h = Hasher()
            self.password.data = h.hash(self.password.data)

        super(UserEditForm, self).populate_obj(user)


# Generic Forms
class LoginForm(Form):
    username = TextField('Username')
    password = PasswordField('Password')

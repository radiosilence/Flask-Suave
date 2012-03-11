from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash

from flask.ext.suave import admin, db

from .models import User, LogEntry
from .forms import UserEditForm, LoginForm
from .utils import auth_logged_in, auth_allowed_to, admin_section, \
    edit_instance, json_inner, log_out
from .auth import Auth, AuthError, AuthInactiveError


# User Views
@admin.route('/users')
@auth_logged_in
@auth_allowed_to('manage_users')
@admin_section('users')
def list_users():
    return render_template('users.html')


@admin.route('/user/new', methods=['GET', 'POST'])
@auth_logged_in
@auth_allowed_to('manage_users')
@admin_section('users')
def create_user():
    return edit_user()


@admin.route('/user/<int:id>', methods=['GET', 'POST'])
@auth_logged_in
@auth_allowed_to('manage_users')
@admin_section('users')
def edit_user(id=None):
    return edit_instance(User, UserEditForm, id=id)


@admin.route('/async/users')
@auth_logged_in
@auth_allowed_to('manage_users')
@admin_section('users')
def json_users():
    return json_inner(User, User.query, filter_field=User.username)


# Log entries
@admin.route('/logs')
@auth_logged_in
@auth_allowed_to('view_logs')
@admin_section('logs')
def view_logs():
    return render_template('logs.html')


@admin.route('/async/logs')
@auth_logged_in
@auth_allowed_to('view_logs')
@admin_section('logs')
def json_logs():
    return json_inner(LogEntry, LogEntry.query.order_by(LogEntry.when.desc()),
        filter_field=LogEntry.verb)


# Dashboards
@admin_section('logs')
@auth_allowed_to('manage_pages')
def dashboard_administrator():
    """Administrator dashboard will cover page editing, event uploading, user
    management."""
    return view_logs()


@admin_section('users')
@auth_allowed_to('manage_site')
def dashboard_superuser():
    """Superuser can anything an admin can, but with the ability to change site
    settings, manage permissions, etc."""
    return list_users()


# Generic Views
@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        a = Auth(session, db, User)
        try:
            g.user = a.log_in(form.username.data, form.password.data)
            session['logged_in'] = g.user.id
            flash("Successfully logged in.", 'success')
            return redirect(url_for('admin.home'))
        except AuthInactiveError:
            flash('This user account has not been activated.', 'error')
        except AuthError:
            flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form, submit='Login')


@admin.route('/logout')
@auth_logged_in
def logout():
    log_out()
    return redirect(url_for('admin.login'))


@admin.route('/')
@auth_logged_in
def home():
    # Do some logic to get the right dashboard for the person
    if g.user.group.name == 'Administrator' \
        or g.user.group.name == 'Super User':
        return dashboard_administrator()
    else:
        return abort(403)

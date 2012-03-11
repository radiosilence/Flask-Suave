"""Admin specific utility functions and classes."""
import math
import json

from functools import wraps
from flask import g, redirect, flash, url_for, abort, request, \
    render_template, session

from .models import LogEntry

def edit_instance(cls, form_cls, edit_template='form.html', id=None,
    submit_value=None, view=None, callback=None, **kwargs):


    if id:
        instance = cls.query.filter_by(id=id).first()
        if not instance:
            return abort(404)
    else:
        instance = cls()
    if not submit_value and id:
        submit_value = 'Update'
    else:
        submit_value = 'Create'
    form = form_cls(request.form, instance)    
    saved, created = save_instance(form, instance, **kwargs)
    if not view:
        view = 'admin.edit_%s' % cls.__name__.lower()
    if saved:
        if created:
            verb = 'created'
        else:
            verb = 'edited'

        if cls.__name__ == 'User' and created:
            subject = saved
        else:
            subject = g.user            
        LogEntry.log(verb, target=saved, subject=subject)
        if callback:
            return callback(id, saved, created, form)
        else:
            return redirect(url_for(view, id=saved.id))
    return render_template(edit_template, form=form, submit=submit_value)


def save_instance(form, instance, message=u"%s saved.", do_flash=True):
    """This function handles the simple cyle of testing if an instance's form
    validates and then saving it.
    """
    if request.method == 'POST':
        if not form.validate():
            flash("There were errors saving, see below.", 'error')
            return False, False
        form.populate_obj(instance)
        if not instance.id:
            created = True
            db.session.add(instance)
        else:
            created = False
        db.session.commit()
        if do_flash:
            flash(message % instance.__unicode__(), 'success')
        return instance, created
    return False, False

def log_out():
    g.user = None
    del session['logged_in']
    flash('Logged out.')

def logged_in():
    try:
        user = g.user
        if not user  or user.status == 'banned':
            return False
    except AttributeError:
        return False
    return True

def auth_logged_in(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            if not logged_in() :
                raise AuthPermissionDeniedError("Not logged in.")
        except (AttributeError, AuthPermissionDeniedError):
            flash("You must be logged in to view this page.", 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated

def auth_allowed_to(permission):
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            try:
                user = g.user
                if user.allowed_to(permission):
                    return f(*args, **kwargs)
                raise AuthPermissionDeniedError("Not allowed to do this.")
            except (AttributeError, AuthPermissionDeniedError):
                return abort(403)
        return inner
    return decorator

def admin_section(name):
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            g.section = name
            return f(*args, **kwargs)
        return inner
    return decorator


def calc_pages(results, per_page):
    return int(math.ceil(float(results) / float(per_page)))


def json_inner(cls, base, status=None, page=None, per_page=None, filter=None,
    order=None, filter_field=None):
    """This function handles getting json for instances once arguments have
    already been decided.
    """
    if not filter_field:
         filter_field = cls.title
    if not status:
        status = request.args.get('status', default='any')
    if not page:
        page = request.args.get('page', default=1, type=int)
    if not per_page:
        per_page = request.args.get('per_page', default=20, type=int)
    if not filter:
        filter = request.args.get('filter', default=None)

    start = per_page * (page - 1)
    end = per_page * page

    if filter and status != 'any':
        q = base.filter_by(status=status).filter(
            filter_field.like('%' + filter + '%'))
    elif filter:
        q = base.filter(
            filter_field.like('%' + filter + '%'))
    elif status == 'any':
        q = base
    else:
        q = base.filter_by(status=status)
    
    if order:
        q = q.order_by(*order)

    instances = q[start:end]
    num_pages = calc_pages(q.count(), per_page)
    return json.dumps({
        'items': [o.json_dict for o in instances],
        'num_pages': num_pages
    })


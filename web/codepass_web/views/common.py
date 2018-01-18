import functools
import json
import markdown

from datetime import datetime
from flask import Blueprint, request, redirect, session, url_for, flash, render_template, jsonify, abort, Response, \
    current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, InputRequired, EqualTo
from sqlalchemy.exc import IntegrityError
from ..models import *
from .. import constants


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login.', 'danger')
            return redirect(url_for('user.get_login'))
        return f(*args, **kwargs)

    return decorated_function


def row_to_dict(row):
    d = dict(row.__dict__)
    d.pop('_sa_instance_state', None)
    return d


def markdown_to_html5(text):
    html = markdown.markdown(text, output_format='html5')
    # html = bleach.clean(html)  # FIXME
    return html

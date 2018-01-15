import functools

from datetime import datetime
from flask import Blueprint, request, redirect, session, url_for, flash, render_template, jsonify, abort, Response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, InputRequired, EqualTo
from sqlalchemy.exc import IntegrityError
from ..models import *


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login.', 'danger')
            return redirect(url_for('user.get_login'))
        return f(*args, **kwargs)

    return decorated_function

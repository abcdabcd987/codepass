from .common import *

mod = Blueprint('user', __name__)


def guest_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            flash(constants.TextUserAlreadyLoggedIn, 'danger')
            return redirect(url_for('homepage.get_homepage'))
        return f(*args, **kwargs)

    return decorated_function


def set_session_login(user):
    session['user_id'] = user.id
    session['user_username'] = user.username


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])


@mod.route('/login')
@guest_required
def get_login():
    form = LoginForm()
    return render_template('user/login.html', form=form)


@mod.route('/login', methods=['POST'])
@guest_required
def post_login():
    while True:
        form = LoginForm()
        if not form.validate():
            break
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if not user:
            flash(constants.TextUserWrongPassword, 'danger')
            break
        if user.password != form.password.data:
            flash(constants.TextUserWrongPassword, 'danger')
            break

        set_session_login(user)
        flash(constants.TextUserLoginSuccess, 'success')
        return redirect(url_for('homepage.get_homepage'))

    return render_template('user/login.html', form=form)


class RegisterForm(FlaskForm):
    username = StringField('Username', [InputRequired(constants.TextInputRequired)])
    password = PasswordField('Password', [InputRequired(constants.TextInputRequired)])
    confirm = PasswordField('Confirm', [InputRequired(constants.TextInputRequired),
                                        EqualTo('password', constants.TextPasswordMismatch)])


@mod.route('/register')
@guest_required
def get_register():
    form = RegisterForm()
    return render_template('user/register.html', form=form)


@mod.route('/register', methods=['POST'])
@guest_required
def post_register():
    while True:
        form = RegisterForm()
        if not form.validate():
            break
        user = User(username=form.username.data,
                    password=form.password.data,
                    created_at=datetime.utcnow())

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            flash(constants.TextUserUsernameOccupied, 'warning')
            break

        user = db.session.query(User).filter(User.username == form.username.data).one()
        set_session_login(user)
        flash(constants.TextUserRegisterSuccess, 'success')
        return redirect(url_for('homepage.get_homepage'))

    return render_template('user/register.html', form=form)


@mod.route('/logout')
def get_logout():
    session.clear()
    flash(constants.TextUserLogout, 'success')
    return redirect(url_for('homepage.get_homepage'))

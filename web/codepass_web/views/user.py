from .common import *

mod = Blueprint('user', __name__)


def guest_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            flash('You have already logged in.', 'danger')
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
            flash('Incorrect combination of username and password.', 'danger')
            break
        if user.password != form.password.data:
            flash('Incorrect combination of username and password.', 'danger')
            break

        set_session_login(user)
        flash('Successfully registered', 'success')
        return redirect(url_for('homepage.get_homepage'))

    return render_template('user/login.html', form=form)


class RegisterForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
    confirm = PasswordField('Confirm', [InputRequired(), EqualTo('password', 'Passwords must match.')])


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
            flash('The username has been occupied. Please try another one.', 'warning')
            break

        user = db.session.query(User).filter(User.username == form.username.data).one()
        set_session_login(user)
        flash('Successfully registered', 'success')
        return redirect(url_for('homepage.get_homepage'))

    return render_template('user/register.html', form=form)


@mod.route('/logout')
def get_logout():
    session.clear()
    flash('You have logged out.', 'success')
    return redirect(url_for('homepage.get_homepage'))

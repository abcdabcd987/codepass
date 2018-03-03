from .common import *

mod = Blueprint('submission', __name__)


class SubmitForm(FlaskForm):
    problem_id = IntegerField('Problem ID', [InputRequired('This field is required.')])
    language_id = SelectField('Language', [InputRequired('This field is required.')], coerce=int)
    code = TextAreaField('Compile Command', [InputRequired('This field is required.')])


@mod.route('/submit/')
@mod.route('/submit/<int:problem_id>')
@login_required
def get_submit(problem_id=None):
    form = SubmitForm()
    if problem_id:
        form.problem_id.data = problem_id
    languages = db.session.query(Language).order_by(Language.id).all()
    form.language_id.choices = [(l.id, l.name) for l in languages]
    return render_template('submission/submit.html', form=form)


@mod.route('/submit/', methods=['POST'])
@login_required
def post_submit():
    form = SubmitForm()
    languages = db.session.query(Language).order_by(Language.id).all()
    form.language_id.choices = [(l.id, l.name) for l in languages]
    if not form.validate():
        return render_template('submission/submit.html', form=form)
    problem = db.session.query(Problem).filter(Problem.id == form.problem_id.data).first()
    if not problem:
        flash('Cannot find the problem {}'.format(form.problem_id.data), 'danger')
        return render_template('submission/submit.html', form=form)

    submission = Submission(user_id=session['user_id'],
                            problem_id=form.problem_id.data,
                            language_id=form.language_id.data,
                            status=constants.SUBMISSION_PENDING,
                            code=form.code.data,
                            created_at=datetime.utcnow())
    db.session.add(submission)
    db.session.commit()
    return redirect(url_for('.get_status'))


@mod.route('/status/')
def get_status():
    # TODO: paginate
    # TODO: filter
    submissions = db.session.query(Submission).order_by(Submission.id.desc()).all()
    user_ids = [s.user_id for s in submissions]
    users = {u.id: u for u in db.session.query(User).filter(User.id.in_(user_ids))}
    languages = {l.id: l for l in db.session.query(Language)}
    return render_template('submission/status.html', submissions=submissions, users=users, languages=languages)

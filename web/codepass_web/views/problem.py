from .common import *

mod = Blueprint('problem', __name__)


@mod.route('/<int:problem_id>')
def get_problem(problem_id):
    while True:
        problem = db.session.query(Problem).filter(Problem.id == problem_id).first()
        if not problem or not problem.archive_id:
            break
        archive = db.session.query(ProblemArchive).filter(ProblemArchive.id == problem.archive_id).one()
        return render_template('problem/show.html', problem=problem, archive=archive)


@mod.route('/add')
@login_required
def get_add():
    form = FlaskForm()
    return render_template('problem/add.html', form=form)


def problem_form_to_dict(fields, form, path):
    d = {}
    for field in fields:
        key = field['key']
        if field['type'] == 'combo':
            d[key] = problem_form_to_dict(field['content'], form, path + key + '.')
        else:
            value = form.get(path + key, None)
            if value is not None:
                if field['type'] == 'int':
                    try:
                        d[key] = int(value)
                    except ValueError:
                        pass
                else:
                    d[key] = value
    return d


@mod.route('/save', methods=['POST'])
@login_required
def post_save():
    while True:
        form = FlaskForm()
        if not form.validate():
            break

        now = datetime.utcnow()
        user = db.session.query(User).filter(User.id == session['user_id']).one()

        config = problem_form_to_dict(current_app.config['WEB']['PROBLEM_FORMAT'], request.form, '')

        problem = Problem(is_public=False,
                          title=request.form.get('title', None),
                          author=request.form.get('author', None),
                          source=request.form.get('source', None),
                          updated_by=user.id,
                          updated_at=now,
                          created_by=user.id,
                          created_at=now)
        db.session.add(problem)
        db.session.commit()

        archive = ProblemArchive(problem_id=problem.id,
                                 json=config,
                                 created_by=user.id,
                                 created_at=now)
        db.session.add(archive)
        db.session.commit()

        problem.archive_id = archive.id
        db.session.commit()

        flash('The problem has been added.', 'success')
        return redirect(url_for('.get_problem', problem_id=problem.id))
    return render_template('problem/add.html', form=form)

import copy
import hashlib
import shutil
import subprocess
from .common import *

mod = Blueprint('problem', __name__)


def file_sha1(filename):
    with open(filename, 'rb') as f:
        sha1 = hashlib.sha1()
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def testcase_dir(sha1):
    return '{}/{}/{}/{}/{}'.format(sha1[0:2], sha1[2:4], sha1[4:6], sha1[6:8], sha1)


@mod.route('/<int:problem_id>')
def get_problem(problem_id):
    while True:
        problem = db.session.query(Problem).filter(Problem.id == problem_id).first()
        if not problem or not problem.archive_id:
            break
        archive = db.session.query(ProblemArchive).filter(ProblemArchive.id == problem.archive_id).one()
        return render_template('problem/show.html', problem=problem, archive=archive)
    abort(404)


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


@mod.route('/<int:problem_id>/upload')
@login_required
def get_upload(problem_id):
    problem = db.session.query(Problem).filter(Problem.id == problem_id).first()
    if not problem or not problem.archive_id:
        abort(404)
    archive = db.session.query(ProblemArchive).filter(ProblemArchive.id == problem.archive_id).one()
    form = FlaskForm()
    return render_template('problem/upload.html', form=form, problem=problem, archive=archive)


@mod.route('/<int:problem_id>/upload', methods=['POST'])
@login_required
def post_upload(problem_id):
    form = FlaskForm()
    assert form.validate()
    problem = db.session.query(Problem).filter(Problem.id == problem_id).first()
    if not problem or not problem.archive_id:
        abort(404)

    file = request.files.get('file', None)
    if not file or not file.filename:
        flash('No file uploaded', 'danger')
        return redirect(url_for('.get_upload', problem_id=problem_id))
    filename = secure_filename(file.filename)
    base, ext = os.path.splitext(filename)
    filepath = os.path.join(current_app.config['TMP_UPLOAD_DIR'], random_string(32)) + ext
    dirname = os.path.join(current_app.config['TMP_UPLOAD_DIR'], random_string(32))
    dst = os.path.join(dirname, base)
    file.save(filepath)

    os.makedirs(dst, exist_ok=True)
    p = subprocess.run(['unzip', '-o', '-d', dst, filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(filepath):
        os.unlink(filepath)
    if p.returncode:
        shutil.rmtree(dirname, ignore_errors=True)
        msg = 'Failed to extract the archive. <pre>STDOUT:\n{}\nSTDERR:\n{}</pre>'.format(
            str(p.stdout, 'utf-8'), str(p.stderr, 'utf-8'))
        flash(msg, 'danger')
        return redirect(url_for('.get_upload', problem_id=problem_id))

    if 'upload_testcase' not in session:
        session['upload_testcase'] = {}
    key = random_string(32)
    session['upload_testcase'][key] = {'problem_id': problem_id, 'dirname': dirname, 'filename': filename}
    flash('Successfully uploaded.', 'success')
    return redirect(url_for('.get_select_files'))


@mod.route('/select_files')
@login_required
def get_select_files():
    uploads = []
    if 'upload_testcase' in session:
        for key, upload in session['upload_testcase'].items():
            problem_id = upload['problem_id']
            dirname = upload['dirname']
            l = len(dirname) + 1
            files = [os.path.join(root[l:], file) for root, dir, files in os.walk(dirname) for file in files]
            files.sort()
            problem = db.session.query(Problem).filter(Problem.id == problem_id).one()
            uploads.append({'problem': problem, 'files': files, 'key': key, 'filename': upload['filename']})
    form = FlaskForm()
    return render_template('problem/select_files.html', uploads=uploads, form=form)


@mod.route('/select_files/<key>', methods=['POST'])
@login_required
def post_select_files(key):
    form = FlaskForm()
    assert form.validate()
    uploads = session.get('upload_testcase', None)
    if not uploads or key not in uploads:
        flash('Cannot find the uploaded files.', 'danger')
        return redirect(url_for('homepage.homepage'))

    problem_id = uploads[key]['problem_id']
    dirname = uploads[key]['dirname']
    problem = db.session.query(Problem).filter(Problem.id == problem_id).one()
    archive = db.session.query(ProblemArchive).filter(ProblemArchive.id == problem.archive_id).one()
    db.make_transient(archive)
    archive.id = None
    if 'files' not in archive.json:
        archive.json['files'] = {}

    for filename, checkbox in request.form.items():
        if checkbox != 'on':
            continue
        src_path = os.path.join(dirname, filename)
        if not os.path.exists(src_path):
            continue
        sha1 = file_sha1(src_path)
        dst_path = os.path.join(current_app.config['TESTCASES_DIR'], testcase_dir(sha1))
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        os.rename(src_path, dst_path)
        archive.json['files'][filename] = dict(
            sha1=sha1,
            updated_at=datetime.utcnow().timestamp()
        )

    db.session.add(archive)
    db.session.commit()
    problem.archive_id = archive.id
    db.session.add(problem)
    db.session.commit()

    shutil.rmtree(dirname, ignore_errors=True)
    del uploads[key]
    flash('Successfully added files.', 'success')
    return redirect(url_for('.get_edit_testcases', problem_id=problem_id))


@mod.route('/<int:problem_id>/modify_files', methods=['POST'])
@login_required
def post_modify_files(problem_id):
    form = FlaskForm()
    assert form.validate()
    problem = db.session.query(Problem).filter(Problem.id == problem_id).first()
    if not problem or not problem.archive_id:
        abort(404)
    archive = db.session.query(ProblemArchive).filter(ProblemArchive.id == problem.archive_id).one()
    db.make_transient(archive)
    archive.id = None

    new_files = archive.json['files']
    old_files = copy.copy(new_files)
    for name, value in request.form.items():
        if not name.startswith('rename-'):
            continue
        old_name = name[len('rename-'):]
        if old_name not in old_files:
            flash('There is no file called <code>{}</code>.'.format(old_name), 'danger')
            return redirect(url_for('.get_edit_testcases', problem_id=problem_id))
        del new_files[old_name]
        new_files[value] = old_files[old_name]
    for name, value in request.form.items():
        if not name.startswith('delete-'):
            continue
        new_name = name[len('delete-'):]
        if new_name not in new_files:
            flash('There is no file called <code>{}</code>.'.format(new_name), 'danger')
            return redirect(url_for('.get_edit_testcases', problem_id=problem_id))
        del new_files[new_name]

    db.session.add(archive)
    db.session.commit()
    problem.archive_id = archive.id
    db.session.add(problem)
    db.session.commit()

    flash('Successfully updated files.', 'success')
    return redirect(url_for('.get_edit_testcases', problem_id=problem_id))


def testcase_config_do_line(cols, files):
    if len(cols) <= 0:
        return {'err': 'Standard Input is missing.'}
    stdin = cols[0].strip()
    if stdin not in files:
        return {'err': 'There is no file named <code>{}</code>.'.format(stdin)}

    if len(cols) <= 1:
        return {'err': 'Standard Output is missing.'}
    stdout = cols[1].strip()
    if stdout not in files:
        return {'err': 'There is no file named <code>{}</code>.'.format(stdout)}

    if len(cols) <= 2:
        return {'err': 'Time Limit (ms) is missing.'}
    time = cols[2].strip()
    try:
        time = int(time)
    except ValueError:
        return {'err': '<code>{}</code> is not an integer.'.format(time)}

    if len(cols) <= 3:
        return {'err': 'Memory Limit (MB) is missing.'}
    mem = cols[3].strip()
    try:
        mem = int(mem)
    except ValueError:
        return {'err': '<code>{}</code> is not an integer.'.format(mem)}

    if len(cols) <= 4:
        return {'err': 'Score is missing.'}
    score = cols[4].strip()
    try:
        score = int(score)
    except ValueError:
        return {'err': '<code>{}</code> is not an integer.'.format(score)}

    return {'res': dict(stdin=stdin, stdout=stdout, time=time, mem=mem, score=score)}


@mod.route('/<int:problem_id>/testcase_config', methods=['POST'])
@login_required
def post_testcase_config(problem_id):
    form = FlaskForm()
    assert form.validate()
    problem = db.session.query(Problem).filter(Problem.id == problem_id).first()
    if not problem or not problem.archive_id:
        abort(404)

    archive = db.session.query(ProblemArchive).filter(ProblemArchive.id == problem.archive_id).one()
    db.make_transient(archive)
    archive.id = None

    config = []
    for i, line in enumerate(request.form.get('config', '').splitlines(), start=1):
        ret = testcase_config_do_line(line.split('|'), archive.json['files'])
        if 'err' in ret:
            flash('Line {}: {}'.format(i, ret['err']), 'danger')
            return redirect(url_for('.get_edit_testcases', problem_id=problem_id))
        config.append(ret['res'])
    archive.json['testcases'] = config

    db.session.add(archive)
    db.session.commit()
    problem.archive_id = archive.id
    db.session.add(problem)
    db.session.commit()

    flash('Successfully updated testcases.', 'success')
    return redirect(url_for('.get_edit_testcases', problem_id=problem_id))


@mod.route('/<int:problem_id>/testcases')
@login_required
def get_edit_testcases(problem_id):
    problem = db.session.query(Problem).filter(Problem.id == problem_id).first()
    if not problem or not problem.archive_id:
        abort(404)
    archive = db.session.query(ProblemArchive).filter(ProblemArchive.id == problem.archive_id).one()

    config = ''
    if 'testcases' in archive.json:
        for testcase in archive.json['testcases']:
            config += '{t[stdin]}|{t[stdout]}|{t[time]}|{t[mem]}|{t[score]}\n'.format(t=testcase)

    form = FlaskForm()
    return render_template('problem/testcases.html', form=form, problem=problem, archive=archive, config=config)

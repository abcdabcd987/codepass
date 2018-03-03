from .common import *

mod = Blueprint('admin', __name__)


class LanguageForm(FlaskForm):
    name = StringField('Name', [InputRequired('This field is required.')])
    time_scale = FloatField('Time Scale', [InputRequired('This field is required.')])
    source_filename = StringField('Source Filename')
    compile_command = TextAreaField('Compile Command')
    execute_command = TextAreaField('Execute Command')
    version_command = TextAreaField('Version Command')


@mod.route('/language/add')
@login_required
def get_language_add():
    form = LanguageForm()
    return render_template('admin/language_add.html', form=form)


@mod.route('/language/add', methods=['POST'])
@login_required
def post_language_add():
    form = LanguageForm()
    if not form.validate():
        return render_template('admin/language_add.html', form=form)
    language = Language(name=form.name.data,
                        time_scale=form.time_scale.data,
                        source_filename=form.source_filename.data,
                        compile_command=form.compile_command.data,
                        execute_command=form.execute_command.data,
                        version_command=form.version_command.data,
                        updated_at=datetime.utcnow())
    db.session.add(language)
    db.session.commit()
    flash('Successfully added the language.', 'success')
    return redirect(url_for('homepage.get_homepage'))

import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class JSONEncodedDict(db.TypeDecorator):
    impl = db.Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)


class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.Integer, primary_key=True)
    archive_id = db.Column(db.Integer, db.ForeignKey('problem_archives.id'))
    is_public = db.Column(db.Boolean, nullable=False, index=True)
    title = db.Column(db.String, index=True)  # cache
    author = db.Column(db.String, index=True)  # cache
    source = db.Column(db.String, index=True)  # cache
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # cache
    updated_at = db.Column(db.TIMESTAMP, nullable=False)  # cache
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False)


class ProblemArchive(db.Model):
    __tablename__ = 'problem_archives'
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False, index=True)
    json = db.Column(JSONEncodedDict)
    checker_id = db.Column(db.Integer, db.ForeignKey('checkers.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)


class Testcase(db.Model):
    __tablename__ = 'testcases'
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False, index=True)
    time_limit = db.Column(db.Integer, nullable=False)
    memory_limit = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)


class Checker(db.Model):
    __tablename__ = 'checkers'
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.Integer, db.ForeignKey('languages.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)


class Language(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    time_limit_multiplier = db.Column(db.Float, nullable=False)
    source_filename = db.Column(db.String)
    executable_filename = db.Column(db.String)
    compile_command = db.Column(db.String)
    execute_command = db.Column(db.String)
    checker_compile_command = db.Column(db.String)
    checker_execute_command = db.Column(db.String)
    version_command = db.Column(db.String)
    version = db.Column(db.Text)
    updated_at = db.Column(db.TIMESTAMP, nullable=False)


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False, index=True)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'), nullable=False, index=True)
    status = db.Column(db.Integer, nullable=False, index=True)
    code = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    dispatched_to = db.Column(db.String)  # judger name
    dispatched_at = db.Column(db.TIMESTAMP)
    compile_info = db.Column(db.Text)
    result = db.Column(JSONEncodedDict)
    # [{'testcase_id', 'time', 'memory', 'exitcode', 'verdict', 'checker_info', 'text'}, ...]
    completed_at = db.Column(db.TIMESTAMP)

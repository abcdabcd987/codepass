from flask import Flask
from flask_wtf.csrf import CSRFProtect
from .models import db
from .settings import Settings
from . import views


def create_app(config=None):
    app = Flask('codepass_web')

    app.config.from_object(Settings)
    app.config['TEMPLATES_AUTO_RELOAD'] = bool(app.debug)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = bool(app.debug)
    app.jinja_env.auto_reload = bool(app.debug)
    app.config.update(config or {})

    db.init_app(app)
    csrf = CSRFProtect(app)

    app.register_blueprint(views.homepage)
    app.register_blueprint(views.user, url_prefix='/user')

    @app.cli.command()
    def initdb():
        db.create_all()

    return app

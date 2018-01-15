import os
import tempfile
import pytest
from codepass_web.models import db
from codepass_web.factory import create_app


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
                      'TESTING': True,})

    with app.app_context():
        db.create_all()
        yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


def test_title(client):
    rv = client.get('/')
    assert b'Online Judge' in rv.data

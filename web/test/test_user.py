from codepass_web import constants


def register(client, username, password, confirm):
    return client.post('/user/register', data=dict(
        username=username,
        password=password,
        confirm=confirm,
    ), follow_redirects=True)


def login(client, username, password):
    return client.post('/user/login', data=dict(
        username=username,
        password=password,
    ), follow_redirects=True)


def logout(client):
    return client.get('/user/logout', follow_redirects=True)


def test_get_register(client):
    rv = client.get('/user/register')
    assert rv.status_code == 200


def test_register(client):
    rv = register(client, 'user1', 'pass1', '')
    assert constants.TextInputRequired in rv.get_data(as_text=True)

    rv = register(client, 'user1', '', 'pass1')
    assert constants.TextInputRequired in rv.get_data(as_text=True)

    rv = register(client, 'user1', 'pass1', 'pass2')
    assert constants.TextPasswordMismatch in rv.get_data(as_text=True)

    rv = register(client, 'user1', 'pass1', 'pass1')
    assert constants.TextUserRegisterSuccess in rv.get_data(as_text=True)


def test_register_disallows_for_logged_in_users(client):
    rv = register(client, 'user1', 'pass1', 'pass1')
    assert constants.TextUserRegisterSuccess in rv.get_data(as_text=True)

    rv = register(client, 'user2', 'pass2', 'pass2')
    assert constants.TextUserAlreadyLoggedIn in rv.get_data(as_text=True)


def test_register_enforces_unique_username(client):
    rv = register(client, 'user1', 'pass1', 'pass1')
    assert constants.TextUserRegisterSuccess in rv.get_data(as_text=True)

    rv = logout(client)
    assert constants.TextUserLogout in rv.get_data(as_text=True)

    rv = register(client, 'user1', 'pass2', 'pass2')
    assert constants.TextUserUsernameOccupied in rv.get_data(as_text=True)


def test_get_login(client):
    rv = client.get('/user/login')
    assert rv.status_code == 200

    rv = client.post('/user/login')
    assert rv.status_code == 200


def test_login(client):
    rv = register(client, 'user1', 'pass1', 'pass1')
    assert constants.TextUserRegisterSuccess in rv.get_data(as_text=True)

    rv = logout(client)
    assert constants.TextUserLogout in rv.get_data(as_text=True)

    rv = login(client, 'user1', 'wrongpassword')
    assert constants.TextUserWrongPassword in rv.get_data(as_text=True)

    rv = login(client, 'wronguser', 'pass1')
    assert constants.TextUserWrongPassword in rv.get_data(as_text=True)

    rv = login(client, 'user1', 'pass1')
    assert constants.TextUserLoginSuccess in rv.get_data(as_text=True)

    rv = login(client, 'user1', 'pass1')
    assert constants.TextUserAlreadyLoggedIn in rv.get_data(as_text=True)

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
    assert 'This field is required.' in rv.get_data(as_text=True)

    rv = register(client, 'user1', '', 'pass1')
    assert 'This field is required.' in rv.get_data(as_text=True)

    rv = register(client, 'user1', 'pass1', 'pass2')
    assert 'Passwords must match.' in rv.get_data(as_text=True)

    rv = register(client, 'user1', 'pass1', 'pass1')
    assert 'Successfully registered.' in rv.get_data(as_text=True)


def test_register_disallows_for_logged_in_users(client):
    rv = register(client, 'user1', 'pass1', 'pass1')
    assert 'Successfully registered.' in rv.get_data(as_text=True)

    rv = register(client, 'user2', 'pass2', 'pass2')
    assert 'You have already logged in.' in rv.get_data(as_text=True)


def test_register_enforces_unique_username(client):
    rv = register(client, 'user1', 'pass1', 'pass1')
    assert 'Successfully registered.' in rv.get_data(as_text=True)

    rv = logout(client)
    assert 'You have logged out.' in rv.get_data(as_text=True)

    rv = register(client, 'user1', 'pass2', 'pass2')
    assert 'The username has been occupied. Please try another one.' in rv.get_data(as_text=True)


def test_get_login(client):
    rv = client.get('/user/login')
    assert rv.status_code == 200

    rv = client.post('/user/login')
    assert rv.status_code == 200


def test_login(client):
    rv = register(client, 'user1', 'pass1', 'pass1')
    assert 'Successfully registered.' in rv.get_data(as_text=True)

    rv = logout(client)
    assert 'You have logged out.' in rv.get_data(as_text=True)

    rv = login(client, 'user1', 'wrongpassword')
    assert 'Incorrect combination of username and password.' in rv.get_data(as_text=True)

    rv = login(client, 'wronguser', 'pass1')
    assert 'Incorrect combination of username and password.' in rv.get_data(as_text=True)

    rv = login(client, 'user1', 'pass1')
    assert 'Successfully logged in.' in rv.get_data(as_text=True)

    rv = login(client, 'user1', 'pass1')
    assert 'You have already logged in.' in rv.get_data(as_text=True)

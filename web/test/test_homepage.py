def test_title(app, client):
    rv = client.get('/')
    assert bytes(app.config['WEBSITE_NAME'], 'utf-8') in rv.data

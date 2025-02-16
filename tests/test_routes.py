from app import create_app

# Test for JWKS endpoint
def test_jwks_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get('/.well-known/jwks.json')
    assert response.status_code == 200
    assert 'keys' in response.get_json() 


# Test the /auth endpoint for valid JWT 
def test_auth_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.post('/auth', json={"username": "user"})
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data


# Test the /auth?expired=true endpoint for expired JWT
def test_auth_expired_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.post('/auth?expired=true', json={"username": "user"})
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data


# Test invalid HTTP methods (POST, PUT, DELETE, PATCH) on JWKS endpoint
def test_invalid_methods_jwks():
    app = create_app()
    client = app.test_client()
    for method in ['post', 'put', 'delete', 'patch']:
        response = getattr(client, method)('/.well-known/jwks.json')
        assert response.status_code == 405



# Test invalid HTTP methods (GET, PUT, DELETE, PATCH, HEAD) on /auth endpoint
def test_invalid_methods_auth():
    app = create_app()
    client = app.test_client()
    for method in ['get', 'put', 'delete', 'patch', 'head']:
        response = getattr(client, method)('/auth')
        assert response.status_code == 405

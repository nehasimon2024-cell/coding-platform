from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_greet_with_name():
    response = client.get('/greet?name=Alice')
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome, Alice!"}

def test_greet_default():
    response = client.get('/greet')
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome, Guest!"}
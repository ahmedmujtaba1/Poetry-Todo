from fastapi.testclient import TestClient
from fastapi_helloworld import app 

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_create_user():
    response = client.post("/users/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code in (200, 201)

def test_login():
    response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    token = response.json()["access_token"]
    assert token

def test_create_todo():
    # Obtain a token first
    login_response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Now create a to-do item
    response = client.post("/todos/", json={"title": "Test Todo", "description": "Test Description"}, headers=headers)
    assert response.status_code in (200, 201)
    assert response.json()["title"] == "Test Todo"

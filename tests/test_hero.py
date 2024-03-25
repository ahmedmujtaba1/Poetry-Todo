from fastapi.testclient import TestClient
from hero_api.main import app

def test_root_path():
    client : TestClient = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

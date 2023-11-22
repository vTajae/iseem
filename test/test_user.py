from fastapi.testclient import TestClient
from app.main import app  # Import the FastAPI app object

client = TestClient(app)

def test_read_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == {"message": "Here is the list of users"}
    
# Execute with
# pytest
import pytest
from fastapi.testclient import TestClient
# Import your FastAPI app object. 
# If your main file is app/main.py, the import is:
from app.main import app 

@pytest.fixture
def client():
    """
    This fixture creates a TestClient that our tests can use 
    to send requests to the FastAPI app.
    """
    return TestClient(app)
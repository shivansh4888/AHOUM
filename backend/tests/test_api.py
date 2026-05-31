from fastapi.testclient import TestClient
from app.main import app
def test_health(): assert TestClient(app).get('/health').json()['status']=='ok'
def test_facets(): assert isinstance(TestClient(app).get('/api/facets').json(),list)

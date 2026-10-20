import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets/templates/backend"))
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_health():
    assert client.get('/healthz').json() == {'status': 'ok'}

def test_forecast():
    result = client.post('/v1/forecasts', json={'history':[1,2,3], 'horizon':2})
    assert result.status_code == 200
    assert result.json()['forecast'] == [2,2]

def test_route():
    result = client.post('/v1/routes/optimize', json={'distance_matrix':[[0,2,4],[2,0,1],[4,1,0]]})
    assert result.status_code == 200
    assert result.json()['total_distance_units'] == 7

def test_bad_matrix():
    result = client.post('/v1/routes/optimize', json={'distance_matrix':[[0,2],[2]]})
    assert result.status_code == 422

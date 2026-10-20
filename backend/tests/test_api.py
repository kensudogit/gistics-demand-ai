from datetime import date

from fastapi.testclient import TestClient

from app.demo_data import AS_OF, demand_history, weather_forecasts
from app.forecast import precip_for_day, series_until
from app.main import app
from app.routing import optimize_cvrptw

client = TestClient(app)


def test_health():
    assert client.get("/healthz").json() == {"status": "ok"}


def test_forecast_template_history():
    result = client.post("/v1/forecasts", json={"history": [1, 2, 3], "horizon": 2})
    assert result.status_code == 200
    assert result.json()["forecast"] == [2.0, 2.0]


def test_forecast_sku_site_no_future_leak():
    as_of = AS_OF
    result = client.post(
        "/v1/forecasts",
        json={"sku_id": "SKU-A", "site_id": "WH-TYO", "horizon": 7, "as_of": as_of.isoformat()},
    )
    assert result.status_code == 200
    body = result.json()
    assert body["as_of"] == as_of.isoformat()
    assert len(body["forecast"]) == 7
    assert body["forecast"][0]["demand_date"] > as_of.isoformat()
    points = series_until(
        demand_history(as_of), sku_id="SKU-A", site_id="WH-TYO", as_of=as_of
    )
    assert points[-1][0] == as_of


def test_weather_issued_after_as_of_ignored():
    as_of = date(2026, 10, 10)
    weather = weather_forecasts(AS_OF)
    used = precip_for_day(weather, site_id="WH-TYO", target=date(2026, 10, 19), as_of=as_of)
    assert used is None


def test_route_template_matrix():
    result = client.post(
        "/v1/routes/optimize",
        json={"distance_matrix": [[0, 2, 4], [2, 0, 1], [4, 1, 0]]},
    )
    assert result.status_code == 200
    body = result.json()
    assert body["feasible"] is True
    assert body["total_travel_minutes"] == 7
    assert body["production_ready"] is False


def test_bad_matrix():
    result = client.post("/v1/routes/optimize", json={"distance_matrix": [[0, 2], [2]]})
    assert result.status_code == 422


def test_cvrptw_infeasible_does_not_invent_route():
    matrix = [[0, 10, 10], [10, 0, 10], [10, 10, 0]]
    out = optimize_cvrptw(
        travel_time_matrix=matrix,
        demands=[0, 20, 20],
        vehicle_capacities=[15],
        time_windows=[[0, 1000], [0, 1000], [0, 1000]],
        service_times=[0, 0, 0],
        depot_index=0,
    )
    assert out["feasible"] is False
    assert out["unassigned"]
    routed = {n for v in out["vehicles"] for n in v["route"]}
    for item in out["unassigned"]:
        assert item["node"] not in routed or item["node"] == 0


def test_time_window_respected_or_unassigned():
    matrix = [[0, 50, 50], [50, 0, 50], [50, 50, 0]]
    out = optimize_cvrptw(
        travel_time_matrix=matrix,
        demands=[0, 1, 1],
        vehicle_capacities=[10],
        time_windows=[[0, 10], [0, 10], [0, 10]],
        service_times=[0, 0, 0],
        depot_index=0,
    )
    assert out["feasible"] is False
    for veh in out["vehicles"]:
        if len(veh["route"]) > 2:
            assert veh["feasible"] is True


def test_demo_route_and_job():
    routed = client.post("/v1/routes/optimize", json={"use_demo": True})
    assert routed.status_code == 200
    body = routed.json()
    assert "great-circle" in body["distance_note"]
    job = client.post("/v1/jobs", json={"kind": "route_optimize"})
    assert job.status_code == 202
    job_id = job.json()["job_id"]
    got = client.get(f"/v1/jobs/{job_id}")
    assert got.status_code == 200
    assert got.json()["status"] == "succeeded"


def test_meta_not_production():
    meta = client.get("/v1/meta").json()
    assert meta["production_ready"] is False

"""Local logistics + demand API. Auth, BigQuery, and road APIs are out of scope."""

from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.demo_data import AS_OF, demand_history, route_instance, weather_forecasts
from app.forecast import forecast_sku_site, last_k_mean, rolling_origin_backtest, series_until
from app.jobs import complete_job, create_job, get_job
from app.routing import optimize_cvrptw
from app.schemas import ForecastRequest, JobRequest, RouteRequest

app = FastAPI(title="Logistics Demand AI", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3070", "http://localhost:3070"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.get("/v1/meta")
def meta():
    return {
        "production_ready": False,
        "assumptions": "docs/10-assumptions.md",
        "forecast": "SKU×site×day, horizon 7, weekday median + weather issued_at<=as_of",
        "routing": "CVRPTW. travel matrix is not road distance. infeasible returns unassigned",
        "open_ids": [f"OPEN-{i:02d}" for i in range(1, 13)],
    }


@app.post("/v1/forecasts")
def forecast(req: ForecastRequest):
    as_of = date.fromisoformat(req.as_of) if req.as_of else AS_OF
    if req.history is not None:
        avg = last_k_mean([(as_of, x) for x in req.history], req.horizon)
        return {
            "forecast": avg,
            "method": "last_7_mean_demo",
            "unit": "input_units",
            "note": "raw history path keeps skill template compatibility",
        }
    try:
        return forecast_sku_site(
            demand_history(as_of),
            weather_forecasts(as_of),
            sku_id=req.sku_id,
            site_id=req.site_id,
            as_of=as_of,
            horizon=req.horizon,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/forecasts/backtest")
def backtest(req: ForecastRequest):
    as_of = date.fromisoformat(req.as_of) if req.as_of else AS_OF
    points = series_until(
        demand_history(as_of),
        sku_id=req.sku_id,
        site_id=req.site_id,
        as_of=as_of,
    )
    return rolling_origin_backtest(points, horizon=req.horizon)


@app.post("/v1/routes/optimize")
def optimize(req: RouteRequest):
    if req.use_demo or not (req.travel_time_matrix or req.distance_matrix):
        demo = route_instance()
        result = optimize_cvrptw(
            demo["travel_time_matrix"],
            demo["demands"],
            demo["vehicle_capacities"],
            demo["time_windows"],
            demo["service_times"],
            demo["depot_index"],
        )
        result["stops"] = [s["stop_id"] for s in demo["stops"]]
        result["distance_note"] = demo["distance_note"]
        return result

    matrix_src = req.travel_time_matrix or req.distance_matrix or []
    matrix = [[int(v) for v in row] for row in matrix_src]
    n = len(matrix)
    demands = req.demands if req.demands is not None else [0] + [1] * (n - 1)
    caps = req.vehicle_capacities or [sum(demands) or 1]
    tw = req.time_windows or [[0, 10_000] for _ in range(n)]
    service = req.service_times or [0] * n
    if len(demands) != n:
        demands = (demands + [0] * n)[:n]
        demands[req.depot_index] = 0
    try:
        result = optimize_cvrptw(matrix, demands, caps, tw, service, req.depot_index)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if req.distance_matrix is not None and req.travel_time_matrix is None:
        result["distance_note"] = (
            "distance_matrix accepted as travel_time units for template compatibility; not road-km"
        )
    return result


@app.post("/v1/jobs", status_code=202)
def enqueue(req: JobRequest):
    job = create_job(req.kind, req.payload)
    if req.kind == "route_optimize":
        demo = route_instance()
        complete_job(
            job["job_id"],
            optimize_cvrptw(
                demo["travel_time_matrix"],
                demo["demands"],
                demo["vehicle_capacities"],
                demo["time_windows"],
                demo["service_times"],
                demo["depot_index"],
            ),
        )
    return get_job(job["job_id"])


@app.get("/v1/jobs/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job

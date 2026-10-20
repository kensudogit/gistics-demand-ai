"""Synthetic SKU×site demand, weather, and a small CVRPTW instance.

Not production data. Travel times are great-circle × 1.3 at 30 km/h, not roads.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from typing import Any

AS_OF = date(2026, 10, 19)
HISTORY_DAYS = 84
SITES = ("WH-TYO", "WH-OSA")
SKUS = ("SKU-A", "SKU-B")

# Rough depot / stop coordinates (lon, lat). Stop ids only — no addresses.
STOPS = [
    {"stop_id": "DEPOT", "lon": 139.767, "lat": 35.681, "demand": 0, "tw": (0, 720), "service": 0},
    {"stop_id": "S-01", "lon": 139.810, "lat": 35.710, "demand": 8, "tw": (60, 360), "service": 12},
    {"stop_id": "S-02", "lon": 139.700, "lat": 35.650, "demand": 12, "tw": (90, 420), "service": 12},
    {"stop_id": "S-03", "lon": 139.850, "lat": 35.640, "demand": 10, "tw": (120, 480), "service": 10},
    {"stop_id": "S-04", "lon": 139.620, "lat": 35.700, "demand": 6, "tw": (60, 300), "service": 8},
    {"stop_id": "S-05", "lon": 139.780, "lat": 35.620, "demand": 9, "tw": (150, 540), "service": 10},
]

VEHICLES = [
    {"vehicle_id": "V-1", "capacity": 30},
    {"vehicle_id": "V-2", "capacity": 30},
]


def _haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def synthetic_travel_time_matrix_min() -> list[list[int]]:
    """Minutes. Circuity 1.3, 30 km/h. NOT road distance, NOT traffic."""
    n = len(STOPS)
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            km = _haversine_km(STOPS[i]["lon"], STOPS[i]["lat"], STOPS[j]["lon"], STOPS[j]["lat"])
            minutes = max(1, round(km * 1.3 / 30.0 * 60.0))
            matrix[i][j] = int(minutes)
    return matrix


def _base_demand(sku: str, site: str, d: date) -> float:
    weekday = d.weekday()  # Mon=0
    if sku == "SKU-A":
        weekly = (18, 20, 19, 21, 22, 11, 8)[weekday]
        site_k = 1.0 if site == "WH-TYO" else 0.72
    else:
        weekly = (9, 10, 10, 11, 12, 16, 15)[weekday]
        site_k = 0.9 if site == "WH-TYO" else 1.15
    wave = 1.0 + 0.08 * math.sin((d.timetuple().tm_yday / 365) * 2 * math.pi)
    return weekly * site_k * wave


def demand_history(as_of: date = AS_OF) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = as_of - timedelta(days=HISTORY_DAYS - 1)
    for offset in range(HISTORY_DAYS):
        d = start + timedelta(days=offset)
        rain = 12.0 if d.weekday() == 2 else (0.0 if d.weekday() < 5 else 3.0)
        for site in SITES:
            for sku in SKUS:
                qty = _base_demand(sku, site, d)
                if rain >= 10:
                    qty *= 0.9
                rows.append(
                    {
                        "demand_date": d.isoformat(),
                        "site_id": site,
                        "sku_id": sku,
                        "demand_units": round(qty, 3),
                    }
                )
    return rows


def weather_forecasts(as_of: date = AS_OF) -> list[dict[str, Any]]:
    """Issued the previous afternoon. Horizon includes future days."""
    rows: list[dict[str, Any]] = []
    start = as_of - timedelta(days=HISTORY_DAYS - 1)
    for offset in range(HISTORY_DAYS + 7):
        valid = start + timedelta(days=offset)
        issued = datetime(valid.year, valid.month, valid.day, 15, 0, tzinfo=timezone.utc) - timedelta(days=1)
        precip = 12.0 if valid.weekday() == 2 else (0.0 if valid.weekday() < 5 else 3.0)
        for site in SITES:
            rows.append(
                {
                    "location_id": site,
                    "forecast_issued_at": issued.isoformat(),
                    "valid_at": valid.isoformat(),
                    "temperature": 18.0,
                    "precipitation": precip,
                }
            )
    return rows


def route_instance() -> dict[str, Any]:
    matrix = synthetic_travel_time_matrix_min()
    return {
        "distance_note": "travel_time_matrix is synthetic minutes (great-circle × 1.3 at 30 km/h), not road distance",
        "depot_index": 0,
        "stops": STOPS,
        "vehicles": VEHICLES,
        "travel_time_matrix": matrix,
        "demands": [s["demand"] for s in STOPS],
        "time_windows": [list(s["tw"]) for s in STOPS],
        "service_times": [s["service"] for s in STOPS],
        "vehicle_capacities": [v["capacity"] for v in VEHICLES],
    }

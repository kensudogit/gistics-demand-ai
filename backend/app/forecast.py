"""Time-series baselines with as_of cutoff. No future actuals in features."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from statistics import median
from typing import Any


def _parse_date(value: str | date) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value)[:10])


def _parse_dt(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def series_until(
    history: list[dict[str, Any]],
    *,
    sku_id: str,
    site_id: str,
    as_of: date,
) -> list[tuple[date, float]]:
    rows: list[tuple[date, float]] = []
    for row in history:
        if row["sku_id"] != sku_id or row["site_id"] != site_id:
            continue
        d = _parse_date(row["demand_date"])
        if d <= as_of:
            rows.append((d, float(row["demand_units"])))
    rows.sort(key=lambda x: x[0])
    return rows


def precip_for_day(
    weather: list[dict[str, Any]],
    *,
    site_id: str,
    target: date,
    as_of: date,
) -> float | None:
    """Use only forecasts issued on or before as_of (end of that calendar day UTC)."""
    cutoff = datetime(as_of.year, as_of.month, as_of.day, 23, 59, 59)
    chosen: tuple[datetime, float] | None = None
    for row in weather:
        if row["location_id"] != site_id:
            continue
        valid = _parse_date(row["valid_at"])
        if valid != target:
            continue
        issued = _parse_dt(row["forecast_issued_at"]).replace(tzinfo=None)
        if issued > cutoff:
            continue
        if chosen is None or issued >= chosen[0]:
            chosen = (issued, float(row["precipitation"]))
    return None if chosen is None else chosen[1]


def last_k_mean(points: list[tuple[date, float]], horizon: int, k: int = 7) -> list[float]:
    window = points[-k:] if points else []
    avg = sum(v for _, v in window) / len(window) if window else 0.0
    return [round(avg, 3)] * horizon


def weekday_median(points: list[tuple[date, float]], horizon: int, as_of: date) -> list[float]:
    by_wd: dict[int, list[float]] = defaultdict(list)
    for d, v in points:
        by_wd[d.weekday()].append(v)
    out: list[float] = []
    for i in range(1, horizon + 1):
        wd = (as_of + timedelta(days=i)).weekday()
        vals = by_wd.get(wd) or [p[1] for p in points] or [0.0]
        out.append(round(float(median(vals)), 3))
    return out


def seasonal_naive(points: list[tuple[date, float]], horizon: int, as_of: date) -> list[float]:
    lookup = {d: v for d, v in points}
    out: list[float] = []
    for i in range(1, horizon + 1):
        target = as_of + timedelta(days=i)
        prev = lookup.get(target - timedelta(days=7))
        if prev is None and points:
            prev = points[-1][1]
        out.append(round(float(prev or 0.0), 3))
    return out


def apply_weather(preds: list[float], rains: list[float | None]) -> list[float]:
    adjusted: list[float] = []
    for y, rain in zip(preds, rains):
        factor = 0.9 if rain is not None and rain >= 10 else 1.0
        adjusted.append(round(y * factor, 3))
    return adjusted


def _wape(actual: list[float], pred: list[float]) -> float:
    denom = sum(abs(a) for a in actual)
    if denom <= 0:
        return 0.0
    return sum(abs(a - p) for a, p in zip(actual, pred)) / denom


def rolling_origin_backtest(
    points: list[tuple[date, float]],
    *,
    horizon: int = 7,
    origins: int = 8,
) -> dict[str, Any]:
    if len(points) < horizon + 14:
        return {"origins": 0, "mae": None, "wape": None, "bias": None, "note": "not_enough_history"}
    last_origin_idx = len(points) - horizon - 1
    first_origin_idx = max(14, last_origin_idx - origins + 1)
    abs_err = 0.0
    err = 0.0
    actual_sum = 0.0
    n = 0
    used = 0
    for idx in range(first_origin_idx, last_origin_idx + 1):
        origin = points[idx][0]
        train = points[: idx + 1]
        actuals = [points[idx + h][1] for h in range(1, horizon + 1)]
        pred = weekday_median(train, horizon, origin)
        abs_err += sum(abs(a - p) for a, p in zip(actuals, pred))
        err += sum(p - a for a, p in zip(actuals, pred))
        actual_sum += sum(abs(a) for a in actuals)
        n += horizon
        used += 1
    return {
        "origins": used,
        "horizon": horizon,
        "mae": round(abs_err / n, 3) if n else None,
        "wape": round(abs_err / actual_sum, 4) if actual_sum else None,
        "bias": round(err / n, 3) if n else None,
        "method": "weekday_median",
        "note": "demo_series_only_not_production_accuracy",
    }


def forecast_sku_site(
    history: list[dict[str, Any]],
    weather: list[dict[str, Any]],
    *,
    sku_id: str,
    site_id: str,
    as_of: date,
    horizon: int = 7,
) -> dict[str, Any]:
    points = series_until(history, sku_id=sku_id, site_id=site_id, as_of=as_of)
    if not points:
        raise ValueError("no history on or before as_of")
    rains = [
        precip_for_day(weather, site_id=site_id, target=as_of + timedelta(days=i), as_of=as_of)
        for i in range(1, horizon + 1)
    ]
    candidates = {
        "last_7_mean": last_k_mean(points, horizon),
        "weekday_median": weekday_median(points, horizon, as_of),
        "seasonal_naive": seasonal_naive(points, horizon, as_of),
    }
    bt = rolling_origin_backtest(points, horizon=horizon)
    method = "weekday_median"
    preds = apply_weather(candidates[method], rains)
    dates = [(as_of + timedelta(days=i)).isoformat() for i in range(1, horizon + 1)]
    return {
        "sku_id": sku_id,
        "site_id": site_id,
        "as_of": as_of.isoformat(),
        "horizon": horizon,
        "method": method,
        "weather_rule": "precip>=10mm (issued_at<=as_of) scales demand by 0.9",
        "unit": "units_per_day",
        "forecast": [
            {
                "demand_date": d,
                "yhat": y,
                "precipitation_forecast": rains[i],
            }
            for i, (d, y) in enumerate(zip(dates, preds))
        ],
        "candidates": {k: v for k, v in candidates.items()},
        "backtest": bt,
        "history_points": len(points),
        "leakage_guard": "features use demand_date<=as_of and weather forecast_issued_at<=as_of",
    }

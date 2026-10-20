"""教育用API。認証・永続化・実道路経路・学習モデルは別途実装。"""
from itertools import permutations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Logistics Demand AI demo", version="0.1.0")


class ForecastRequest(BaseModel):
    history: list[float] = Field(min_length=1, max_length=365)
    horizon: int = Field(default=7, ge=1, le=30)


class RouteRequest(BaseModel):
    distance_matrix: list[list[float]] = Field(min_length=2, max_length=9)
    depot_index: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def check_matrix(self):
        n = len(self.distance_matrix)
        if self.depot_index >= n or any(len(row) != n for row in self.distance_matrix):
            raise ValueError("matrix must be square and depot_index in range")
        for i, row in enumerate(self.distance_matrix):
            for j, value in enumerate(row):
                if value < 0 or value != value or value == float("inf"):
                    raise ValueError("distances must be finite and nonnegative")
                if i == j and value != 0:
                    raise ValueError("diagonal must be zero")
        return self


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/v1/forecasts")
def forecast(req: ForecastRequest):
    # 教育用ベースライン: 最近7件の平均。実運用では時系列検証が必要。
    avg = sum(req.history[-7:]) / len(req.history[-7:])
    return {"forecast": [round(avg, 3)] * req.horizon,
            "method": "last_7_mean_demo", "unit": "input_units"}


@app.post("/v1/routes/optimize")
def optimize(req: RouteRequest):
    # 小規模TSP全探索: 9地点以下のみ。道路距離や時間窓/容量は考慮しない。
    n, depot = len(req.distance_matrix), req.depot_index
    others = [i for i in range(n) if i != depot]
    best_route, best_cost = None, float("inf")
    for order in permutations(others):
        path = [depot, *order, depot]
        cost = sum(req.distance_matrix[a][b] for a, b in zip(path, path[1:]))
        if cost < best_cost:
            best_route, best_cost = path, cost
    if best_route is None:
        raise HTTPException(status_code=422, detail="No feasible route")
    return {"route": best_route, "total_distance_units": best_cost,
            "method": "bruteforce_tsp_demo", "production_ready": False}

from pydantic import BaseModel, Field, model_validator


class ForecastRequest(BaseModel):
    sku_id: str = Field(default="SKU-A")
    site_id: str = Field(default="WH-TYO")
    horizon: int = Field(default=7, ge=1, le=30)
    as_of: str | None = None
    history: list[float] | None = Field(default=None, max_length=365)


class RouteRequest(BaseModel):
    travel_time_matrix: list[list[int]] | None = None
    distance_matrix: list[list[float]] | None = None
    depot_index: int = Field(default=0, ge=0)
    demands: list[int] | None = None
    vehicle_capacities: list[int] | None = None
    time_windows: list[list[int]] | None = None
    service_times: list[int] | None = None
    use_demo: bool = False

    @model_validator(mode="after")
    def check_matrix(self):
        matrix = self.travel_time_matrix or self.distance_matrix
        if self.use_demo:
            return self
        if not matrix:
            raise ValueError("travel_time_matrix required unless use_demo")
        n = len(matrix)
        if n < 2 or n > 20:
            raise ValueError("matrix size must be 2..20")
        if self.depot_index >= n or any(len(row) != n for row in matrix):
            raise ValueError("matrix must be square and depot_index in range")
        return self


class JobRequest(BaseModel):
    kind: str = Field(default="route_optimize")
    payload: dict = Field(default_factory=dict)

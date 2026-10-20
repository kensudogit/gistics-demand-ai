"""Capacitated VRP with time windows. Never invent a feasible optimum."""

from __future__ import annotations

from typing import Any

try:
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2

    HAS_ORTOOLS = True
except ImportError:  # pragma: no cover
    HAS_ORTOOLS = False


def _simulate(route: list[int], travel: list[list[int]], service: list[int], tw: list[list[int]]) -> tuple[bool, int, str]:
    time = tw[route[0]][0] if route else 0
    for a, b in zip(route, route[1:]):
        time += travel[a][b]
        earliest, latest = tw[b]
        if time < earliest:
            time = earliest
        if time > latest:
            return False, time, f"time_window_missed:{b}"
        time += service[b]
    cost = sum(travel[a][b] for a, b in zip(route, route[1:]))
    return True, cost, "ok"


def _insertion(
    travel: list[list[int]],
    demands: list[int],
    capacities: list[int],
    tw: list[list[int]],
    service: list[int],
    depot: int,
) -> dict[str, Any]:
    n = len(travel)
    remaining = [i for i in range(n) if i != depot]
    routes = [[depot, depot] for _ in capacities]
    loads = [0] * len(capacities)
    unassigned: list[dict[str, Any]] = []

    while remaining:
        best: tuple[int, int, int, int] | None = None  # stop, veh, pos, delta
        reasons: dict[int, str] = {}
        for stop in remaining:
            placed = False
            for v, cap in enumerate(capacities):
                if loads[v] + demands[stop] > cap:
                    reasons[stop] = reasons.get(stop) or "capacity"
                    continue
                route = routes[v]
                for pos in range(1, len(route)):
                    trial = route[:pos] + [stop] + route[pos:]
                    ok, cost, why = _simulate(trial, travel, service, tw)
                    if not ok:
                        reasons[stop] = why
                        continue
                    pred, succ = route[pos - 1], route[pos]
                    delta = travel[pred][stop] + travel[stop][succ] - travel[pred][succ]
                    if best is None or delta < best[3]:
                        best = (stop, v, pos, delta)
                    placed = True
            if not placed and stop not in reasons:
                reasons[stop] = "no_feasible_insertion"
        if best is None:
            for stop in list(remaining):
                unassigned.append({"node": stop, "reason": reasons.get(stop, "infeasible")})
                remaining.remove(stop)
            break
        stop, v, pos, _ = best
        routes[v] = routes[v][:pos] + [stop] + routes[v][pos:]
        loads[v] += demands[stop]
        remaining.remove(stop)

    vehicles = []
    total = 0
    for v, route in enumerate(routes):
        ok, cost, why = _simulate(route, travel, service, tw)
        load = sum(demands[i] for i in route if i != depot)
        vehicles.append(
            {
                "vehicle_index": v,
                "route": route,
                "load": load,
                "capacity": capacities[v],
                "travel_minutes": cost if ok else None,
                "feasible": ok,
                "detail": why,
            }
        )
        if ok:
            total += cost
    return {
        "vehicles": vehicles,
        "unassigned": unassigned,
        "total_travel_minutes": total,
        "feasible": not unassigned and all(x["feasible"] for x in vehicles),
        "method": "cheapest_insertion_cvrptw",
    }


def _ortools(
    travel: list[list[int]],
    demands: list[int],
    capacities: list[int],
    tw: list[list[int]],
    service: list[int],
    depot: int,
) -> dict[str, Any] | None:
    if not HAS_ORTOOLS:
        return None
    n = len(travel)
    num_vehicles = len(capacities)
    manager = pywrapcp.RoutingIndexManager(n, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)
    horizon = max(end for _, end in (tuple(w) for w in tw)) + max(service) + 1

    def time_cb(from_index: int, to_index: int) -> int:
        i = manager.IndexToNode(from_index)
        j = manager.IndexToNode(to_index)
        return int(travel[i][j] + service[i])

    transit = routing.RegisterTransitCallback(time_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(transit)
    routing.AddDimension(transit, horizon, horizon, False, "Time")
    time_dim = routing.GetDimensionOrDie("Time")
    for node, window in enumerate(tw):
        index = manager.NodeToIndex(node)
        time_dim.CumulVar(index).SetRange(int(window[0]), int(window[1]))
    for v in range(num_vehicles):
        start = routing.Start(v)
        end = routing.End(v)
        time_dim.CumulVar(start).SetRange(int(tw[depot][0]), int(tw[depot][1]))
        time_dim.CumulVar(end).SetRange(int(tw[depot][0]), int(tw[depot][1]))

    def demand_cb(from_index: int) -> int:
        return int(demands[manager.IndexToNode(from_index)])

    demand_idx = routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(demand_idx, 0, capacities, True, "Capacity")

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromSeconds(2)
    solution = routing.SolveWithParameters(params)
    if solution is None:
        return None

    vehicles = []
    total = 0
    used: set[int] = {depot}
    for v in range(num_vehicles):
        index = routing.Start(v)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            used.add(node)
            index = solution.Value(routing.NextVar(index))
        route.append(depot)
        ok, cost, why = _simulate(route, travel, service, tw)
        load = sum(demands[i] for i in route if i != depot)
        vehicles.append(
            {
                "vehicle_index": v,
                "route": route,
                "load": load,
                "capacity": capacities[v],
                "travel_minutes": cost if ok else None,
                "feasible": ok,
                "detail": why,
            }
        )
        if ok:
            total += cost
    unassigned = [{"node": i, "reason": "not_routed"} for i in range(n) if i not in used]
    return {
        "vehicles": vehicles,
        "unassigned": unassigned,
        "total_travel_minutes": total,
        "feasible": not unassigned and all(x["feasible"] for x in vehicles),
        "method": "ortools_cvrptw",
    }


def optimize_cvrptw(
    travel_time_matrix: list[list[int]],
    demands: list[int],
    vehicle_capacities: list[int],
    time_windows: list[list[int]],
    service_times: list[int],
    depot_index: int = 0,
) -> dict[str, Any]:
    n = len(travel_time_matrix)
    if any(len(row) != n for row in travel_time_matrix):
        raise ValueError("travel_time_matrix must be square")
    if not (len(demands) == len(time_windows) == len(service_times) == n):
        raise ValueError("demands, time_windows, service_times must match matrix size")
    if depot_index < 0 or depot_index >= n:
        raise ValueError("depot_index out of range")
    if demands[depot_index] != 0:
        raise ValueError("depot demand must be 0")
    for i, row in enumerate(travel_time_matrix):
        for j, value in enumerate(row):
            if value < 0:
                raise ValueError("travel times must be nonnegative")
            if i == j and value != 0:
                raise ValueError("diagonal must be zero")

    solved = _ortools(
        travel_time_matrix, demands, vehicle_capacities, time_windows, service_times, depot_index
    )
    if solved is None:
        solved = _insertion(
            travel_time_matrix, demands, vehicle_capacities, time_windows, service_times, depot_index
        )
    solved["production_ready"] = False
    solved["matrix_meaning"] = "travel_time_minutes_as_provided_not_road_distance"
    if not solved["feasible"]:
        solved["message"] = "no feasible CVRPTW covering all stops; unassigned lists reasons"
    else:
        solved["message"] = "feasible solution under capacity and time windows"
    return solved

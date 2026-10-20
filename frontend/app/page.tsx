"use client";

import { useEffect, useMemo, useState } from "react";

type ForecastRow = {
  demand_date: string;
  yhat: number;
  precipitation_forecast: number | null;
};
type ForecastResp = {
  sku_id: string;
  site_id: string;
  method: string;
  forecast: ForecastRow[];
  backtest: { wape: number | null; mae: number | null; note: string; origins: number };
  leakage_guard: string;
};
type RouteResp = {
  feasible: boolean;
  method: string;
  total_travel_minutes: number;
  distance_note: string;
  message: string;
  stops?: string[];
  vehicles: {
    vehicle_index: number;
    route: number[];
    load: number;
    capacity: number;
    travel_minutes: number | null;
    feasible: boolean;
  }[];
  unassigned: { node: number; reason: string }[];
};

export default function Home() {
  const [sku, setSku] = useState("SKU-A");
  const [site, setSite] = useState("WH-TYO");
  const [forecast, setForecast] = useState<ForecastResp | null>(null);
  const [route, setRoute] = useState<RouteResp | null>(null);
  const [busy, setBusy] = useState<string>("");
  const [error, setError] = useState("");

  async function loadForecast() {
    setBusy("forecast");
    setError("");
    try {
      const res = await fetch("/v1/forecasts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sku_id: sku, site_id: site, horizon: 7 }),
      });
      if (!res.ok) throw new Error(`forecast ${res.status}`);
      setForecast(await res.json());
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy("");
    }
  }

  async function loadRoute() {
    setBusy("route");
    setError("");
    try {
      const res = await fetch("/v1/routes/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ use_demo: true }),
      });
      if (!res.ok) throw new Error(`route ${res.status}`);
      setRoute(await res.json());
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy("");
    }
  }

  useEffect(() => {
    loadForecast();
    loadRoute();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const maxY = useMemo(
    () => Math.max(1, ...(forecast?.forecast.map((r) => r.yhat) ?? [1])),
    [forecast]
  );

  function stopLabel(idx: number) {
    return route?.stops?.[idx] ?? String(idx);
  }

  return (
    <main>
      <h1>物流・需要予測 AI（デモ）</h1>
      <p className="sub">
        真の需要も道路距離も出しません。SKU×拠点の 7 日予測は時系列ベースライン、ルートは容量と時間窓を満たすときだけ実行可能とします。精度・コストは未計測です。
      </p>
      {error ? <p className="bad">{error}</p> : null}

      <div className="grid">
        <section className="panel">
          <h2>需要予測</h2>
          <label>SKU</label>
          <select value={sku} onChange={(e) => setSku(e.target.value)}>
            <option>SKU-A</option>
            <option>SKU-B</option>
          </select>
          <label>拠点</label>
          <select value={site} onChange={(e) => setSite(e.target.value)}>
            <option>WH-TYO</option>
            <option>WH-OSA</option>
          </select>
          <button disabled={busy === "forecast"} onClick={loadForecast}>
            7日先を予測
          </button>
          {forecast ? (
            <>
              <div className="kpi">
                <span>手法 {forecast.method}</span>
                <span>
                  デモ WAPE {forecast.backtest.wape ?? "—"} / MAE {forecast.backtest.mae ?? "—"}
                </span>
                <span>origin {forecast.backtest.origins}</span>
              </div>
              <div className="bars">
                {forecast.forecast.map((row) => (
                  <i
                    key={row.demand_date}
                    title={`${row.demand_date}: ${row.yhat}`}
                    style={{ height: `${(row.yhat / maxY) * 100}%` }}
                  />
                ))}
              </div>
              <table>
                <thead>
                  <tr>
                    <th>日</th>
                    <th>yhat</th>
                    <th>予報降水</th>
                  </tr>
                </thead>
                <tbody>
                  {forecast.forecast.map((row) => (
                    <tr key={row.demand_date}>
                      <td>{row.demand_date}</td>
                      <td>{row.yhat}</td>
                      <td>{row.precipitation_forecast ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="note">{forecast.leakage_guard}。WAPE は合成系列の backtest であり本番精度ではありません。</p>
            </>
          ) : null}
        </section>

        <section className="panel">
          <h2>配送ルート（容量・時間窓）</h2>
          <button disabled={busy === "route"} onClick={loadRoute}>
            デモ便を最適化
          </button>
          {route ? (
            <>
              <div className="kpi">
                <span className={route.feasible ? "ok" : "bad"}>
                  {route.feasible ? "実行可能" : "未割当あり"}
                </span>
                <span>{route.method}</span>
                <span>合計 {route.total_travel_minutes} 分</span>
              </div>
              {route.vehicles.map((v) => (
                <p key={v.vehicle_index} className="route">
                  車 {v.vehicle_index + 1} 積載 {v.load}/{v.capacity} ：{" "}
                  {v.route.map(stopLabel).join(" → ")}
                </p>
              ))}
              {route.unassigned.length ? (
                <ul className="bad">
                  {route.unassigned.map((u) => (
                    <li key={u.node}>
                      {stopLabel(u.node)}: {u.reason}
                    </li>
                  ))}
                </ul>
              ) : null}
              <p className="note">{route.distance_note}</p>
              <p className="note">{route.message}</p>
            </>
          ) : null}
        </section>
      </div>
    </main>
  );
}

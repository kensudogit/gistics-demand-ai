# データ契約

時刻は UTC で保存する。業務日は `Asia/Tokyo` から導出する。

## 注文 / 需要

| 列 | 型 | 意味 |
|---|---|---|
| event_id | string | 一意 |
| order_id | string | 注文 |
| sku_id | string | SKU |
| site_id | string | 拠点 |
| ordered_at | timestamp UTC | イベント時刻 |
| quantity | int | 数量 |
| status | string | completed のみ需要に加算 |
| ingested_at | timestamp UTC | 取込時刻 |

日次 mart: `demand_date, site_id, sku_id, demand_units`。パーティションは event_date。

## 気象（リーク防止）

| 列 | 意味 |
|---|---|
| location_id | 拠点に対応 |
| forecast_issued_at | 予報発表。`as_of` より後なら使わない |
| valid_at | 対象日 |
| temperature / precipitation | 予報値 |

## 配送

| 列 | 意味 |
|---|---|
| stop_id | 停留。住所は持たない |
| demand_units | 車両容量と比較 |
| time_window_start / end | 分（デポ出発基準） |
| travel_time_matrix | 分。道路距離と名乗らない |

## 品質

一意キー、null 率、遅延到着の冪等 MERGE。再処理はバッチ ID。デモ実装はメモリシードで代替し、BigQuery は `sql/bigquery_daily_demand.sql` のみ。

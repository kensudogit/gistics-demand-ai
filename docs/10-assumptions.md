# 未確定事項（OPEN）

Skill 手順1。AWS/GCP アカウント未指定のため仮定。実データ学習・本番デプロイはしていない。精度・レイテンシ・コストは未計測。

| ID | 項目 | 仮定 |
|---|---|---|
| OPEN-01 | クラウド | ローカルデモ。GCP（Cloud Run + BigQuery）を既定設計、AWS は代替。デプロイ未実施 |
| OPEN-02 | リージョン | asia-northeast1 |
| OPEN-03 | 予測粒度 | SKU × 拠点 × 日。ホライズン 7 日 |
| OPEN-04 | 需要 | 合成時系列。欠品バイアス・販促実績は未接続 |
| OPEN-05 | 気象 | 合成。`forecast_issued_at <= as_of` の予報のみ使用 |
| OPEN-06 | 交通 | 呼び出し側の travel_time_matrix。デモは大圏×1.3 / 30km/h。**道路距離でも渋滞でもない** |
| OPEN-07 | 配送 | 1 デポ、車両 2、容量と時間窓あり。休憩・複数デポ・勤務上限は未実装 |
| OPEN-08 | 認証 | ローカルは無し。Cloud Run は `--no-allow-unauthenticated` をテンプレに残す |
| OPEN-09 | PII | 住所・氏名は持たない。停留は stop_id と概略座標 |
| OPEN-10 | SLA | p95 目標未設定。未計測 |
| OPEN-11 | 予算 | 未設定。BigQuery スキャン課金は未発生 |
| OPEN-12 | 非同期 | `/v1/jobs` はメモリ上。Cloud Run Jobs 未接続 |

未実施: 実測 WAPE、道路 API、本番 IAM、復元訓練、apply/deploy。

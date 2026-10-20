# 構成（仮定 OPEN-01〜12）

```text
Browser (Next.js :3070)
  → FastAPI (:8070)
      ├─ POST /v1/forecasts          時系列ベースライン（リークなし）
      ├─ POST /v1/forecasts/backtest rolling-origin（デモ系列）
      ├─ POST /v1/routes/optimize    CVRP + 時間窓。不能なら未割当を返す
      ├─ POST /v1/jobs  / GET /v1/jobs/{id}
      └─ GET  /healthz  /v1/meta
          → 合成需要・気象（local）
          → travel_time_matrix（呼び出し元。道路APIではない）
```

GCP 既定（未デプロイ）:

Cloud Storage / Pub/Sub → Cloud Run Jobs → BigQuery（raw/staging/marts）
→ Cloud Run（FastAPI）→ Next.js
重い最適化・再学習は HTTP 同期に載せない。

AWS 代替: S3 + EventBridge + ECS/Lambda、Redshift/Athena、Secrets Manager。

依存: データ契約（時刻 UTC、as_of カット）→ 予測 → ルート制約。予測値を道路時間と混ぜない。

脅威の扱い:

- 秘密鍵を Git に置かない
- PII は最小。デモは stop_id
- 実行不能なルートを「最適」と返さない
- 将来実績を特徴量に入れない

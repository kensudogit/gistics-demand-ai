# logistics-demand-ai

Skill `logistics-demand-ai` の実行成果です。**GCP/AWS へはデプロイしていません。精度・レイテンシ・コストは未計測です。**

SKU×拠点の日次需要を 7 日先まで、時系列ベースラインで予測します。配送は車両容量と時間窓付き CVRPTW です。実行不能なら未割当と理由を返し、架空の最適解は出しません。移動時間は呼び出し側の行列です。デモ行列は大圏×1.3 / 30km/h で、**道路距離ではありません**。

仮定は [`docs/10-assumptions.md`](docs/10-assumptions.md)。構成は [`docs/architecture.md`](docs/architecture.md)。データ契約は [`docs/data-contracts.md`](docs/data-contracts.md)。Skill 本体は [`logistics-demand-ai/SKILL.md`](logistics-demand-ai/SKILL.md)。

## 起動

```powershell
cd C:\devlop\logistics-demand-ai\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8070
```

別ターミナル:

```powershell
cd C:\devlop\logistics-demand-ai\frontend
npm install
npm run dev
```

| URL | 用途 |
|---|---|
| http://127.0.0.1:3070/ | ダッシュボード |
| http://127.0.0.1:8070/docs | OpenAPI |
| http://127.0.0.1:8070/healthz | ヘルス |

API だけなら `docker compose up --build`（ポート 8070）。

## 検証

```powershell
cd C:\devlop\logistics-demand-ai
python logistics-demand-ai\scripts\validate_skill.py
cd backend
pytest -q
```

`apply` / `gcloud run deploy` は承認後に手動です。テンプレは [`infra/deploy-cloud-run.sh`](infra/deploy-cloud-run.sh)（未実行）。

## API

| Method | Path | 意味 |
|---|---|---|
| GET | `/healthz` | 生存確認 |
| GET | `/v1/meta` | 仮定と production_ready=false |
| POST | `/v1/forecasts` | SKU×拠点の 7 日予測。`history` だけなら旧デモ平均 |
| POST | `/v1/forecasts/backtest` | rolling-origin（合成系列） |
| POST | `/v1/routes/optimize` | CVRPTW。`use_demo` または travel_time_matrix |
| POST | `/v1/jobs` | 202。メモリ上。Cloud Run Jobs ではない |
| GET | `/v1/jobs/{id}` | ジョブ状態 |

## 残課題（OPEN）

- BigQuery 接続と実注文 ETL
- 道路・交通 API の時間行列
- 認証、IAM、複数デポ、休憩
- 実測 WAPE / p95 / スキャン課金
- Cloud Run Jobs への長い最適化の切り出し
# gistics-demand-ai

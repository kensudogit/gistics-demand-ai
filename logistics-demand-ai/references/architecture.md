# アーキテクチャ

## GCP推奨
- 取り込み: Cloud Storage → Pub/Sub / Cloud Run Jobs → BigQuery（生データ/整形/特徴量マート）
- オーケストレーション: Cloud Scheduler + Workflows（必要なら Dataform）
- 学習/推論: Cloud Run Jobs / Vertex AI（規模次第）、オンラインAPI: Cloud Run + FastAPI
- UI: Next.js on Cloud Run または Firebase Hosting 等
- モデル/成果物: Cloud Storage、Secret Manager、Cloud Logging/Monitoring
- セキュリティ: IAM最小権限、サービスアカウント分離、Cloud Run認証、必要に応じVPC/Cloud Armor
- 大量データ: BigQueryパーティション・クラスタリング、増分MERGE、列選択、コスト上限/クエリ監視

## AWS代替
- 取り込み: S3 + EventBridge / SQS / Lambda / Step Functions
- 分析: Redshift Serverless または Athena + Glue Catalog（要件に応じ選択）
- 学習: SageMaker / ECS Tasks、オンラインAPI: Lambda+API Gateway または ECS Fargate
- UI: Amplify Hosting / ECS、監視: CloudWatch、機密: Secrets Manager

## API境界
`/v1/forecasts`（推論）、`/v1/routes/optimize`（経路）、`/v1/jobs/{id}`（非同期ジョブ）、`/healthz`。
重い最適化・再学習はジョブに切り出し、202 + job_id、状態取得、再試行/取消を実装。

## デプロイ
開発/検証/本番を別プロジェクト・アカウントとし、IaC（Terraform等）で管理。認証・シークレット・ネットワーク・監視をコード化する。

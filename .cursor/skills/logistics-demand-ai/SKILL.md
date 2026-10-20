---
name: logistics-demand-ai
description: >
  物流・EC向け配送ルート最適化、需要予測AI、配送ログ・気象・交通データのETL/ELT、
  Python FastAPI推論REST API、React Next.js TypeScriptダッシュボード、
  Google Cloud Run・BigQuery または AWS Lambda/ECS・Redshift/S3 の
  サーバーレス基盤を設計・実装・テスト・改善するときに使う。
  Cursor/Copilot/Claude Code等のAIコーディング支援を安全に活用する開発規約も含む。
---

# Logistics & Demand Forecast AI Skill

## 利用する場面
- 配送ログ・注文・在庫・気象・交通を統合する分析基盤の開発
- 需要予測モデルの学習・評価・推論 API の開発
- 車両容量・時間枠を考慮した配送ルート最適化
- FastAPI + Next.js/React/TypeScript + BigQuery + Cloud Run の構築
- AWSへの代替配置、性能・コスト最適化、CI/CD、運用監視

## 実行手順（必ず順番に確認）
1. `references/requirements.md` に従い業務要件、予測粒度、予測期間、配送制約、SLA、クラウド、データ権限を確定。不明なら仮定を明記。
2. `references/architecture.md` を読み、GCPを既定、AWSを代替として構成図と責務分離を設計。
3. `references/data-contracts.md` に従い、時刻・単位・スキーマ・PII・欠損値・リーク防止を定義。
4. `references/ml-routing.md` に従い、時系列ベースライン→検証→高度モデル、ルート制約→実行可能性確認を行う。
5. `assets/templates/` を基にAPI・UI・SQL・IaCを生成し、単体・結合・性能テストを追加。
6. `references/security-operations.md` に従い認証、権限、監視、費用、障害復旧、AI補助開発レビューを実施。
7. 成果物として README、構成図、API契約、DB/DWH定義、テスト結果、未実装事項を必ず提示。

## 厳守事項
- 実測していない精度・レイテンシ・コストを達成済みと表現しない。
- 需要予測は時系列分割を使用。将来情報・実績確定後データを特徴量に混入させない。
- ルート最適化は直線距離を道路距離と偽らない。交通時間は信頼できる経路API/行列を使用。
- PII/秘密鍵/顧客ログをAI支援ツールに無許可で入力しない。
- APIは入力検証、エラー形式、認証・認可、冪等性、タイムアウトを設計。
- Cloud Runで長時間処理をHTTP同期実行しない。Cloud Run Jobs / Pub/Sub / Workflows等を検討。
- 生成コードは人間によるレビュー、テスト、依存関係スキャンを経て利用する。

## 実装例
`assets/templates/backend` は依存を最小化したFastAPIデモ。
`assets/templates/frontend` はNext.js UIの最小サンプル。
`assets/templates/sql` はBigQuery向け集計SQL。
`assets/templates/infra` はCloud Runデプロイ参考例（認証・本番設定は別途）。
`tests` は基本テスト。`scripts/validate_skill.py` で構成を検証する。

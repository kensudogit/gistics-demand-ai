# セキュリティ・運用・AIコーディング規約

- 認証: OIDC/JWTの署名・issuer・audience検証、テナント別認可、RBAC。
- REST: Pydantic検証、標準エラー形式、ページング、APIバージョン、レート制限、監査ログ。
- 秘密: Secret Manager/Secrets Manager。キーをGit/プロンプトに貼らない。
- 非同期: Cloud Run Jobs/Workflows、リトライ、DLQ、冪等キー、ジョブ状態。
- 可観測性: trace_id、構造化ログ、p95、エラー率、DWHスキャン量、推論ドリフト、最適化時間。
- 品質: pytest、ruff、mypy、Playwright、OpenAPI契約、負荷テスト、依存関係スキャン。
- Cursor/Copilot/Claude: 企業データ入力前に利用規約/社内ポリシー/学習設定を確認。実データは匿名化・最小化。生成コードはレビューし、ライセンス・脆弱性・テストを確認。
- 本番反映: PR承認、CI、IaC planレビュー、ロールバック、バックアップ/復元演習。

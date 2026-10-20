# logistics-demand-ai

Claude.ai / Claude Code で再利用する物流・需要予測AI開発Skillです。

## インストール
- Claude Code: フォルダ全体を `.claude/skills/logistics-demand-ai/` または `~/.claude/skills/logistics-demand-ai/` に配置。`/logistics-demand-ai` あるいは自然言語で呼び出す。
- Claude.ai: Skills機能を利用できる環境では ZIP をアップロードして有効化。利用可否やメニューは契約・UIによって異なります。

## 呼び出し例
「logistics-demand-ai Skillを使い、GCP Cloud Run + BigQueryで配送ログと気象データを統合し、SKU×拠点の日次需要を7日先まで予測するFastAPI APIとNext.js画面を作ってください。配送ルートは車両容量と配達時間枠を考慮してください。」

## 構成
- SKILL.md: Skill本体
- references/: 要件・アーキテクチャ・データ契約・ML/ルーティング・セキュリティ運用
- assets/templates/backend/: FastAPIデモ（需要予測ベースライン、距離行列ベースの経路サンプル）
- assets/templates/frontend/: Next.jsサンプル
- assets/templates/sql/: BigQuery SQL
- assets/templates/infra/: Cloud Run参考デプロイ
- scripts/validate_skill.py: ZIP内容検証
- tests/: APIの基本テスト

## APIデモ実行
```bash
cd assets/templates/backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
`http://127.0.0.1:8000/docs` で確認。ルートAPIは教育用の対称距離行列を入力する例で、実道路や時間枠制約には未対応です。

## 本番化前の必須作業
認証・認可、永続化、DWH連携、実データでのモデル学習、外部交通API、時間枠/容量付きVRP、監視、CI/CD、セキュリティ・性能検証を追加してください。サンプルは商用完成品ではありません。

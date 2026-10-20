# データ契約・パイプライン

- 時刻はUTC TIMESTAMPで保存、業務日付は店舗/配送先のタイムゾーンから導出。
- 注文イベント: event_id, order_id, sku_id, site_id, ordered_at, quantity, status, ingested_at。
- 配送ログ: shipment_id, vehicle_id, stop_id, planned_at, actual_at, status, latitude, longitude（PII管理）。
- 天気: location_id, forecast_issued_at, valid_at, temperature, precipitation。予測時点で利用可能だったforecast_issued_atのみ使用。
- 交通: segment_id, observed_at, travel_seconds, source, freshness。
- DWH層: raw（原本）→ staging（型・重複・欠損検証）→ marts（学習/BI用）。
- 品質: 一意キー、null率、更新遅延、異常値、件数照合、スキーマ互換性、重複排除。
- 再処理: バッチID/水位/チェックポイント、冪等MERGE、遅延到着イベントを考慮。
- BigQuery: event_dateでパーティション、site_id/sku_idでクラスタリングを検討。料金はスキャン量を測定。
- PII: 氏名・住所・精密位置情報は最小収集、用途限定、アクセス制御、暗号化、保持期限を設定。

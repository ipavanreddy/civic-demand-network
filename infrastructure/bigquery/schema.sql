-- JanVaani BigQuery tables (dataset: ${BIGQUERY_DATASET}, region asia-south1).
-- Written by services/api/app/integrations/bigquery_sink.py when USE_BIGQUERY=true.
-- Create in the existing dataset (tables only): grep -v "CREATE SCHEMA" infrastructure/bigquery/schema.sql | bq query --use_legacy_sql=false --location=asia-south1

CREATE SCHEMA IF NOT EXISTS civic_demand_network OPTIONS (location = 'asia-south1');

CREATE TABLE IF NOT EXISTS civic_demand_network.requests (
  request_id STRING NOT NULL, citizen_id STRING, channel STRING, language STRING,
  text_original STRING, text_en STRING, audio_url STRING, photo_url STRING,
  category STRING, sub_category STRING, summary_en STRING, urgency STRING, urgency_reason STRING,
  est_beneficiaries INT64, vulnerable_groups ARRAY<STRING>, seasonality STRING, sentiment FLOAT64,
  confidence FLOAT64, missing_information ARRAY<STRING>, state STRING, lgd_district STRING,
  lgd_block STRING, lgd_unit STRING, h3_cell STRING, resolution_method STRING,
  resolution_confidence FLOAT64, cluster_id STRING, status STRING, created_at TIMESTAMP,
  model_name STRING, model_version STRING, prompt_version STRING, is_synthetic BOOL
) PARTITION BY DATE(created_at) CLUSTER BY state, category;

CREATE TABLE IF NOT EXISTS civic_demand_network.request_cluster_assignments (
  request_id STRING, cluster_id STRING, assigned_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS civic_demand_network.recommendations (
  recommendation_id STRING, cluster_id STRING, priority_score FLOAT64, score_breakdown JSON,
  weights_used JSON, evidence_brief JSON, grounding JSON, generated_at TIMESTAMP, language STRING,
  model_name STRING, model_version STRING, prompt_version STRING, mode STRING, note STRING, scope JSON
);

CREATE TABLE IF NOT EXISTS civic_demand_network.weight_changes (
  `at` TIMESTAMP, officer STRING, reason STRING, `from` JSON, `to` JSON, scope STRING
);

CREATE TABLE IF NOT EXISTS civic_demand_network.decisions (
  recommendation_id STRING, decision STRING, officer STRING, note STRING, decided_at TIMESTAMP
);

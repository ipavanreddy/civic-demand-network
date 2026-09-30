export type Weights = {
  demand: number;
  infra_gap: number;
  vulnerability: number;
  trend: number;
  investment: number;
};

export type FactorScore = {
  factor: keyof Weights;
  label: string;
  raw: number | null;
  normalised: number;
  weight: number;
  contribution: number;
  explanation: string;
  sources: string[];
};

export type Decision = {
  recommendation_id: string;
  decision: "approve_for_field_verification" | "defer" | "reject";
  officer: string;
  note: string | null;
  decided_at: string;
};

export type RecommendationRow = {
  recommendation_id: string;
  cluster_id: string;
  rank: number;
  default_rank: number | null;
  priority_score: number;
  band: "High" | "Medium" | "Low";
  breakdown: FactorScore[];
  weights_used: Weights;
  title: string;
  category: string;
  category_label: string;
  sub_category: string | null;
  summary: string;
  state: string;
  state_name: string;
  district: string;
  block: string;
  places: string[];
  lat: number | null;
  lng: number | null;
  request_count: number;
  unique_citizens: number;
  population: number;
  status: string;
  is_synthetic: boolean;
  decision: Decision | null;
  has_brief: boolean;
};

export type Scope = { state: string | null; district: string | null; category: string | null; label: string };

export type Ranking = {
  scope: Scope;
  weights: Weights;
  default_weights: Weights;
  formula: string;
  as_of: string;
  items: RecommendationRow[];
};

export type IndicatorRow = {
  unit: string;
  lgd_code: string;
  indicator_name: string;
  value: number | boolean;
  year: number;
  geographic_level: string;
  source: string;
  definition: string | null;
  is_sample: boolean;
};

export type InvestmentRow = {
  project_id: string;
  scheme: string;
  title: string;
  status: string;
  sanctioned_amount_inr: number;
  start_date: string;
  population_covered: number;
  source: string;
  is_sample: boolean;
  covers_cluster_area: boolean;
};

export type EvidenceBrief = {
  title: string;
  summary: string;
  demand_evidence: string[];
  data_evidence: { claim: string; field: string; value: string; source: string; year: string }[];
  investment_context: string[];
  estimated_beneficiaries: number | null;
  beneficiaries_basis: string;
  uncertainties: string[];
  next_step: string;
  confidence: number;
};

export type BriefRecord = {
  recommendation_id: string;
  evidence_brief: EvidenceBrief;
  grounding: { ok: boolean; numbers_checked: number; ungrounded_numbers: string[] };
  generated_at: string;
  model_name: string;
  model_version: string;
  prompt_version: string;
  mode: "real" | "demo";
  note: string | null;
};

export type RecommendationDetail = RecommendationRow & {
  scope: Scope;
  total_in_scope: number;
  indicators: IndicatorRow[];
  investments: InvestmentRow[];
  quotes: { language: string; original: string; translated_en: string; is_synthetic: boolean }[];
  first_seen: string | null;
  last_seen: string | null;
  recent_requests_30d: number;
  brief: BriefRecord | null;
};

export type Analytics = {
  scope: Scope;
  requests: number;
  unique_citizens: number;
  clusters: number;
  top_categories: { category: string; label: string; requests: number }[];
  by_district: { code: string; name: string; state: string; requests: number }[];
  languages: Record<string, number>;
  channels: Record<string, number>;
  synthetic_share: number;
  freshness: {
    citizen_requests_last_received: string | null;
    last_live_request: string | null;
    scoring_as_of: string;
    indicator_years: number[];
  };
  investments_in_scope: number;
};

export type Hotspot = {
  h3_cell: string;
  lat: number;
  lng: number;
  boundary: [number, number][];
  request_count: number;
  unique_citizens: number;
  top_category: string;
  top_category_label: string;
  cluster_ids: string[];
  max_priority_score: number;
};

export type StateInfo = {
  state_code: string;
  name: string;
  name_local: string;
  languages: string[];
  default_language: string;
  focus_categories: string[];
  unit_level: string;
  level_labels: Record<string, string>;
  map_center: [number, number];
  districts: { code: string; name: string; blocks: string[] }[];
  units: number;
  indicators: number;
  investments: number;
  adapter_config: string;
};

export type Integration = { mode: "real" | "demo"; env: string; detail: string };
export type SystemStatus = {
  demo_mode: boolean;
  integrations: Record<string, Integration>;
  sample_data: boolean;
  synthetic_requests: number;
  live_requests: number;
  data_notice: string;
  dataset_version: string;
  gemini_model: string;
};

export type Taxonomy = { categories: { id: string; label: Record<string, string> }[] };

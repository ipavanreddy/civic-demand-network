export type SystemStatus = {
  demo_mode: boolean;
  live_count?: number;
  total_count?: number;
  /** real = live Google service · demo = not configured · fallback = configured but last call failed */
  integrations: Record<string, { mode: "real" | "demo" | "fallback"; env: string; detail: string }>;
  sample_data: boolean;
  synthetic_requests: number;
  live_requests: number;
  data_notice: string;
  dataset_version: string;
};

export type Scenario = {
  id: string;
  scenario: string;
  state: string;
  district: string | null;
  language: "en" | "hi" | "te";
  channel: string;
  text_original: string;
  text_en: string;
};

export type StateInfo = {
  state_code: string;
  name: string;
  name_local: string;
  default_language: string;
  districts: { code: string; name: string }[];
};

export type Taxonomy = { categories: { id: string; label: Record<string, string> }[] };

export type RequestView = {
  request: {
    request_id: string;
    language: string;
    text_original: string;
    text_en: string;
    category: string;
    sub_category: string | null;
    urgency: string;
    urgency_reason: string | null;
    vulnerable_groups: string[];
    missing_information: string[];
    confidence: number;
    est_beneficiaries: number | null;
    model_name: string;
    model_version: string;
    prompt_version: string;
    channel: string;
    audio_url: string | null;
  };
  status: string;
  status_label: string;
  provenance: { model_name: string; mode: "real" | "demo"; note: string | null; prompt_version: string } | null;
  translation: { text_en: string; mode: string; provider: string; note?: string } | null;
  speech: { transcript: string; mode: string; provider: string; note?: string } | null;
  location: {
    resolved: boolean;
    unit_name: string | null;
    block_name: string | null;
    district_name: string | null;
    lgd_unit: string | null;
    h3_cell: string | null;
    method: string;
    confidence: number;
    candidates: { lgd_code: string; label: string }[];
  } | null;
  needs_clarification: boolean;
  clarification_question: string | null;
  message: {
    language: string;
    text: string;
    speech?: { mode: "real" | "demo"; provider: string; audio_base64: string | null; mime: string | null };
  };
  cluster: {
    cluster_id: string;
    request_count: number;
    unique_citizens: number;
    status: string;
    summary: string;
    representative_quotes: string[];
    joined_existing?: boolean;
    similarity_method?: string;
  } | null;
  demo_mode: boolean;
  demo_components: string[];
};

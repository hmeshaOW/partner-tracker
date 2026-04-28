export type DomainCategory =
  | "Digital Assets"
  | "Private Capital"
  | "Technology & Modernization"
  | "Quantum Technologies"
  | "Data & AI"
  | "Other";

export interface InferredActivity {
  id: string;
  source: "email" | "meeting";
  title: string;
  contact: string;
  organization: string;
  client: string;
  domain: DomainCategory;
  summary: string;
  date: string;
  confidence: number;
  is_bff: boolean;
  is_external: boolean;
  bff_status: string;
  stage_hint: string;
  next_step: string;
  matched_opportunity_id?: string | null;
}

export interface OpportunityRecord {
  opportunity_id: string;
  client: string;
  cit?: string | null;
  opportunity_name: string;
  bff_status?: string | null;
  stage?: string | null;
  generating_partner?: string | null;
  hany_involvement_type?: string | null;
  hany_is_core_pursuit?: boolean | null;
  fees_value_usd?: number | null;
  probability?: number | null;
  industry_sector?: string | null;
  capability_teams?: string | null;
  estimated_start_date?: string | null;
  software_or_ai_involved?: string | null;
}

export interface OpportunitySummary {
  count: number;
  core_pursuits: number;
  total_fees_usd: number;
  weighted_fees_usd: number;
  by_stage: Record<string, number>;
}

export interface OpportunityListResponse {
  opportunities: OpportunityRecord[];
  summary: OpportunitySummary;
}

export interface WeeklyReportResponse {
  period_start: string;
  period_end: string;
  report_markdown: string;
  totals: {
    activities: number;
    external_activities: number;
    bff_activities: number;
  };
}

export interface SyncResponse {
  synced_items: number;
  inferred_activities: InferredActivity[];
}

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
  domain: DomainCategory;
  summary: string;
  date: string;
  confidence: number;
  is_bff: boolean;
  is_external: boolean;
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

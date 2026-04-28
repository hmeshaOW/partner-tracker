import type { SyncResponse, WeeklyReportResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {})
    },
    ...init
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export function healthCheck() {
  return api<{ status: string }>("/health");
}

export function syncMailboxAndCalendar(accessToken: string) {
  return api<SyncResponse>("/api/sync", {
    method: "POST",
    body: JSON.stringify({ access_token: accessToken })
  });
}

export function generateWeeklyReport(startDate: string, endDate: string) {
  return api<WeeklyReportResponse>("/api/reports/weekly", {
    method: "POST",
    body: JSON.stringify({
      period_start: startDate,
      period_end: endDate
    })
  });
}

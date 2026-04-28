import { useEffect, useMemo, useState } from "react";
import { generateWeeklyReport, getOpportunities, healthCheck, syncMailboxAndCalendar } from "./api";
import { hasMicrosoftLoginConfig, loginAndAcquireGraphToken } from "./auth";
import type { InferredActivity, OpportunityRecord, OpportunitySummary } from "./types";

function getWeekRange() {
  const now = new Date();
  const end = now.toISOString().slice(0, 10);
  const startDate = new Date(now);
  startDate.setDate(now.getDate() - 6);
  return {
    start: startDate.toISOString().slice(0, 10),
    end
  };
}

export default function App() {
  const [accessToken, setAccessToken] = useState("");
  const [accountName, setAccountName] = useState("");
  const [status, setStatus] = useState("idle");
  const [backendStatus, setBackendStatus] = useState("unknown");
  const [activities, setActivities] = useState<InferredActivity[]>([]);
  const [opportunities, setOpportunities] = useState<OpportunityRecord[]>([]);
  const [opportunitySummary, setOpportunitySummary] = useState<OpportunitySummary>({
    count: 0,
    core_pursuits: 0,
    total_fees_usd: 0,
    weighted_fees_usd: 0,
    by_stage: {}
  });
  const [report, setReport] = useState("");
  const [error, setError] = useState("");

  const week = useMemo(() => getWeekRange(), []);

  useEffect(() => {
    void checkBackend();
    void loadOpportunities();
  }, []);

  async function loadOpportunities() {
    try {
      const result = await getOpportunities();
      setOpportunities(result.opportunities);
      setOpportunitySummary(result.summary);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function checkBackend() {
    setError("");
    try {
      const result = await healthCheck();
      setBackendStatus(result.status);
    } catch (e) {
      setError((e as Error).message);
      setBackendStatus("down");
    }
  }

  async function handleSync() {
    setStatus("syncing");
    setError("");
    try {
      let token = accessToken;
      if (!token && hasMicrosoftLoginConfig()) {
        const login = await loginAndAcquireGraphToken();
        token = login.accessToken;
        setAccessToken(token);
        setAccountName(login.accountName);
      }

      if (!token) {
        throw new Error("Microsoft login configuration is required to acquire an access token at runtime.");
      }

      const result = await syncMailboxAndCalendar(token);
      setActivities(result.inferred_activities);
      setStatus("synced");
    } catch (e) {
      setError((e as Error).message);
      setStatus("error");
    }
  }

  async function handleReport() {
    setStatus("reporting");
    setError("");
    try {
      const result = await generateWeeklyReport(week.start, week.end);
      setReport(result.report_markdown);
      setStatus("ready");
    } catch (e) {
      setError((e as Error).message);
      setStatus("error");
    }
  }

  const topStageEntries = Object.entries(opportunitySummary.by_stage).sort((a, b) => b[1] - a[1]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>BD Command</h1>
        <p>Partner Tracker</p>
      </aside>
      <main className="main">
        <header className="hero">
          <h2>Business Development Dashboard</h2>
          <p>AI-assisted weekly non-billable activity intelligence for OW leadership reporting.</p>
          <div className="actions">
            <button onClick={checkBackend}>Check Backend</button>
            <button onClick={handleSync} disabled={status === "syncing"}>
              {status === "syncing" ? "Syncing..." : "Sync Email + Calendar"}
            </button>
            <button onClick={handleReport} disabled={activities.length === 0 || status === "reporting"}>
              {status === "reporting" ? "Generating..." : "Generate Weekly Report"}
            </button>
          </div>
          <div className="account-row">
            <span>{accountName ? `Signed in as ${accountName}` : "Sync will prompt Microsoft login at runtime."}</span>
          </div>
          <div className="status-row">
            <span>Backend: {backendStatus}</span>
            <span>State: {status}</span>
          </div>
          {error ? <div className="error">{error}</div> : null}
        </header>

        <section className="kpi-grid">
          <article className="kpi-card">
            <span className="kpi-label">Workbook Opportunities</span>
            <strong>{opportunitySummary.count}</strong>
          </article>
          <article className="kpi-card">
            <span className="kpi-label">Core Pursuits</span>
            <strong>{opportunitySummary.core_pursuits}</strong>
          </article>
          <article className="kpi-card">
            <span className="kpi-label">Fees USD</span>
            <strong>{currency(opportunitySummary.total_fees_usd)}</strong>
          </article>
          <article className="kpi-card">
            <span className="kpi-label">Weighted Fees</span>
            <strong>{currency(opportunitySummary.weighted_fees_usd)}</strong>
          </article>
        </section>

        <section className="two-column">
          <section className="panel">
            <h3>Opportunity Register</h3>
            <table>
              <thead>
                <tr>
                  <th>Client</th>
                  <th>Opportunity</th>
                  <th>Stage</th>
                  <th>BFF Status</th>
                  <th>Fees USD</th>
                </tr>
              </thead>
              <tbody>
                {opportunities.slice(0, 10).map((item) => (
                  <tr key={item.opportunity_id}>
                    <td>{item.client}</td>
                    <td>{item.opportunity_name}</td>
                    <td>{item.stage || ""}</td>
                    <td>{item.bff_status || ""}</td>
                    <td>{currency(item.fees_value_usd || 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="panel">
            <h3>Stage Mix</h3>
            <ul className="stage-list">
              {topStageEntries.map(([stage, count]) => (
                <li key={stage}>
                  <span>{stage}</span>
                  <strong>{count}</strong>
                </li>
              ))}
            </ul>
          </section>
        </section>

        <section className="panel">
          <h3>LLM-Extracted Log Entries</h3>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Source</th>
                <th>Client</th>
                <th>Contact</th>
                <th>Domain</th>
                <th>Stage Hint</th>
                <th>Summary</th>
              </tr>
            </thead>
            <tbody>
              {activities.map((item) => (
                <tr key={item.id}>
                  <td>{item.date}</td>
                  <td>{item.source}</td>
                  <td>{item.client}</td>
                  <td>{item.contact}</td>
                  <td>{item.domain}</td>
                  <td>{item.stage_hint}</td>
                  <td>{item.summary}<div className="subtle">{item.next_step}</div></td>
                </tr>
              ))}
              {activities.length === 0 ? (
                <tr>
                  <td colSpan={7}>No synced activities yet.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </section>

        <section className="panel report">
          <h3>Weekly Leadership Draft</h3>
          <pre>{report || "Generate a report to view weekly summary."}</pre>
        </section>
      </main>
    </div>
  );
}

function currency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: value >= 1_000_000 ? "compact" : "standard",
    maximumFractionDigits: 1,
  }).format(value);
}

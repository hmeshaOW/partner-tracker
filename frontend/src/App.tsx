import { useMemo, useState } from "react";
import { generateWeeklyReport, healthCheck, syncMailboxAndCalendar } from "./api";
import type { InferredActivity } from "./types";

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
  const [status, setStatus] = useState("idle");
  const [backendStatus, setBackendStatus] = useState("unknown");
  const [activities, setActivities] = useState<InferredActivity[]>([]);
  const [report, setReport] = useState("");
  const [error, setError] = useState("");

  const week = useMemo(() => getWeekRange(), []);

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
      const result = await syncMailboxAndCalendar(accessToken);
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
            <button onClick={handleSync} disabled={!accessToken || status === "syncing"}>
              {status === "syncing" ? "Syncing..." : "Sync Email + Calendar"}
            </button>
            <button onClick={handleReport} disabled={activities.length === 0 || status === "reporting"}>
              {status === "reporting" ? "Generating..." : "Generate Weekly Report"}
            </button>
          </div>
          <div className="token-row">
            <label htmlFor="token">Microsoft Graph Access Token</label>
            <input
              id="token"
              type="password"
              placeholder="Paste delegated Graph token"
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
            />
          </div>
          <div className="status-row">
            <span>Backend: {backendStatus}</span>
            <span>State: {status}</span>
          </div>
          {error ? <div className="error">{error}</div> : null}
        </header>

        <section className="panel">
          <h3>Inferred Activities</h3>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Source</th>
                <th>Contact</th>
                <th>Domain</th>
                <th>BFF / External</th>
                <th>Summary</th>
              </tr>
            </thead>
            <tbody>
              {activities.map((item) => (
                <tr key={item.id}>
                  <td>{item.date}</td>
                  <td>{item.source}</td>
                  <td>{item.contact}</td>
                  <td>{item.domain}</td>
                  <td>{item.is_bff ? "BFF" : ""}{item.is_bff && item.is_external ? " + " : ""}{item.is_external ? "External" : ""}</td>
                  <td>{item.summary}</td>
                </tr>
              ))}
              {activities.length === 0 ? (
                <tr>
                  <td colSpan={6}>No synced activities yet.</td>
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

/**
 * Frontend Service — Node.js + Express
 * Part of the AI-Based Self-Healing Framework for Containers
 */

const express = require("express");
const axios = require("axios");

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || "http://backend:5000";

app.use(express.json());

// ── Utility: call backend with timeout & error handling ─────────────
async function callBackend(path) {
  try {
    const res = await axios.get(BACKEND_URL + path, { timeout: 5000 });
    return { ok: true, data: res.data };
  } catch (err) {
    const msg = err.response
      ? "Backend returned " + err.response.status
      : err.code || err.message;
    console.error("[FRONTEND] Backend call failed (" + path + "): " + msg);
    return { ok: false, error: msg };
  }
}

// ── Build dashboard HTML ────────────────────────────────────────────
function buildDashboard(statusInfo, eventList) {
  var backendClass = statusInfo.backend === "running" ? "healthy" : "unhealthy";
  var mongoClass = statusInfo.mongo === "connected" ? "healthy" : "unhealthy";
  var backendText = statusInfo.backend || statusInfo.error || "unknown";
  var mongoText = statusInfo.mongo || "unknown";
  var eventsCount = statusInfo.total_events != null ? statusInfo.total_events : "—";
  var uptimeText = statusInfo.uptime != null ? statusInfo.uptime.toFixed(1) + " s" : "—";

  var eventsHtml;
  if (eventList.length === 0) {
    eventsHtml = '<p class="empty">No events recorded yet.</p>';
  } else {
    var rows = eventList.map(function (e) {
      return "<tr>" +
        "<td>" + (e.timestamp || "—") + "</td>" +
        "<td>" + (e.type || "—") + "</td>" +
        "<td>" + (e.message || JSON.stringify(e)) + "</td>" +
        "</tr>";
    }).join("");
    eventsHtml =
      "<table>" +
      "<thead><tr><th>Timestamp</th><th>Type</th><th>Details</th></tr></thead>" +
      "<tbody>" + rows + "</tbody>" +
      "</table>";
  }

  return '<!DOCTYPE html>' +
    '<html lang="en">' +
    '<head>' +
    '<meta charset="UTF-8" />' +
    '<meta name="viewport" content="width=device-width, initial-scale=1.0" />' +
    '<title>Self-Healing Framework Dashboard</title>' +
    '<style>' +
    '* { box-sizing: border-box; margin: 0; padding: 0; }' +
    'body { font-family: "Segoe UI", system-ui, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; padding: 2rem; }' +
    'h1 { font-size: 1.8rem; margin-bottom: .5rem; color: #38bdf8; }' +
    '.subtitle { color: #94a3b8; margin-bottom: 2rem; }' +
    '.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.2rem; margin-bottom: 2rem; }' +
    '.card { background: #1e293b; border-radius: 12px; padding: 1.4rem; border: 1px solid #334155; }' +
    '.card h2 { font-size: 1rem; color: #94a3b8; margin-bottom: .6rem; }' +
    '.card .value { font-size: 1.6rem; font-weight: 700; }' +
    '.healthy { color: #4ade80; }' +
    '.unhealthy { color: #f87171; }' +
    'table { width: 100%; border-collapse: collapse; }' +
    'th, td { text-align: left; padding: .6rem .8rem; border-bottom: 1px solid #334155; }' +
    'th { color: #94a3b8; font-weight: 600; font-size: .85rem; text-transform: uppercase; }' +
    '.empty { text-align: center; color: #64748b; padding: 2rem; }' +
    '</style>' +
    '</head>' +
    '<body>' +
    '<h1>AI-Based Self-Healing Framework</h1>' +
    '<p class="subtitle">Container Deployment &amp; Failure Simulation Dashboard</p>' +
    '<div class="grid">' +
    '<div class="card"><h2>Backend</h2><div class="value ' + backendClass + '">' + backendText + '</div></div>' +
    '<div class="card"><h2>MongoDB</h2><div class="value ' + mongoClass + '">' + mongoText + '</div></div>' +
    '<div class="card"><h2>Total Events</h2><div class="value">' + eventsCount + '</div></div>' +
    '<div class="card"><h2>Backend Uptime</h2><div class="value">' + uptimeText + '</div></div>' +
    '</div>' +
    '<div class="card"><h2>Recent Events</h2>' + eventsHtml + '</div>' +
    '</body>' +
    '</html>';
}

// ── Routes ──────────────────────────────────────────────────────────

// Root — dashboard HTML
app.get("/", async function (_req, res) {
  var status = await callBackend("/api/status");
  var events = await callBackend("/api/events");

  var statusInfo = status.ok ? status.data : { error: status.error };
  var eventList = events.ok && events.data.events ? events.data.events : [];

  res.send(buildDashboard(statusInfo, eventList));
});

// Health check
app.get("/health", async function (_req, res) {
  var backend = await callBackend("/health");
  if (backend.ok) {
    return res.json({ status: "healthy", backend: backend.data });
  }
  return res.status(503).json({ status: "degraded", backend: backend.error });
});

// Proxy: GET backend status
app.get("/api/status", async function (_req, res) {
  var result = await callBackend("/api/status");
  res.status(result.ok ? 200 : 502).json(result.ok ? result.data : { error: result.error });
});

// Proxy: GET events
app.get("/api/events", async function (_req, res) {
  var result = await callBackend("/api/events");
  res.status(result.ok ? 200 : 502).json(result.ok ? result.data : { error: result.error });
});

// Proxy: POST event
app.post("/api/events", async function (req, res) {
  try {
    var response = await axios.post(BACKEND_URL + "/api/events", req.body, { timeout: 5000 });
    res.status(201).json(response.data);
  } catch (err) {
    var msg = err.response ? err.response.data : err.message;
    console.error("[FRONTEND] POST /api/events failed:", msg);
    res.status(502).json({ error: msg });
  }
});

// ── Start server ────────────────────────────────────────────────────
app.listen(PORT, "0.0.0.0", function () {
  console.log("[FRONTEND] Dashboard running on http://0.0.0.0:" + PORT);
  console.log("[FRONTEND] Backend URL: " + BACKEND_URL);
});

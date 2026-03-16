"""
generate_network.py
-------------------
Generates a single self-contained HTML file (node_map.html) that lets the
user drag-and-drop / browse ANY CSV file.  No predetermined file path.

Expected CSV columns (header row required, order flexible):
    From Node | To Node | Distance (km) | Time (mins) | Fuel (Liters)

Run:
    python generate_network.py
Then open node_map.html in any modern browser.
"""

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Network Path Finder</title>

<!-- vis-network (CDN) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
<link  href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet"/>

<style>
/* ── Reset & base ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #0d0d0f;
  --panel-bg:  #141418;
  --panel-border: rgba(255,255,255,0.07);
  --accent:    #4FC3F7;
  --gold:      #FFD740;
  --green:     #00E676;
  --red:       #FF5252;
  --text:      #E0E0E0;
  --muted:     #607080;
  --font:      'Segoe UI', system-ui, sans-serif;
}

html, body {
  height: 100%; width: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  overflow: hidden;
}

/* ── Network canvas ───────────────────────────────────────── */
#network-container {
  position: fixed; inset: 0;
  background: var(--bg);
}

/* ── Side panel ───────────────────────────────────────────── */
#panel {
  position: fixed;
  top: 20px; left: 20px;
  width: 300px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 14px;
  padding: 22px 20px;
  box-shadow: 0 8px 40px rgba(0,0,0,.7);
  scrollbar-width: thin;
  scrollbar-color: #333 transparent;
  z-index: 10;
}

#panel h3 {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: .5px;
  color: var(--accent);
  margin-bottom: 16px;
}

/* ── Drop zone ────────────────────────────────────────────── */
#drop-zone {
  border: 2px dashed rgba(79,195,247,.35);
  border-radius: 10px;
  padding: 22px 16px;
  text-align: center;
  cursor: pointer;
  transition: border-color .2s, background .2s;
  margin-bottom: 16px;
  user-select: none;
}
#drop-zone:hover, #drop-zone.drag-over {
  border-color: var(--accent);
  background: rgba(79,195,247,.07);
}
#drop-zone svg { display: block; margin: 0 auto 10px; opacity: .55; }
#drop-zone p   { font-size: 13px; color: #90A4AE; line-height: 1.5; }
#drop-zone span { color: var(--accent); font-weight: 600; cursor: pointer; }
#file-input { display: none; }

#file-status {
  font-size: 12px;
  text-align: center;
  margin-bottom: 12px;
  min-height: 16px;
  color: var(--green);
  word-break: break-all;
}
#file-status.error { color: var(--red); }

/* ── Divider ──────────────────────────────────────────────── */
.divider {
  border: none;
  border-top: 1px solid var(--panel-border);
  margin: 14px 0;
}

/* ── Form elements ────────────────────────────────────────── */
label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.1px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 5px;
}

select {
  width: 100%;
  padding: 9px 11px;
  margin-bottom: 13px;
  background: #1c1c22;
  color: var(--text);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 7px;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%23607080' d='M1 1l5 5 5-5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}
select:focus { border-color: var(--accent); }
select:disabled { opacity: .35; cursor: not-allowed; }

button {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 7px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: background .15s, transform .1s;
}
button:active { transform: scale(.98); }

#find-btn {
  background: var(--accent);
  color: #002233;
  margin-bottom: 8px;
}
#find-btn:hover    { background: #29B6F6; }
#find-btn:disabled { opacity: .35; cursor: not-allowed; }

#reset-btn {
  background: #1e2832;
  color: #90A4AE;
  font-size: 12px;
  padding: 7px;
  display: none;
}
#reset-btn:hover { background: #263342; }

/* ── Show-all-values toggle row ───────────────────────────── */
.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #1c1c22;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 9px 12px;
  margin-bottom: 13px;
  cursor: pointer;
  user-select: none;
  transition: border-color .2s, background .2s;
}
.toggle-row:hover { border-color: rgba(79,195,247,.3); background: #1e1e28; }
.toggle-row.disabled { opacity: .35; cursor: not-allowed; pointer-events: none; }

.toggle-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: .2px;
}
.toggle-label .t-icon { font-size: 14px; }

/* pill switch */
.pill {
  position: relative;
  width: 36px; height: 20px;
  background: #2a2a38;
  border-radius: 20px;
  transition: background .2s;
  flex-shrink: 0;
}
.pill::after {
  content: '';
  position: absolute;
  top: 3px; left: 3px;
  width: 14px; height: 14px;
  border-radius: 50%;
  background: #607080;
  transition: transform .2s, background .2s;
}
.toggle-row.active .pill        { background: rgba(79,195,247,.25); border: 1px solid rgba(79,195,247,.5); }
.toggle-row.active .pill::after { transform: translateX(16px); background: var(--accent); }

/* ── Same-node tooltip ────────────────────────────────────── */
#same-node-tip {
  display: none;
  align-items: center;
  gap: 8px;
  background: rgba(255,82,82,.12);
  border: 1px solid rgba(255,82,82,.4);
  border-radius: 8px;
  padding: 9px 12px;
  margin-bottom: 10px;
  animation: fadeUp .25s ease;
}
#same-node-tip .tip-icon { font-size: 16px; flex-shrink: 0; }
#same-node-tip .tip-text {
  font-size: 12px;
  font-weight: 600;
  color: #FF8A80;
  line-height: 1.4;
}

/* ── Criteria badge ───────────────────────────────────────── */
.criteria-badge {
  display: inline-block;
  background: rgba(79,195,247,.15);
  border: 1px solid rgba(79,195,247,.3);
  border-radius: 20px;
  padding: 1px 8px;
  font-size: 10px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: .5px;
  margin-left: 6px;
  vertical-align: middle;
}

/* ── Primary result card (gold) ───────────────────────────── */
#result {
  display: none;
  margin-top: 14px;
  padding: 14px 16px;
  background: linear-gradient(135deg,#0f1f0f,#0f0f1f);
  border: 1px solid rgba(255,215,64,.4);
  border-radius: 10px;
  box-shadow: 0 0 18px rgba(255,215,64,.18);
  animation: fadeUp .35s ease;
}

/* ── Secondary result card (muted) ───────────────────────── */
#result-secondary {
  display: none;
  margin-top: 8px;
  padding: 12px 14px;
  background: #111118;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  animation: fadeUp .4s ease;
}
#result-secondary .sec-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 10px;
}
.sec-metric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.sec-metric-item {
  background: #1a1a22;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  padding: 9px 10px;
}
.sec-metric-item .sm-icon  { font-size: 15px; margin-bottom: 3px; }
.sec-metric-item .sm-value {
  font-size: 18px; font-weight: 800;
  color: #7A8FA0; line-height: 1;
}
.sec-metric-item .sm-unit {
  font-size: 10px; color: #3a4a58;
  font-weight: 600; letter-spacing: .5px; margin-top: 2px;
}
.sec-metric-item .sm-name {
  font-size: 10px; color: #3d5060;
  font-weight: 700; letter-spacing: .8px;
  text-transform: uppercase; margin-top: 1px;
}

@keyframes fadeUp {
  from { opacity:0; transform:translateY(-6px); }
  to   { opacity:1; transform:translateY(0); }
}

.result-label {
  font-size: 10px; font-weight: 700;
  letter-spacing: 1.6px; text-transform: uppercase;
  color: var(--gold); opacity: .75; margin-bottom: 9px;
}
.path-line {
  display: flex; flex-wrap: wrap;
  align-items: center; gap: 3px;
  font-size: 13px; font-weight: 600; line-height: 1.8;
}
.node-chip {
  background: rgba(79,195,247,.16);
  border: 1px solid rgba(79,195,247,.3);
  border-radius: 5px; padding: 2px 7px;
  font-size: 12px; color: #81D4FA;
}
.node-chip.start { background: rgba(0,230,118,.16); border-color: rgba(0,230,118,.35); color: var(--green); }
.node-chip.end   { background: rgba(255,82,82,.16);  border-color: rgba(255,82,82,.35);  color: var(--red);   }
.edge-badge {
  display: inline-flex; align-items: center; gap: 3px;
  background: rgba(255,215,64,.1); border: 1px solid rgba(255,215,64,.3);
  border-radius: 20px; padding: 1px 7px;
  font-size: 11px; font-weight: 700; color: var(--gold);
}
.arrow { color: var(--gold); font-weight: 900; font-size: 11px; }
.metric-row { display:flex; align-items:center; gap:8px; margin-top:11px; }
.metric-icon  { font-size:18px; }
.metric-value { font-size:24px; font-weight:800; color:var(--gold);
                text-shadow:0 0 12px rgba(255,215,64,.55); }
.metric-unit  { font-size:13px; color:var(--muted); }
.hop-count    { margin-top:7px; font-size:11px; color:var(--muted); }

/* ── Empty-state overlay ─────────────────────────────────── */
#overlay {
  position: fixed; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  pointer-events: none; z-index: 5; gap: 12px;
}
#overlay p { font-size: 15px; color: rgba(255,255,255,.18); letter-spacing: .3px; }
</style>
</head>
<body>

<div id="overlay">
  <svg width="64" height="64" viewBox="0 0 24 24" fill="none"
       stroke="rgba(255,255,255,.12)" stroke-width="1.2"
       stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="5"  r="2"/><circle cx="5"  cy="19" r="2"/>
    <circle cx="19" cy="19" r="2"/>
    <line x1="12" y1="7"  x2="5"  y2="17"/>
    <line x1="12" y1="7"  x2="19" y2="17"/>
    <line x1="7"  y1="19" x2="17" y2="19"/>
  </svg>
  <p>Upload a CSV to visualise your network</p>
</div>

<div id="network-container"></div>

<!-- ── Side panel ── -->
<div id="panel">

  <h3>⬡ Network Path Finder</h3>

  <!-- CSV upload -->
  <div id="drop-zone">
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
         stroke="#4FC3F7" stroke-width="1.5"
         stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
      <polyline points="17 8 12 3 7 8"/>
      <line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
    <p>Drag &amp; drop a CSV here<br/>or <span id="browse-link">browse files</span></p>
  </div>
  <input type="file" id="file-input" accept=".csv"/>
  <div id="file-status"></div>

  <hr class="divider"/>

  <!-- Path finder controls -->
  <label>Start Node</label>
  <select id="start" disabled></select>

  <label>End Node</label>
  <select id="end" disabled></select>

  <label>
    Optimise By
    <span class="criteria-badge" id="criteria-badge">km</span>
  </label>
  <select id="criteria" disabled>
    <option value="distance">Distance (km)</option>
    <option value="time">Time (mins)</option>
    <option value="fuel">Fuel (Liters)</option>
  </select>

  <!-- Show all values toggle -->
  <div id="show-all-toggle" class="toggle-row disabled" onclick="toggleShowAll()">
    <span class="toggle-label">
      <span class="t-icon">👁</span>
      Show All Values
    </span>
    <span class="pill" id="toggle-pill"></span>
  </div>

  <!-- Same-node warning -->
  <div id="same-node-tip">
    <span class="tip-icon">⚠️</span>
    <span class="tip-text">Start and End nodes must be different to find a path.</span>
  </div>

  <button id="find-btn" disabled onclick="findPath()">Find Shortest Path</button>

  <!-- Primary result (gold) -->
  <div id="result"></div>

  <!-- Secondary result (other metrics, muted) -->
  <div id="result-secondary"></div>

  <button id="reset-btn" onclick="resetAll()">✕ Clear Highlights</button>

</div>

<script>
// ── Colour tokens ────────────────────────────────────────────
const C = {
  nodeDef: "#4FC3F7", nodeDim: "#1a3a4a",
  edgeDef: "#AAAAAA", edgeDim: "#2a2a2a",
  pathNode: "#FFD740", pathEdge: "#FFD740",
  start: "#00E676", end: "#FF5252",
  fontDef: "#E0F7FA", fontDim: "rgba(180,210,230,0.2)"
};

// ── Criteria meta ─────────────────────────────────────────────
const UNIT  = { distance:"km",   time:"mins", fuel:"L"  };
const ICON  = { distance:"📍",  time:"⏱",   fuel:"⛽" };
const LABEL = { distance:"Total Distance", time:"Total Time", fuel:"Total Fuel" };
const BADGE = { distance:"km",  time:"mins", fuel:"L"  };
const ALL_WEIGHTS = ["distance", "time", "fuel"];

// ── App state ─────────────────────────────────────────────────
let visNetwork   = null;
let nodesDS      = null;
let edgesDS      = null;
let graphData    = { nodes: [], edges: [] };
let currentStart = null, currentEnd = null, pathActive = false;
let showAll      = false;

// ── Edge label builder ────────────────────────────────────────
function edgeLabelFor(e, weight) {
  if (showAll) {
    return `📍 ${e.distance}km\n⏱ ${e.time}mins\n⛽ ${e.fuel}L`;
  }
  return `${ICON[weight]} ${e[weight]} ${UNIT[weight]}`;
}

// ── Refresh all edge labels ───────────────────────────────────
function updateEdgeLabels(weight) {
  if (!edgesDS) return;
  edgesDS.update(graphData.edges.map((e, i) => ({
    id: i,
    label: edgeLabelFor(e, weight)
  })));
  document.getElementById("criteria-badge").textContent = BADGE[weight];
}

// ── Toggle show-all ───────────────────────────────────────────
function toggleShowAll() {
  showAll = !showAll;
  document.getElementById("show-all-toggle").classList.toggle("active", showAll);
  const weight = document.getElementById("criteria").value;
  updateEdgeLabels(weight);
  if (pathActive) findPath();
}

// ── CSV parsing ───────────────────────────────────────────────
function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) throw new Error("CSV must have a header row and at least one data row.");

  const header = lines[0].split(",").map(h => h.trim().toLowerCase());
  const COL = {
    from:     header.findIndex(h => h.includes("from")),
    to:       header.findIndex(h => h.includes("to")),
    distance: header.findIndex(h => h.includes("distance")),
    time:     header.findIndex(h => h.includes("time")),
    fuel:     header.findIndex(h => h.includes("fuel"))
  };

  const missing = Object.entries(COL).filter(([,i]) => i === -1).map(([k]) => k);
  if (missing.length) throw new Error(`Missing columns: ${missing.join(", ")}`);

  const nodesSet = new Set();
  const edges    = [];

  for (let i = 1; i < lines.length; i++) {
    const raw = lines[i];
    if (!raw.trim()) continue;
    const cells = raw.match(/(".*?"|[^",\n]+|(?<=,)(?=,)|(?<=,)$|^(?=,))/g)
                  || raw.split(",");
    const cell  = j => (cells[j] ?? "").replace(/^"|"$/g, "").trim();
    const from = cell(COL.from), to = cell(COL.to);
    if (!from || !to) continue;
    nodesSet.add(from); nodesSet.add(to);
    edges.push({
      from, to,
      distance: parseFloat(cell(COL.distance)) || 0,
      time:     parseFloat(cell(COL.time))     || 0,
      fuel:     parseFloat(cell(COL.fuel))     || 0
    });
  }

  return { nodes: [...nodesSet], edges };
}

// ── Build vis network ─────────────────────────────────────────
function buildNetwork(data) {
  graphData = data;
  const weight = document.getElementById("criteria").value || "distance";

  const nodeItems = data.nodes.map(n => ({
    id: n, label: n,
    color: { background: C.nodeDef, border: C.nodeDef },
    font: { color: C.fontDef, size: 28, strokeWidth: 4, strokeColor: "#000" },
    size: 28
  }));

  const edgeItems = data.edges.map((e, i) => ({
    id: i, from: e.from, to: e.to,
    label: edgeLabelFor(e, weight),
    arrows: "to",
    color: { color: C.edgeDef },
    font: { color: "#fff", size: 16, align: "top", strokeWidth: 0 },
    smooth: { type: "dynamic" }
  }));

  nodesDS = new vis.DataSet(nodeItems);
  edgesDS = new vis.DataSet(edgeItems);

  const container = document.getElementById("network-container");
  if (visNetwork) { visNetwork.destroy(); }

  visNetwork = new vis.Network(container,
    { nodes: nodesDS, edges: edgesDS },
    {
      physics: {
        solver: "barnesHut",
        barnesHut: { gravitationalConstant:-20000, centralGravity:.3,
                     springLength:250, springStrength:.05, damping:.09 }
      },
      nodes: { shape:"dot" },
      edges: { smooth:{ type:"dynamic" } },
      interaction: { hover:true }
    }
  );
}

function populateSelects(nodes) {
  ["start","end"].forEach(id => {
    const sel = document.getElementById(id);
    sel.innerHTML = nodes.map(n => `<option value="${n}">${n}</option>`).join("");
    sel.disabled  = false;
  });
  document.getElementById("criteria").disabled = false;
  document.getElementById("find-btn").disabled  = false;
  document.getElementById("show-all-toggle").classList.remove("disabled");
  if (nodes.length > 1) document.getElementById("end").selectedIndex = 1;
}

// ── Same-node validation ──────────────────────────────────────
function checkSameNode() {
  const s = document.getElementById("start").value;
  const e = document.getElementById("end").value;
  const isSame = s && e && s === e;
  document.getElementById("same-node-tip").style.display = isSame ? "flex" : "none";
  document.getElementById("find-btn").disabled = isSame;
}

// ── File handling ─────────────────────────────────────────────
function loadFile(file) {
  if (!file || !file.name.endsWith(".csv")) {
    setStatus("Please upload a .csv file.", true); return;
  }
  const reader = new FileReader();
  reader.onload = ev => {
    try {
      const data = parseCSV(ev.target.result);
      buildNetwork(data);
      populateSelects(data.nodes);
      document.getElementById("overlay").style.display = "none";
      setStatus(`✓ ${file.name}  (${data.nodes.length} nodes, ${data.edges.length} edges)`);
      checkSameNode();
      setTimeout(() => {
        highlightNode("start", document.getElementById("start").value);
        highlightNode("end",   document.getElementById("end").value);
      }, 900);
    } catch (err) {
      setStatus("Error: " + err.message, true);
    }
  };
  reader.readAsText(file);
}

function setStatus(msg, isError=false) {
  const el = document.getElementById("file-status");
  el.textContent = msg;
  el.className = isError ? "error" : "";
}

const dz = document.getElementById("drop-zone");
dz.addEventListener("dragover",  e => { e.preventDefault(); dz.classList.add("drag-over"); });
dz.addEventListener("dragleave", ()  => dz.classList.remove("drag-over"));
dz.addEventListener("drop",      e  => { e.preventDefault(); dz.classList.remove("drag-over"); loadFile(e.dataTransfer.files[0]); });
dz.addEventListener("click", () => document.getElementById("file-input").click());
document.getElementById("browse-link").addEventListener("click", e => { e.stopPropagation(); document.getElementById("file-input").click(); });
document.getElementById("file-input").addEventListener("change", e => loadFile(e.target.files[0]));

// ── Criteria change ───────────────────────────────────────────
document.getElementById("criteria").addEventListener("change", e => {
  updateEdgeLabels(e.target.value);
  if (pathActive) findPath();
});

// ── Highlight helpers ─────────────────────────────────────────
function resetHighlights() {
  if (!nodesDS) return;
  const weight = document.getElementById("criteria").value;
  nodesDS.update(graphData.nodes.map(n => ({
    id: n,
    color: { background: C.nodeDef, border: C.nodeDef },
    font:  { color: C.fontDef, size: 28, strokeWidth: 4, strokeColor: "#000" },
    size: 28, opacity: 1
  })));
  edgesDS.update(graphData.edges.map((e, i) => ({
    id: i,
    color: { color: C.edgeDef },
    font:  { color: "#fff", size: 16, strokeWidth: 0 },
    label: edgeLabelFor(e, weight),
    width: 1
  })));
}

function highlightNode(role, name) {
  if (role === "start") currentStart = name;
  else                  currentEnd   = name;
  if (pathActive || !nodesDS) return;
  resetHighlights();
  const applyNode = (n, col) => n && nodesDS.update([{ id: n, color: { background: col, border: "#fff" }, size: 36 }]);
  applyNode(currentStart, C.start);
  applyNode(currentEnd,   C.end);
}

document.getElementById("start").addEventListener("change", e => { highlightNode("start", e.target.value); checkSameNode(); });
document.getElementById("end").addEventListener("change",   e => { highlightNode("end",   e.target.value); checkSameNode(); });

// ── Dijkstra ──────────────────────────────────────────────────
function dijkstra(start, end, weight) {
  const dist = {}, prev = {};
  let remaining = [...graphData.nodes];
  graphData.nodes.forEach(n => { dist[n] = Infinity; prev[n] = null; });
  dist[start] = 0;

  while (remaining.length) {
    remaining.sort((a,b) => dist[a] - dist[b]);
    const u = remaining.shift();
    if (u === end) break;
    graphData.edges.forEach(e => {
      if (e.from !== u) return;
      const alt = dist[u] + e[weight];
      if (alt < dist[e.to]) { dist[e.to] = alt; prev[e.to] = u; }
    });
  }

  const path = []; let cur = end;
  while (cur) { path.unshift(cur); cur = prev[cur]; }
  return { path, total: dist[end] };
}

// ── Sum other metrics along a given path ──────────────────────
function sumAlongPath(path, weights) {
  const totals = {};
  weights.forEach(w => { totals[w] = 0; });
  for (let i = 0; i < path.length - 1; i++) {
    const edge = graphData.edges.find(e => e.from === path[i] && e.to === path[i+1]);
    if (edge) weights.forEach(w => { totals[w] += edge[w]; });
  }
  // Round to avoid floating-point noise
  weights.forEach(w => { totals[w] = Math.round(totals[w] * 100) / 100; });
  return totals;
}

// ── Find path ─────────────────────────────────────────────────
function findPath() {
  const start  = document.getElementById("start").value;
  const end    = document.getElementById("end").value;
  const weight = document.getElementById("criteria").value;
  if (start === end) { checkSameNode(); return; }

  const { path, total } = dijkstra(start, end, weight);
  const pathSet   = new Set(path);
  const pathPairs = new Set(path.slice(0,-1).map((_,i) => path[i]+"|"+path[i+1]));

  // ── Highlight network
  if (nodesDS) {
    pathActive = true;

    nodesDS.update(graphData.nodes.map(n => {
      const on = pathSet.has(n);
      let bg = on ? C.pathNode : C.nodeDim;
      let fc = on ? "#1A1A2E"  : C.fontDim;
      if (n === start) { bg = C.start; fc = "#003300"; }
      if (n === end)   { bg = C.end;   fc = "#3b0000"; }
      return {
        id: n, opacity: 1,
        color: { background: bg, border: on ? "#fff" : "#1e2e3e" },
        size: on ? 38 : 24,
        font: { color: fc, size: on ? 32 : 26, strokeWidth: on ? 4 : 2,
                strokeColor: on ? "rgba(255,255,255,.5)" : "rgba(0,0,0,.2)" }
      };
    }));

    edgesDS.update(graphData.edges.map((e, i) => {
      const on = pathPairs.has(e.from+"|"+e.to);
      return {
        id: i,
        label: edgeLabelFor(e, weight),
        color: { color: on ? C.pathEdge : C.edgeDim },
        font:  { color: on ? C.pathEdge : "rgba(255,255,255,.1)",
                 size: on ? 18 : 14, strokeWidth: on ? 3 : 0,
                 strokeColor: on ? "#000" : "transparent" },
        width: on ? 5 : 1
      };
    }));
  }

  // ── Primary result card
  const unit = UNIT[weight], icon = ICON[weight];
  const pathHtml = path.map((n, i) => {
    let cls = "node-chip";
    if (i === 0)             cls += " start";
    if (i === path.length-1) cls += " end";
    let suffix = "";
    if (i < path.length - 1) {
      const edge = graphData.edges.find(e => e.from === n && e.to === path[i+1]);
      const val  = edge ? edge[weight] : "?";
      suffix = `<span class="arrow">→</span>
                <span class="edge-badge">${icon} ${val} ${unit}</span>
                <span class="arrow">→</span>`;
    }
    return `<span class="${cls}">${n}</span>${suffix}`;
  }).join(" ");

  const hops = path.length - 1;
  document.getElementById("result").style.display = "block";
  document.getElementById("result").innerHTML = `
    <div class="result-label">Optimal Route Found</div>
    <div class="path-line">${pathHtml}</div>
    <div class="metric-row">
      <span class="metric-icon">${icon}</span>
      <span class="metric-value">${total}</span>
      <span class="metric-unit">${unit}</span>
    </div>
    <div class="hop-count">${LABEL[weight]} &nbsp;·&nbsp; ${hops} hop${hops!==1?"s":""}</div>`;

  // ── Secondary result card (other two metrics along the same path)
  const otherWeights = ALL_WEIGHTS.filter(w => w !== weight);
  const otherTotals  = sumAlongPath(path, otherWeights);

  document.getElementById("result-secondary").style.display = "block";
  document.getElementById("result-secondary").innerHTML = `
    <div class="sec-label">Also Along This Route</div>
    <div class="sec-metric-grid">
      ${otherWeights.map(w => `
        <div class="sec-metric-item">
          <div class="sm-icon">${ICON[w]}</div>
          <div class="sm-value">${otherTotals[w]}</div>
          <div class="sm-unit">${UNIT[w]}</div>
          <div class="sm-name">${LABEL[w]}</div>
        </div>
      `).join("")}
    </div>`;

  document.getElementById("reset-btn").style.display = "block";
}

// ── Reset all ─────────────────────────────────────────────────
function resetAll() {
  pathActive = false;
  resetHighlights();
  highlightNode("start", document.getElementById("start").value);
  highlightNode("end",   document.getElementById("end").value);
  document.getElementById("result").style.display           = "none";
  document.getElementById("result-secondary").style.display = "none";
  document.getElementById("reset-btn").style.display        = "none";
}
</script>
</body>
</html>
"""

import os
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_map.html")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"Generated: {OUTPUT}")
print("Open it in any modern browser and upload your CSV to get started.")
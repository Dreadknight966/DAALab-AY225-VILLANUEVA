/**
 * app.js — Data Artifact Template
 * Fetches ./assets/data.json, renders Chart.js visualisation + HTML table.
 *
 * Assumptions about data shape (produced by upstream Python processor):
 *   [ { "Date": "2023-01", "MetricA": 100, "MetricB": 50 }, … ]
 *
 * The first key whose values are non-numeric is treated as the Label axis.
 * All remaining numeric keys become chart series and table columns.
 */

/* ═══════════════════════════════════════════════════════════════════════════════
   CONFIG
   ═══════════════════════════════════════════════════════════════════════════════ */

const CONFIG = {
  dataPath:    './assets/data.json',
  maxTiles:    3,           // how many metric summary tiles to show
  chartHeight: 400,         // px height for the canvas
  pageSize:    50,          // max rows rendered initially (virtual-ish)
};

/* ═══════════════════════════════════════════════════════════════════════════════
   DOM REFS
   ═══════════════════════════════════════════════════════════════════════════════ */

const DOM = {
  statusBadge:       document.getElementById('statusBadge'),
  statusMessage:     document.getElementById('statusMessage'),
  statusProgressBar: document.getElementById('statusProgressBar'),
  statRecords:       document.getElementById('statRecords'),
  statFields:        document.getElementById('statFields'),
  statSource:        document.getElementById('statSource'),
  statLoaded:        document.getElementById('statLoaded'),
  metricTiles:       document.getElementById('metricTiles'),
  chartContainer:    document.getElementById('chartContainer'),
  chartPlaceholder:  document.getElementById('chartPlaceholder'),
  chartLegendPanel:  document.getElementById('chartLegendPanel'),
  chartTypeBtns:     document.querySelectorAll('.chart-type-btn'),
  tableWrapper:      document.getElementById('tableWrapper'),
  tablePlaceholder:  document.getElementById('tablePlaceholder'),
  tableSearch:       document.getElementById('tableSearch'),
  tableRowCount:     document.getElementById('tableRowCount'),
  tableFooterNote:   document.getElementById('tableFooterNote'),
  btnExportCsv:      document.getElementById('btnExportCsv'),
};

/* ═══════════════════════════════════════════════════════════════════════════════
   STATE
   ═══════════════════════════════════════════════════════════════════════════════ */

const state = {
  rawData:       [],
  labelKey:      '',
  numericKeys:   [],
  chartInstance: null,
  currentType:   'line',
  sortKey:       null,
  sortDir:       'asc',    // 'asc' | 'desc'
  filterQuery:   '',
};

/* ═══════════════════════════════════════════════════════════════════════════════
   UTILITIES
   ═══════════════════════════════════════════════════════════════════════════════ */

/** CSS variable reader (for chart colours) */
function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
    || getComputedStyle(document.body).getPropertyValue(name).trim();
}

/** Detect whether a value is numeric */
const isNumeric = (v) => v !== null && v !== '' && !isNaN(Number(v));

/** Format numbers nicely (locale-aware, max 2 decimal places) */
const fmt = (n) =>
  typeof n === 'number'
    ? n.toLocaleString(undefined, { maximumFractionDigits: 2 })
    : n;

/** Calculate sum, min, max, mean for an array of numbers */
function stats(arr) {
  const nums = arr.filter(v => isNumeric(v)).map(Number);
  if (!nums.length) return { sum: 0, min: 0, max: 0, mean: 0, count: 0 };
  const sum  = nums.reduce((a, b) => a + b, 0);
  return {
    sum,
    min:   Math.min(...nums),
    max:   Math.max(...nums),
    mean:  sum / nums.length,
    count: nums.length,
  };
}

/** Debounce helper */
function debounce(fn, delay) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

/* ═══════════════════════════════════════════════════════════════════════════════
   STATUS HELPERS
   ═══════════════════════════════════════════════════════════════════════════════ */

function setStatus(type, message, progress = 0) {
  // type: 'pending' | 'loaded' | 'error'
  DOM.statusBadge.className = `status-badge status-badge--${type}`;
  DOM.statusBadge.innerHTML = `<span class="status-dot" aria-hidden="true"></span>${
    type.charAt(0).toUpperCase() + type.slice(1)
  }`;
  DOM.statusMessage.textContent = message;
  DOM.statusProgressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   DATA FETCHING
   ═══════════════════════════════════════════════════════════════════════════════ */

async function fetchData() {
  setStatus('pending', 'Fetching data…', 10);

  const response = await fetch(CONFIG.dataPath);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} — ${response.statusText}`);
  }

  setStatus('pending', 'Parsing JSON…', 50);
  const data = await response.json();

  if (!Array.isArray(data) || data.length === 0) {
    throw new Error('data.json must be a non-empty array of objects.');
  }

  return data;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   DATA ANALYSIS — detect label key & numeric keys
   ═══════════════════════════════════════════════════════════════════════════════ */

function analyseSchema(data) {
  const firstRow   = data[0];
  const allKeys    = Object.keys(firstRow);

  // First key whose column-values are predominantly non-numeric → label
  let labelKey   = allKeys[0];
  let numericKeys = [];

  for (const key of allKeys) {
    const colVals  = data.map(r => r[key]);
    const numCount = colVals.filter(v => isNumeric(v)).length;
    const ratio    = numCount / colVals.length;

    if (ratio >= 0.8) {
      numericKeys.push(key);
    } else if (key === allKeys[0] || numCount === 0) {
      labelKey = key; // use last clearly non-numeric key as label
    }
  }

  // If all keys ended up numeric (e.g. index-only dataset), force first as label
  if (numericKeys.length === allKeys.length) {
    labelKey    = numericKeys.shift();
  }

  return { labelKey, numericKeys };
}

/* ═══════════════════════════════════════════════════════════════════════════════
   METRIC TILES
   ═══════════════════════════════════════════════════════════════════════════════ */

function renderMetricTiles(data, numericKeys) {
  const tiles = numericKeys.slice(0, CONFIG.maxTiles);

  DOM.metricTiles.innerHTML = tiles.map(key => {
    const { sum, max } = stats(data.map(r => r[key]));
    return `
      <article class="metric-tile reveal is-visible" role="listitem">
        <span class="metric-tile-label">${key}</span>
        <span class="metric-tile-value">${fmt(Math.round(sum))}</span>
        <span class="status-stat-label">Sum · Max&nbsp;${fmt(Math.round(max))}</span>
      </article>
    `.trim();
  }).join('');
}

/* ═══════════════════════════════════════════════════════════════════════════════
   CHART COLOURS
   ═══════════════════════════════════════════════════════════════════════════════ */

function getChartColors(count) {
  const palette = ['--chart-color-1','--chart-color-2','--chart-color-3','--chart-color-4'];
  const baseColors = Array.from({ length: count }, (_, i) =>
    cssVar(palette[i % palette.length]) || `hsl(${(i * 67) % 360}, 65%, 55%)`
  );

  return baseColors.map(c => ({
    border:     c,
    background: hexToRgba(c, state.currentType === 'line' ? 0.12 : 0.65),
  }));
}

/** Try to convert hex string to rgba */
function hexToRgba(hex, alpha) {
  const clean = hex.trim();
  const shortHex = /^#([a-f\d])([a-f\d])([a-f\d])$/i;
  const fullHex  = /^#([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i;

  let r, g, b;

  const s = shortHex.exec(clean);
  const f = fullHex.exec(clean);

  if (s) {
    [r, g, b] = s.slice(1).map(x => parseInt(x + x, 16));
  } else if (f) {
    [r, g, b] = f.slice(1).map(x => parseInt(x, 16));
  } else {
    // fallback — just use the colour string with opacity via Canvas
    return clean;
  }

  return `rgba(${r},${g},${b},${alpha})`;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   CHART RENDERING
   ═══════════════════════════════════════════════════════════════════════════════ */

function buildChartDatasets(data, labelKey, numericKeys) {
  const colors = getChartColors(numericKeys.length);
  return numericKeys.map((key, i) => ({
    label:           key,
    data:            data.map(r => (isNumeric(r[key]) ? Number(r[key]) : null)),
    borderColor:     colors[i].border,
    backgroundColor: colors[i].background,
    borderWidth:     2,
    pointRadius:     data.length > 80 ? 0 : 3,
    pointHoverRadius: 5,
    tension:         0.35,
    fill:            state.currentType === 'line',
    spanGaps:        true,
  }));
}

function renderChart(data, labelKey, numericKeys) {
  // Remove placeholder
  if (DOM.chartPlaceholder) DOM.chartPlaceholder.style.display = 'none';

  // Destroy existing instance before recreating
  if (state.chartInstance) {
    state.chartInstance.destroy();
    state.chartInstance = null;
  }

  // Create canvas
  const canvas = document.createElement('canvas');
  canvas.id = 'mainChart';
  canvas.setAttribute('role', 'img');
  canvas.setAttribute('aria-label', 'Data visualisation chart');
  canvas.style.height = `${CONFIG.chartHeight}px`;
  DOM.chartContainer.appendChild(canvas);

  const labels   = data.map(r => r[labelKey]);
  const datasets = buildChartDatasets(data, labelKey, numericKeys);

  const gridColor = cssVar('--chart-grid')  || 'rgba(128,128,128,0.1)';
  const tickColor = cssVar('--chart-tick')  || '#888';

  state.chartInstance = new Chart(canvas, {
    type: state.currentType,
    data: { labels, datasets },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend:  { display: false },   // custom legend below
        tooltip: {
          backgroundColor: cssVar('--bg-surface')  || '#fff',
          titleColor:      cssVar('--text-color')   || '#000',
          bodyColor:       cssVar('--text-secondary') || '#555',
          borderColor:     cssVar('--border-color') || '#ddd',
          borderWidth:     1,
          padding:         10,
          titleFont:       { family: "'DM Mono', monospace", size: 11 },
          bodyFont:        { family: "'DM Sans', sans-serif", size: 12 },
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${fmt(ctx.parsed.y)}`,
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color:    tickColor,
            font:     { family: "'DM Mono', monospace", size: 10 },
            maxRotation: 45,
            autoSkip: true,
            maxTicksLimit: 20,
          },
          grid: { color: gridColor },
        },
        y: {
          ticks: {
            color:    tickColor,
            font:     { family: "'DM Mono', monospace", size: 10 },
            callback: (v) => fmt(v),
          },
          grid: { color: gridColor },
        },
      },
    },
  });

  renderChartLegend(datasets);
}

function renderChartLegend(datasets) {
  DOM.chartLegendPanel.innerHTML = `
    <p style="font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;
              color:var(--text-tertiary);margin-bottom:0.6rem;">Series</p>
    ${datasets.map((ds, i) => `
      <div class="legend-entry" data-index="${i}" role="button" tabindex="0"
           aria-label="Toggle ${ds.label} series">
        <span class="legend-swatch" style="background:${ds.borderColor}"></span>
        <span>${ds.label}</span>
      </div>
    `).join('')}
  `;

  DOM.chartLegendPanel.querySelectorAll('.legend-entry').forEach(entry => {
    const toggle = () => {
      const idx = Number(entry.dataset.index);
      const meta = state.chartInstance.getDatasetMeta(idx);
      meta.hidden = !meta.hidden;
      entry.classList.toggle('is-hidden', meta.hidden);
      state.chartInstance.update();
    };
    entry.addEventListener('click', toggle);
    entry.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') toggle(); });
  });
}

/* ═══════════════════════════════════════════════════════════════════════════════
   CHART TYPE TOGGLE
   ═══════════════════════════════════════════════════════════════════════════════ */

function initChartTypeControls() {
  DOM.chartTypeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.dataset.chartType;
      if (type === state.currentType) return;

      state.currentType = type;

      DOM.chartTypeBtns.forEach(b => {
        b.classList.toggle('chart-type-btn--active', b === btn);
        b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
      });

      // Rebuild chart with new type
      if (state.rawData.length) {
        // Remove old canvas
        const old = document.getElementById('mainChart');
        if (old) old.remove();
        renderChart(state.rawData, state.labelKey, state.numericKeys);
      }
    });
  });
}

/* ═══════════════════════════════════════════════════════════════════════════════
   TABLE RENDERING
   ═══════════════════════════════════════════════════════════════════════════════ */

function filteredSortedData() {
  let data = [...state.rawData];

  // Filter
  const q = state.filterQuery.toLowerCase().trim();
  if (q) {
    data = data.filter(row =>
      Object.values(row).some(v => String(v).toLowerCase().includes(q))
    );
  }

  // Sort
  if (state.sortKey) {
    data.sort((a, b) => {
      const va = a[state.sortKey];
      const vb = b[state.sortKey];
      const numA = Number(va), numB = Number(vb);
      const cmp  = isNumeric(va) && isNumeric(vb)
        ? numA - numB
        : String(va).localeCompare(String(vb));
      return state.sortDir === 'asc' ? cmp : -cmp;
    });
  }

  return data;
}

function renderTable() {
  const data      = filteredSortedData();
  const allKeys   = [state.labelKey, ...state.numericKeys];
  const isNumCol  = (k) => state.numericKeys.includes(k);

  DOM.tableRowCount.textContent = `${data.length.toLocaleString()} row${data.length !== 1 ? 's' : ''}`;

  const tableEl = document.createElement('table');
  tableEl.className = 'data-table';
  tableEl.setAttribute('role', 'grid');

  /* thead */
  const sortIconFor = (key) => {
    if (state.sortKey !== key) return '';
    return state.sortDir === 'asc' ? ' sort-asc' : ' sort-desc';
  };

  tableEl.innerHTML = `
    <thead>
      <tr>
        ${allKeys.map(k => `
          <th class="${isNumCol(k) ? 'num' : ''}${sortIconFor(k)}"
              data-key="${k}"
              tabindex="0"
              role="columnheader"
              aria-sort="${state.sortKey === k ? (state.sortDir === 'asc' ? 'ascending' : 'descending') : 'none'}"
              title="Sort by ${k}">
            ${k}
          </th>
        `).join('')}
      </tr>
    </thead>
    <tbody>
      ${data.slice(0, CONFIG.pageSize).map(row => `
        <tr>
          ${allKeys.map(k => `
            <td class="${isNumCol(k) ? 'num' : ''}">${
              isNumCol(k) ? fmt(Number(row[k])) : (row[k] ?? '—')
            }</td>
          `).join('')}
        </tr>
      `).join('')}
    </tbody>
  `;

  // Warn if data was truncated
  if (data.length > CONFIG.pageSize) {
    const note = document.createElement('caption');
    note.style.cssText = 'caption-side:bottom;font-size:0.72rem;padding:0.5rem;color:var(--text-tertiary);font-family:"DM Mono",monospace;';
    note.textContent   = `Showing first ${CONFIG.pageSize.toLocaleString()} of ${data.length.toLocaleString()} rows.`;
    tableEl.appendChild(note);
  }

  /* Sort click handlers on headers */
  tableEl.querySelectorAll('th[data-key]').forEach(th => {
    const activate = () => {
      const key = th.dataset.key;
      if (state.sortKey === key) {
        state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
      } else {
        state.sortKey = key;
        state.sortDir = 'asc';
      }
      renderTable();
    };
    th.addEventListener('click', activate);
    th.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') activate(); });
  });

  // Swap placeholder → table
  if (DOM.tablePlaceholder) DOM.tablePlaceholder.remove();
  const existing = DOM.tableWrapper.querySelector('.data-table');
  if (existing) existing.remove();
  DOM.tableWrapper.appendChild(tableEl);
}

/* ═══════════════════════════════════════════════════════════════════════════════
   SEARCH / FILTER
   ═══════════════════════════════════════════════════════════════════════════════ */

function initTableSearch() {
  DOM.tableSearch.disabled = false;
  DOM.tableSearch.addEventListener('input', debounce(() => {
    state.filterQuery = DOM.tableSearch.value;
    renderTable();
  }, 250));
}

/* ═══════════════════════════════════════════════════════════════════════════════
   CSV EXPORT
   ═══════════════════════════════════════════════════════════════════════════════ */

function initCsvExport() {
  DOM.btnExportCsv.disabled = false;
  DOM.btnExportCsv.addEventListener('click', () => {
    const data    = filteredSortedData();
    const keys    = [state.labelKey, ...state.numericKeys];
    const header  = keys.join(',');
    const rows    = data.map(row =>
      keys.map(k => {
        const v = row[k] ?? '';
        return String(v).includes(',') ? `"${String(v).replace(/"/g,'""')}"` : v;
      }).join(',')
    );
    const csv     = [header, ...rows].join('\n');
    const blob    = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url     = URL.createObjectURL(blob);
    const a       = Object.assign(document.createElement('a'), {
      href:     url,
      download: 'data-export.csv',
    });
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });
}

/* ═══════════════════════════════════════════════════════════════════════════════
   SCROLL REVEAL (lightweight IntersectionObserver)
   ═══════════════════════════════════════════════════════════════════════════════ */

function initScrollReveal() {
  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.reveal:not(.is-visible)').forEach(el => observer.observe(el));
}

/* ═══════════════════════════════════════════════════════════════════════════════
   MAIN BOOTSTRAP
   ═══════════════════════════════════════════════════════════════════════════════ */

async function init() {
  initChartTypeControls();

  try {
    setStatus('pending', 'Connecting to data source…', 5);
    const data = await fetchData();

    setStatus('pending', 'Analysing schema…', 65);
    const { labelKey, numericKeys } = analyseSchema(data);

    // Persist to state
    state.rawData     = data;
    state.labelKey    = labelKey;
    state.numericKeys = numericKeys;

    setStatus('pending', 'Rendering visualisations…', 80);

    // ── Update status card ──
    DOM.statRecords.textContent = data.length.toLocaleString();
    DOM.statFields.textContent  = (numericKeys.length + 1).toLocaleString();
    DOM.statLoaded.textContent  = new Date().toLocaleTimeString('en-GB', { hour12: false });

    // ── Metric tiles ──
    renderMetricTiles(data, numericKeys);

    // ── Chart ──
    renderChart(data, labelKey, numericKeys);

    // ── Table ──
    renderTable();
    initTableSearch();
    initCsvExport();

    setStatus('loaded', `${data.length.toLocaleString()} records loaded successfully.`, 100);

    // Update footer note
    DOM.tableFooterNote.innerHTML = `
      <i class="fa-solid fa-circle-check" aria-hidden="true" style="color:var(--status-loaded)"></i>
      ${data.length.toLocaleString()} records loaded from <code>assets/data.json</code>
    `;

    initScrollReveal();

  } catch (err) {
    console.error('[DataArtifact] Load error:', err);

    setStatus('error', `Error: ${err.message}`, 0);

    // Show error state in chart area
    if (DOM.chartPlaceholder) {
      DOM.chartPlaceholder.querySelector('.chart-placeholder-label').innerHTML = `
        <i class="fa-solid fa-triangle-exclamation" aria-hidden="true" style="color:var(--status-error)"></i>
        ${err.message}
      `;
    }

    // Show error state in table area
    if (DOM.tablePlaceholder) {
      DOM.tablePlaceholder.querySelector('.table-placeholder-label').innerHTML = `
        <i class="fa-solid fa-triangle-exclamation" aria-hidden="true" style="color:var(--status-error)"></i>
        Could not load data: ${err.message}
      `;
    }
  }
}

/* Run once DOM is ready */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
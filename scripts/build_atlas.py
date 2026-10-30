#!/usr/bin/env python3
"""Build site/index.html: a world map of certified translator and interpreter credentials.

Reads data/credentials_by_country.csv and writes:
  site/index.html          one self-contained page (data embedded)
  site/credentials_by_country.csv   the same data for download

D3 loads from cdnjs; topojson-client and world geometry load from jsdelivr
(world-atlas@2.0.2, Natural Earth 1:50m) in the browser. No build step beyond this script.
"""
import csv
import html
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "credentials_by_country.csv"
SITE = ROOT / "site"

# Dataset country name -> name used in world-atlas geometry (where they differ).
ALIAS = {
    "United States": "United States of America",
    "Trinidad & Tobago": "Trinidad and Tobago",
    "Antigua & Barbuda": "Antigua and Barb.",
    "St. Kitts & Nevis": "St. Kitts and Nevis",
    "St. Lucia": "Saint Lucia",
    "St. Vincent & Grenadines": "St. Vin. and Gren.",
    "Dominican Republic": "Dominican Rep.",
    "Macau": "Macao",
    "Solomon Islands": "Solomon Is.",
    "Marshall Islands": "Marshall Is.",
    "Central African Republic": "Central African Rep.",
    "Republic of the Congo": "Congo",
    "Congo (DRC)": "Dem. Rep. Congo",
    "Equatorial Guinea": "Eq. Guinea",
    "Sao Tome & Principe": "São Tomé and Principe",
    "Eswatini": "eSwatini",
    "Bosnia & Herzegovina": "Bosnia and Herz.",
    "North Macedonia": "Macedonia",
    "Vatican City": "Vatican",
    "Western Sahara": "W. Sahara",
    "South Sudan": "S. Sudan",
}


def category(model: str) -> str:
    """Group the free-text Model column into a fixed set of map colours."""
    m = model.lower()
    if m.startswith("national government") or m.startswith("government requirement"):
        return "national"
    if m.startswith("government licence"):
        return "licence"
    if m.startswith("court appointment"):
        return "court"
    if m.startswith("provincial"):
        return "provincial"
    if m.startswith("professional association"):
        return "association"
    return "none"


def load_rows():
    with CSV_PATH.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        nv = r["Used for government work"].strip().lower().startswith("not verified")
        r["category"] = "none" if (r["Status"] == "not yet researched" or nv) else category(r["Model"])
        r["geo_name"] = ALIAS.get(r["Country"], r["Country"])
    return rows


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Certified Translator Atlas · Lingo Ledger</title>
<meta name="description" content="How certified translators and interpreters are credentialed in each country, who grants the credential, and whether it is used for official work.">
<style>
:root{--bg:#ffffff;--panel:#ffffff;--fg:#17172b;--muted:#64667a;--line:#e6e4f1;--soft:#f5f2fd;--accent:#5b21d6;--accent-2:#7c4dea;--accent-soft:#ece4fd;
--national:#3b1f6e;--licence:#5a2d9c;--court:#7b4fc2;--provincial:#9d7bd9;--association:#bfa8ea;--none:#dcd0f3}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent);text-decoration:none}
button,input,select{font:inherit}
.app{display:grid;grid-template-columns:232px minmax(0,1fr);min-height:100vh}
.side{background:#fbfbfe;border-right:1px solid var(--line);padding:22px 16px;display:flex;flex-direction:column;gap:18px;position:sticky;top:0;height:100vh}
.side img{display:block;width:161px;max-width:calc(100% - 16px);height:auto;align-self:flex-start;margin:0 8px}
.nav a{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:10px;color:var(--fg);font-weight:500}
.nav a:hover{background:var(--soft)}
.nav a[aria-current="page"]{background:var(--accent-soft);color:var(--accent)}
.nav small{display:block;color:var(--muted);font-weight:400;font-size:12px}
.nav .dotn{width:8px;height:8px;border-radius:50%;background:var(--accent-2);flex:none}
.side .note{margin-top:auto;font-size:12px;color:var(--muted);padding:0 8px}
main{padding:22px 28px 48px;min-width:0}
.hero{position:relative;display:flex;justify-content:space-between;gap:20px;align-items:flex-start;min-height:180px;z-index:0}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:600;margin:4px 0 6px}
h1{font-size:34px;line-height:1.15;margin:0 0 8px;letter-spacing:-.02em;font-weight:750}
.lead{color:var(--muted);max-width:60ch;margin:0;font-size:15px}
.hero .globe{position:absolute;right:150px;top:4px;width:400px;max-width:36%;height:auto;pointer-events:none;z-index:0}
.btn{display:inline-flex;align-items:center;gap:8px;padding:11px 18px;border-radius:10px;border:1px solid var(--accent);background:var(--accent);color:#fff;font-weight:600;cursor:pointer;white-space:nowrap;position:relative;z-index:1}
.btn.ghost{background:#fff;color:var(--accent)}
:focus-visible{outline:3px solid #c9b6f5;outline-offset:2px}
.stats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;margin:8px 0 18px;position:relative;z-index:1}
@media (max-width:1100px){.stats{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:640px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 16px;display:flex;gap:12px;align-items:center}
.stat i{width:38px;height:38px;border-radius:50%;background:var(--accent-soft);flex:none;display:grid;place-items:center;color:var(--accent);font-style:normal;font-weight:700}
.stat b{display:block;font-size:24px;line-height:1.1;letter-spacing:-.01em}
.stat span{color:var(--muted);font-size:13px}
.grid{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:16px;align-items:start}
@media (max-width:1100px){.grid{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px}
.card h2{font-size:16px;margin:0;font-weight:650}
.card .sub{color:var(--muted);font-size:13px;margin:2px 0 0}
.card-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:8px}
.mapbox{position:relative}
#map{width:100%;height:auto;display:block;cursor:grab;touch-action:none}
path.country{stroke:#fff;stroke-width:.35;transition:opacity .15s}
path.country:hover{opacity:.78;cursor:pointer}
path.country.sel{stroke:var(--fg);stroke-width:1.3}
.zoom{position:absolute;left:14px;bottom:14px;display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(30,20,60,.08)}
.zoom button{width:36px;height:36px;border:0;background:#fff;font-size:18px;cursor:pointer;color:var(--fg)}
.zoom button+button{border-top:1px solid var(--line)}
.legend{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px 14px;margin-top:14px;padding-top:12px;border-top:1px solid var(--line)}
.legend span{display:flex;gap:8px;align-items:flex-start;font-size:13px;color:var(--fg)}
.legend i{width:12px;height:12px;border-radius:3px;background:var(--c);margin-top:4px;flex:none}
.legend em{display:block;font-style:normal;color:var(--muted);font-size:12px}
.pick{position:relative;margin:12px 0 4px}
input.search,select{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--fg)}
.sec{margin-top:18px}
.sec h3{font-size:14px;margin:0 0 8px;font-weight:650;display:flex;justify-content:space-between}
.bars{display:grid;gap:9px}
.bar{display:grid;grid-template-columns:minmax(0,1fr) 84px 30px;gap:10px;align-items:center;font-size:13px}
.bar .lbl{display:flex;gap:8px;align-items:center;min-width:0}
.bar .lbl span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar .track{height:8px;background:var(--soft);border-radius:6px;overflow:hidden}
.bar .fill{height:100%;background:var(--c);border-radius:6px}
.bar em{font-style:normal;color:var(--muted);text-align:right}
.dot{width:9px;height:9px;border-radius:50%;background:var(--c);flex:none;display:inline-block}
#detail{margin-top:8px}
#detail h2{font-size:18px;margin:0 0 6px}
#detail .meta{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}
#detail dl{margin:8px 0 0}
#detail dt{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-top:10px;font-weight:600}
#detail dd{margin:2px 0 0;word-break:break-word}
#detail .empty{color:var(--muted);margin:6px 0 0;font-size:13px}
.badge{display:inline-block;font-size:12px;padding:2px 10px;border-radius:99px;border:1px solid var(--line);background:var(--soft);white-space:nowrap}
.b-sourced{background:#ebe2fb;border-color:#b79fe6;color:#3b1f6e}
.b-partial{background:#f7f5fc;border-color:#cfc0f0;color:#4b2a86}
.b-nyr{background:#fff;border-color:#dcd0f3;color:#6f6192;border-style:dashed}
.toolbar{display:grid;grid-template-columns:minmax(0,1fr) 220px 220px;gap:10px;margin:18px 0 10px}
@media (max-width:900px){.toolbar{grid-template-columns:1fr}}
.toolbar input{background:#fff}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px}
.chip{font-size:13px;padding:6px 13px;border-radius:99px;border:1px solid var(--line);background:#fff;color:var(--fg);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.count{color:var(--muted);font-size:13px;margin:0 0 8px}
.tablewrap{max-height:560px;overflow:auto;border:1px solid var(--line);border-radius:14px;background:#fff}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{position:sticky;top:0;background:var(--soft);text-align:left;font-weight:650;padding:10px 12px;border-bottom:1px solid var(--line);z-index:1}
td{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
tr.row{cursor:pointer}
tr.row:hover td{background:var(--soft)}
tr.row.sel td{background:var(--accent-soft)}
td.body{color:var(--muted);max-width:460px}
.nowrap{white-space:nowrap}
.empty-table{padding:24px;text-align:center;color:var(--muted)}
footer{color:var(--muted);font-size:12.5px;margin-top:28px;border-top:1px solid var(--line);padding-top:14px}
footer p{margin:6px 0}
@media (max-width:860px){
  .app{grid-template-columns:1fr}
  .side{position:static;height:auto;flex-direction:row;flex-wrap:wrap;align-items:center;gap:10px 16px;padding:12px 16px;border-right:0;border-bottom:1px solid var(--line)}
  .side img{margin:0}
  .nav{display:flex;flex-wrap:wrap;gap:4px}
  .nav a{padding:6px 10px;font-size:13px}
  .side .note{display:none}
  .hero{flex-direction:column;min-height:0}
  .hero .globe{display:none}
  main{padding:18px 16px 40px}
  h1{font-size:26px}
}
@media (max-width:480px){
  .stats{gap:10px}
  .stat b{font-size:20px}
  .btn{width:100%;justify-content:center}
  .legend{grid-template-columns:1fr 1fr}
}
</style>
</head>
<body>
<div class="app">
<aside class="side">
  <img src="logo.png" alt="Lingo Ledger">
  <nav class="nav" aria-label="Atlases">
    <a href="./" aria-current="page"><span class="dotn"></span>Certified Translator Atlas</a>
    <a href="charity"><span class="dotn" style="background:#b79fe6"></span>Charity Registration Atlas</a>
    <a href="startups"><span class="dotn" style="background:#d6c8f5"></span>OpenStartup Atlas</a>
  </nav>
  <p class="note">Credential data is compiled from public sources and is not legal advice. Confirm with the credential body or the court before a filing.</p>
</aside>

<main>
  <section class="hero">
    <img class="globe" src="globe.png" alt="">
    <div>
      <p class="eyebrow">Global translation &amp; interpreting</p>
      <h1>Certified Translator Atlas</h1>
      <p class="lead">How certified translators and interpreters are credentialed in each country, who grants the credential, and whether it is used for official work.</p>
    </div>
    <a class="btn" href="credentials_by_country.csv" download>Download CSV</a>
  </section>

  <section class="stats" aria-label="Summary">
    <div class="stat"><i>#</i><div><b id="t-all">0</b><span>Countries and territories</span></div></div>
    <div class="stat"><i>✓</i><div><b id="t-sourced">0</b><span>Sourced</span></div></div>
    <div class="stat"><i>◐</i><div><b id="t-partial">0</b><span>Partial</span></div></div>
    <div class="stat"><i>○</i><div><b id="t-nyr">0</b><span>Not yet researched</span></div></div>
    <div class="stat"><i>⚖</i><div><b id="t-gov">0</b><span>Verified for government use</span></div></div>
  </section>

  <div class="grid">
    <section class="card" aria-label="World map">
      <div class="card-head">
        <div>
          <h2>Global credential coverage</h2>
          <p class="sub">Click a country to see its credential body, sources and open questions.</p>
        </div>
      </div>
      <div class="mapbox">
        <svg id="map" viewBox="0 0 960 500" role="img" aria-label="World map coloured by credential model"></svg>
        <div class="zoom" aria-label="Map zoom">
          <button type="button" id="zin" aria-label="Zoom in">+</button>
          <button type="button" id="zout" aria-label="Zoom out">−</button>
          <button type="button" id="zreset" aria-label="Reset map">⌖</button>
        </div>
      </div>
      <div class="legend" id="legend"></div>
    </section>

    <aside class="card" aria-label="Country panel">
      <h2>Select a country</h2>
      <p class="sub">Search by name, or click the map or a table row.</p>
      <div class="pick"><input id="pick" class="search" type="search" list="names" placeholder="Search country…" aria-label="Search country"></div>
      <datalist id="names"></datalist>
      <div id="detail"><p class="empty">Nothing selected yet.</p></div>
      <div class="sec">
        <h3>Credential models</h3>
        <div class="bars" id="bars-model"></div>
      </div>
      <div class="sec">
        <h3>Research status</h3>
        <div class="bars" id="bars-status"></div>
      </div>
    </aside>
  </div>

  <div class="toolbar">
    <input id="q" class="search" type="search" placeholder="Search country, credential body or credential" aria-label="Search table">
    <select id="cat" aria-label="Credential model"><option value="">All credential models</option></select>
    <select id="sort" aria-label="Sort"><option value="country">Sort: country A–Z</option><option value="status">Sort: status</option><option value="model">Sort: credential model</option></select>
  </div>
  <div class="chips" id="chips" role="group" aria-label="Filter by status"></div>
  <p class="count" id="count"></p>
  <div class="tablewrap">
    <table>
      <thead><tr><th>Country</th><th>Credential model</th><th>Credential body</th><th>Status</th><th>Government use</th></tr></thead>
      <tbody id="rows"></tbody>
    </table>
  </div>

  <footer>
    <p><b>Status.</b> <span class="badge b-sourced">sourced</span> the credential body and at least one official or association source were found in a search. <span class="badge b-partial">partial</span> the body is named but the lookup or government rules were not verified. <span class="badge b-nyr">not yet researched</span> no usable source was found yet. Sources were not fully re-verified.</p>
    <p><b>Government use.</b> "Verified" means the source says certified or sworn translations are required or accepted for official use. Anything else is shown as not verified.</p>
    <p>Data: <a href="credentials_by_country.csv">credentials_by_country.csv</a> in the Lingo Ledger repository. Map: world-atlas (Natural Earth 1:50m) via jsDelivr; D3 via cdnjs.</p>
  </footer>
</main>
</div>
<script id="data" type="application/json">__DATA__</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"></script>
<script>
const ROWS = JSON.parse(document.getElementById("data").textContent).map(r => ({
  ...r,
  gov: !/^not verified/i.test((r["Used for government work"] || "").trim()),
}));
const COLORS = {national:"var(--national)",licence:"var(--licence)",court:"var(--court)",provincial:"var(--provincial)",association:"var(--association)",none:"var(--none)"};
const LABELS = {national:"National government",licence:"Government licence",court:"Court appointment",provincial:"Provincial",association:"Professional association",none:"Not verified or not researched"};
const STATUSES = ["sourced","partial","not yet researched"];
const STATUS_CLASS = {sourced:"b-sourced",partial:"b-partial","not yet researched":"b-nyr"};
const STATUS_LABEL = s => s[0].toUpperCase() + s.slice(1);
const byGeo = new Map(ROWS.map(r => [r.geo_name, r]));
const byName = new Map(ROWS.map(r => [r.Country.toLowerCase(), r]));
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const count = fn => ROWS.filter(fn).length;
const state = {q: "", cat: "", status: "", sort: "country", selected: null};
const cssVar = k => getComputedStyle(document.documentElement).getPropertyValue("--" + k).trim();

// Summary numbers
document.getElementById("t-all").textContent = ROWS.length;
document.getElementById("t-sourced").textContent = count(r => r.Status === "sourced");
document.getElementById("t-partial").textContent = count(r => r.Status === "partial");
document.getElementById("t-nyr").textContent = count(r => r.Status === "not yet researched");
document.getElementById("t-gov").textContent = count(r => r.gov);

// Legend with real counts
document.getElementById("legend").innerHTML = Object.keys(LABELS).map(k =>
  `<span><i style="--c:${COLORS[k]}"></i><div>${esc(LABELS[k])}<em>(${count(r => r.category === k)})</em></div></span>`).join("");

// Filters and datalist
const catSel = document.getElementById("cat");
Object.keys(LABELS).forEach(k => catSel.insertAdjacentHTML("beforeend", `<option value="${k}">${esc(LABELS[k])}</option>`));
document.getElementById("names").innerHTML = ROWS.map(r => `<option value="${esc(r.Country)}"></option>`).join("");
const chipWrap = document.getElementById("chips");
[["", "All"], ...STATUSES.map(s => [s, STATUS_LABEL(s)])].forEach(([val, label]) => {
  const b = document.createElement("button");
  b.className = "chip"; b.type = "button"; b.dataset.status = val; b.textContent = label;
  b.setAttribute("aria-pressed", val === state.status ? "true" : "false");
  b.addEventListener("click", () => {
    state.status = val;
    chipWrap.querySelectorAll(".chip").forEach(c => c.setAttribute("aria-pressed", c.dataset.status === val ? "true" : "false"));
    renderRows();
  });
  chipWrap.appendChild(b);
});

// Breakdown bars
function bars(id, items) {
  const max = Math.max(1, ...items.map(i => i.n));
  document.getElementById(id).innerHTML = items.map(i =>
    `<div class="bar"><span class="lbl">${i.dot ? `<i class="dot" style="--c:${i.dot}"></i>` : ""}<span>${esc(i.label)}</span></span>` +
    `<div class="track"><div class="fill" style="--c:${i.color};width:${(100 * i.n / max).toFixed(1)}%"></div></div>` +
    `<em>${i.n}</em></div>`).join("");
}
function renderBreakdown() {
  bars("bars-model", Object.keys(LABELS).map(k => ({label: LABELS[k], n: count(r => r.category === k), color: `var(--${k})`, dot: `var(--${k})`})));
  bars("bars-status", STATUSES.map(s => ({label: STATUS_LABEL(s), n: count(r => r.Status === s), color: "var(--accent-2)"})));
}

// Country detail
function statusBadge(s) { return `<span class="badge ${STATUS_CLASS[s] || ""}">${esc(s)}</span>`; }
function show(r) {
  if (!r) return;
  state.selected = r.Country;
  const fields = [["Credential model", r.Model], ["Credential body", r["Credential body"]], ["Credentials", r.Credentials],
    ["Used for government work", r["Used for government work"]], ["Official search or register", r["Official search or register"]],
    ["Sources", r.Sources], ["Notes", r.Notes]];
  document.getElementById("detail").innerHTML = `<h2>${esc(r.Country)}</h2>
    <div class="meta">${statusBadge(r.Status)}<span class="badge"><i class="dot" style="--c:${COLORS[r.category]};display:inline-block;margin-right:6px"></i>${esc(LABELS[r.category])}</span></div>
    <dl>` + fields.filter(([, v]) => v && String(v).trim()).map(([k, v]) => {
      const val = /^https?:/.test(v) ? `<a href="${esc(v)}" rel="noopener">${esc(v)}</a>` : esc(v);
      return `<dt>${k}</dt><dd>${val}</dd>`;
    }).join("") + `</dl>
    <p><button class="btn ghost" type="button" id="clear" style="margin-top:12px;padding:8px 14px">Clear selection</button></p>`;
  document.getElementById("clear").addEventListener("click", clearSelection);
  document.getElementById("pick").value = "";
  highlight();
}
function clearSelection() {
  state.selected = null;
  document.getElementById("detail").innerHTML = `<p class="empty">Nothing selected yet.</p>`;
  highlight();
}
function highlight() {
  document.querySelectorAll("path.country").forEach(p => p.classList.toggle("sel", !!state.selected && p.__name === (byName.get(state.selected.toLowerCase()) || {}).geo_name));
  document.querySelectorAll("tr.row").forEach(tr => tr.classList.toggle("sel", tr.dataset.c === state.selected));
}

// Search box: pick a country by exact name
document.getElementById("pick").addEventListener("change", e => {
  const r = byName.get(e.target.value.trim().toLowerCase());
  if (r) show(r);
});

// Table
const order = {sourced: 0, partial: 1, "not yet researched": 2};
function filtered() {
  const q = state.q.trim().toLowerCase();
  const hits = ROWS.filter(r => (!state.cat || r.category === state.cat) && (!state.status || r.Status === state.status) &&
    (!q || [r.Country, r["Credential body"], r.Credentials, r.Model].join(" ").toLowerCase().includes(q)));
  const key = {
    country: (a, b) => a.Country.localeCompare(b.Country),
    status: (a, b) => (order[a.Status] - order[b.Status]) || a.Country.localeCompare(b.Country),
    model: (a, b) => LABELS[a.category].localeCompare(LABELS[b.category]) || a.Country.localeCompare(b.Country),
  }[state.sort];
  return hits.sort(key);
}
function renderRows() {
  const hits = filtered();
  document.getElementById("count").textContent = `Showing ${hits.length} of ${ROWS.length} countries`;
  document.getElementById("rows").innerHTML = hits.length ? hits.map(r =>
    `<tr class="row" tabindex="0" data-c="${esc(r.Country)}">` +
    `<td class="nowrap"><b>${esc(r.Country)}</b></td>` +
    `<td><span class="dot" style="--c:${COLORS[r.category]};margin-right:6px"></span>${esc(LABELS[r.category])}</td>` +
    `<td class="body">${esc(r["Credential body"]) || "<span style='color:#999'>none named</span>"}</td>` +
    `<td>${statusBadge(r.Status)}</td>` +
    `<td>${r.gov ? "Verified" : "Not verified"}</td></tr>`).join("")
    : `<tr><td colspan="5" class="empty-table">No countries match these filters.</td></tr>`;
  highlight();
}
const tbody = document.getElementById("rows");
tbody.addEventListener("click", e => {
  const tr = e.target.closest("tr.row"); if (!tr) return;
  show(ROWS.find(r => r.Country === tr.dataset.c));
});
tbody.addEventListener("keydown", e => {
  const tr = e.target.closest("tr.row"); if (!tr || (e.key !== "Enter" && e.key !== " ")) return;
  e.preventDefault(); show(ROWS.find(r => r.Country === tr.dataset.c));
});
document.getElementById("q").addEventListener("input", e => { state.q = e.target.value; renderRows(); });
catSel.addEventListener("change", e => { state.cat = e.target.value; renderRows(); });
document.getElementById("sort").addEventListener("change", e => { state.sort = e.target.value; renderRows(); });

renderBreakdown();
renderRows();

// Map with zoom controls
const zoom = d3.zoom().scaleExtent([1, 8]).on("zoom", e => d3.select("#world").attr("transform", e.transform));
Promise.all([
  fetch("https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json").then(r => r.json()),
]).then(([world]) => {
  const svg = d3.select("#map").call(zoom);
  const projection = d3.geoNaturalEarth1().fitSize([960, 500], {type: "Sphere"});
  const path = d3.geoPath(projection);
  const countries = topojson.feature(world, world.objects.countries).features;
  const g = svg.append("g").attr("id", "world");
  g.selectAll("path.country").data(countries).join("path")
    .attr("class", "country").attr("d", path)
    .each(function (d) { this.__name = d.properties.name; })
    .attr("fill", d => { const r = byGeo.get(d.properties.name); return r ? COLORS[r.category] : "var(--none)"; })
    .on("click", (e, d) => { const r = byGeo.get(d.properties.name); if (r) show(r); })
    .append("title").text(d => d.properties.name);
  d3.select("#zin").on("click", () => svg.transition().call(zoom.scaleBy, 1.6));
  d3.select("#zout").on("click", () => svg.transition().call(zoom.scaleBy, 1 / 1.6));
  d3.select("#zreset").on("click", () => svg.transition().call(zoom.transform, d3.zoomIdentity));
}).catch(() => {
  document.getElementById("map").insertAdjacentHTML("afterend", '<p class="sub">Map failed to load. The table below still works.</p>');
});
</script>
</body>
</html>
"""


def build() -> Path:
    rows = load_rows()
    # Only embed the fields the page reads.
    data = [{k: v for k, v in r.items()} for r in rows]
    SITE.mkdir(exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out = SITE / "index.html"
    out.write_text(PAGE.replace("__DATA__", payload), encoding="utf-8")
    shutil.copyfile(CSV_PATH, SITE / "credentials_by_country.csv")
    return out


if __name__ == "__main__":
    print(build())

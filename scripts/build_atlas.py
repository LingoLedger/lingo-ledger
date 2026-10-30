#!/usr/bin/env python3
"""Build site/index.html: a world map of certified translator and interpreter credentials.

Reads data/credentials_by_country.csv and writes:
  site/index.html          one self-contained page (data embedded)
  site/credentials_by_country.csv   the same data for download

D3 and topojson-client load from cdnjs; world geometry loads from jsdelivr
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
        r["category"] = category(r["Model"])
        r["geo_name"] = ALIAS.get(r["Country"], r["Country"])
    return rows


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Certified Translator Atlas · Lingo Ledger</title>
<meta name="description" content="How certified translators and interpreters are credentialed in each country, with sources.">
<style>
:root{--bg:#f7f7fb;--fg:#1d1d28;--muted:#666a7a;--card:#ffffff;--line:#dcdde6;--accent:#1d5d86;
--national:#1d5d86;--licence:#6f42c1;--court:#cf6529;--provincial:#2c8a68;--association:#c79a1e;--none:#c9ccd6}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15161c;--fg:#e8e8ef;--muted:#a0a4b5;--card:#1e2028;--line:#33354a;--accent:#7fb8e0;--none:#3a3d4d}}
:root[data-theme="dark"]{--bg:#15161c;--fg:#e8e8ef;--muted:#a0a4b5;--card:#1e2028;--line:#33354a;--accent:#7fb8e0;--none:#3a3d4d}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
header,main{max-width:1100px;margin:0 auto;padding:16px}
h1{font-size:1.6rem;margin:.2rem 0}
p.lead{color:var(--muted);margin:.2rem 0 1rem}
.grid{display:grid;grid-template-columns:2fr 1fr;gap:16px}
@media (max-width:820px){.grid{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
#map{width:100%;height:auto}
path.country{stroke:var(--bg);stroke-width:.4;cursor:pointer}
path.country:hover{opacity:.8}
.legend{display:flex;flex-wrap:wrap;gap:12px;font-size:.9rem;color:var(--muted);margin-top:8px}
.legend span::before{content:"";display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px;background:var(--c)}
.controls{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
select,input{font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
input{flex:1;min-width:180px}
table{width:100%;border-collapse:collapse;font-size:.92rem}
th,td{text-align:left;padding:6px;border-bottom:1px solid var(--line);vertical-align:top}
tr.row{cursor:pointer}
tr.row:hover{background:color-mix(in srgb,var(--accent) 10%,transparent)}
.pill{display:inline-block;font-size:.78rem;padding:1px 8px;border-radius:99px;background:var(--line)}
#detail h2{font-size:1.2rem;margin:0 0 6px}
#detail dt{font-weight:600;margin-top:8px;color:var(--muted);font-size:.85rem}
#detail dd{margin:0}
.scroll{max-height:560px;overflow:auto}
footer{color:var(--muted);font-size:.85rem;max-width:1100px;margin:0 auto;padding:16px}
a{color:var(--accent)}
</style>
</head>
<body>
<header>
  <h1>Certified Translator Atlas</h1>
  <p class="lead">How certified translators and interpreters are credentialed in each country. Click a country for its credential body, its sources, and what is still unverified. <a href="credentials_by_country.csv" download>Download CSV</a></p>
</header>
<main>
  <div class="grid">
    <section class="card">
      <svg id="map" viewBox="0 0 960 500" role="img" aria-label="World map coloured by credential model"></svg>
      <div class="legend" id="legend"></div>
    </section>
    <section class="card" id="detail"><p class="lead">Select a country on the map or in the table.</p></section>
  </div>
  <div class="controls">
    <input id="q" type="search" placeholder="Search country, body or credential">
    <select id="cat"><option value="">All credential models</option></select>
    <select id="stat"><option value="">All statuses</option></select>
  </div>
  <section class="card scroll">
    <table>
      <thead><tr><th>Country</th><th>Credential model</th><th>Credential body</th><th>Status</th></tr></thead>
      <tbody id="rows"></tbody>
    </table>
  </section>
</main>
<footer>
  <p><b>Status.</b> <i>sourced</i> means the credential body and at least one official or association source were found in a search. <i>partial</i> means the body is named but the lookup or government rules were not verified. <i>not yet researched</i> means no research has been done for that country. Sources were not fully re-verified.</p>
  <p><b>Not legal advice.</b> Confirm with the credential body or the court before relying on any credential for a filing.</p>
  <p>Data: <a href="credentials_by_country.csv">credentials_by_country.csv</a> in the Lingo Ledger repository. Map: world-atlas (Natural Earth 1:50m) via jsDelivr; D3 via cdnjs.</p>
</footer>
<script id="data" type="application/json">__DATA__</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/topojson-client/3.1.0/topojson-client.min.js"></script>
<script>
const ROWS = JSON.parse(document.getElementById("data").textContent);
const COLORS = {national:"var(--national)",licence:"var(--licence)",court:"var(--court)",provincial:"var(--provincial)",association:"var(--association)",none:"var(--none)"};
const LABELS = {national:"National government",licence:"Government licence",court:"Court appointment",provincial:"Provincial",association:"Professional association",none:"Not yet researched"};
const byGeo = new Map(ROWS.map(r => [r.geo_name, r]));
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

document.getElementById("legend").innerHTML = Object.keys(LABELS)
  .map(k => `<span style="--c:${COLORS[k]}">${LABELS[k]}</span>`).join("");
const catSel = document.getElementById("cat");
Object.keys(LABELS).forEach(k => catSel.insertAdjacentHTML("beforeend", `<option value="${k}">${LABELS[k]}</option>`));
const statSel = document.getElementById("stat");
[...new Set(ROWS.map(r => r.Status))].sort().forEach(s => statSel.insertAdjacentHTML("beforeend", `<option value="${esc(s)}">${esc(s)}</option>`));

function show(r) {
  const fields = [["Credential model", r.Model], ["Credential body", r["Credential body"]], ["Credentials", r.Credentials],
    ["Used for government work", r["Used for government work"]], ["Official search or register", r["Official search or register"]],
    ["Sources", r.Sources], ["Status", r.Status], ["Notes", r.Notes]];
  document.getElementById("detail").innerHTML = `<h2>${esc(r.Country)}</h2><dl>` +
    fields.filter(([, v]) => v && v.trim()).map(([k, v]) => {
      const val = /^https?:/.test(v) ? `<a href="${esc(v)}" rel="noopener">${esc(v)}</a>` : esc(v);
      return `<dt>${k}</dt><dd>${val}</dd>`;
    }).join("") + "</dl>";
}

function renderRows() {
  const q = document.getElementById("q").value.trim().toLowerCase();
  const c = catSel.value, s = statSel.value;
  const hits = ROWS.filter(r => (!c || r.category === c) && (!s || r.Status === s) &&
    (!q || [r.Country, r["Credential body"], r.Credentials, r.Model].join(" ").toLowerCase().includes(q)));
  document.getElementById("rows").innerHTML = hits.map(r =>
    `<tr class="row" data-c="${esc(r.Country)}"><td>${esc(r.Country)}</td><td><span class="pill">${esc(r.Model)}</span></td><td>${esc(r["Credential body"])}</td><td>${esc(r.Status)}</td></tr>`).join("");
}
document.getElementById("rows").addEventListener("click", e => {
  const tr = e.target.closest("tr.row"); if (!tr) return;
  show(ROWS.find(r => r.Country === tr.dataset.c));
});
["q","cat","stat"].forEach(id => document.getElementById(id).addEventListener("input", renderRows));
renderRows();

Promise.all([
  fetch("https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json").then(r => r.json()),
]).then(([world]) => {
  const svg = d3.select("#map");
  const projection = d3.geoNaturalEarth1().fitSize([960, 500], {type: "Sphere"});
  const path = d3.geoPath(projection);
  const countries = topojson.feature(world, world.objects.countries).features;
  svg.selectAll("path.country").data(countries).join("path")
    .attr("class", "country").attr("d", path)
    .attr("fill", d => { const r = byGeo.get(d.properties.name); return r ? COLORS[r.category] : "var(--none)"; })
    .on("click", (e, d) => { const r = byGeo.get(d.properties.name); if (r) show(r); })
    .append("title").text(d => d.properties.name);
}).catch(() => {
  document.getElementById("map").insertAdjacentHTML("afterend", '<p class="lead">Map failed to load. The table below still works.</p>');
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

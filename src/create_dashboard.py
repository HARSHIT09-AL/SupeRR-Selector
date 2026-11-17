from pathlib import Path
from html import escape
import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUTPUT = ROOT / "dashboard" / "superrr_selector_dashboard.html"

batters = pd.read_csv(DATA / "batter_pressure_ratings.csv")
bowlers = pd.read_csv(DATA / "bowler_pressure_ratings.csv")

best_batter = batters.nlargest(1, "batting_pressure_score").iloc[0]
best_bowler = bowlers.nlargest(1, "bowling_pressure_score").iloc[0]

def make_chart(df, name, score, extra, label, color):
    d = df.nlargest(10, score).sort_values(score)
    fig = go.Figure(go.Bar(
        x=d[score], y=d[name], orientation="h",
        marker_color=color,
        text=d[score].round(1), textposition="outside",
        customdata=d[[extra]],
        hovertemplate="<b>%{y}</b><br>Score: %{x:.2f}<br>" +
                      label + ": %{customdata[0]}<extra></extra>"
    ))
    fig.add_vline(x=100, line_dash="dash", line_color="#829080",
                  annotation_text="Baseline 100")
    fig.update_layout(
        height=390, margin=dict(l=10, r=55, t=20, b=35),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color="#E8EEE7", size=11),
        showlegend=False, bargap=0.35,
        xaxis=dict(title="Pressure score", gridcolor="#26342D",
                   zeroline=False, color="#9BA99D"),
        yaxis=dict(showgrid=False, color="#E8EEE7")
    )
    return fig.to_html(full_html=False, include_plotlyjs="cdn",
                       config={"responsive": True})

batting_chart = make_chart(
    batters, "striker_name", "batting_pressure_score",
    "pressure_runs", "Pressure runs", "#C6F36B"
)
bowling_chart = make_chart(
    bowlers, "bowler_name", "bowling_pressure_score",
    "pressure_wickets", "Pressure wickets", "#55D6BE"
)

def make_rows(df, name, score, stat, stat_label):
    rows = ""
    for rank, (_, p) in enumerate(df.nlargest(10, score).iterrows(), 1):
        rows += (
            f'<tr><td class="rank">{rank:02d}</td>'
            f'<td class="player">{escape(str(p[name]))}</td>'
            f'<td class="score">{p[score]:.2f}</td>'
            f'<td>{p[stat]}</td></tr>'
        )
    return rows

batting_rows = make_rows(
    batters, "striker_name", "batting_pressure_score",
    "pressure_runs", "Runs"
)
bowling_rows = make_rows(
    bowlers, "bowler_name", "bowling_pressure_score",
    "pressure_wickets", "Wickets"
)

batter_json = batters[[
    "striker_name", "batting_pressure_score", "pressure_runs",
    "pressure_balls", "pressure_strike_rate"
]].to_json(orient="records")

bowler_json = bowlers[[
    "bowler_name", "bowling_pressure_score", "pressure_runs_conceded",
    "pressure_legal_balls", "pressure_wickets", "pressure_economy"
]].to_json(orient="records")

def options(df, col):
    return "".join(
        f'<option value="{escape(str(name), quote=True)}">'
        f'{escape(str(name))}</option>'
        for name in sorted(df[col].dropna().unique())
    )

batter_options = options(batters, "striker_name")
bowler_options = options(bowlers, "bowler_name")

html = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SupeRR Selector | Cricket Intelligence</title>
<style>
:root {
 --bg:#090D0A; --surface:#111813; --surface2:#17221A;
 --line:#29362D; --text:#F1F5EE; --muted:#91A093;
 --lime:#C6F36B; --teal:#55D6BE; --red:#F28B82;
}
* {box-sizing:border-box}
html {scroll-behavior:smooth}
body {margin:0;background:var(--bg);color:var(--text);
 font-family:Inter,Arial,Helvetica,sans-serif}
button,input,select {font:inherit}
.topbar {height:68px;padding:0 5%;display:flex;align-items:center;
 justify-content:space-between;border-bottom:1px solid var(--line);
 background:#0D130F;position:sticky;top:0;z-index:20}
.brand {font-size:19px;font-weight:900;letter-spacing:1.5px}
.brand span {color:var(--lime)}
.status {font-size:10px;letter-spacing:1.4px;color:var(--lime);
 border:1px solid #465B32;padding:9px 12px;border-radius:3px}
.nav {display:flex;gap:22px}
.nav a {color:var(--muted);text-decoration:none;font-size:12px}
.nav a:hover {color:var(--lime)}
.container {max-width:1500px;margin:auto;padding:42px 5%}
.eyebrow {color:var(--lime);font-size:10px;letter-spacing:3px;
 font-weight:800;margin-bottom:16px}
.hero {display:grid;grid-template-columns:1.5fr 0.8fr;gap:30px;
 align-items:center;margin-bottom:38px}
h1 {font-size:clamp(40px,6vw,76px);line-height:.92;
 letter-spacing:-3px;margin:0;font-weight:950}
h1 span {color:var(--lime)}
.subtitle {color:var(--muted);font-size:14px;line-height:1.8;
 max-width:610px;margin-top:20px}
.spotlight {background:linear-gradient(135deg,#17251A,#101713);
 border:1px solid #3A4A35;padding:24px;position:relative;overflow:hidden}
.spotlight:after {content:"";position:absolute;width:160px;height:160px;
 border:1px solid #526A3C;border-radius:50%;right:-65px;top:-65px;
 box-shadow:0 0 0 20px #C6F36B08,0 0 0 40px #C6F36B05}
.spotlight .label {font-size:10px;letter-spacing:2px;color:var(--lime)}
.spotlight h2 {font-size:27px;margin:15px 0 6px}
.spotlight .score {font-size:46px;color:var(--lime);font-weight:900}
.spotlight p {font-size:12px;color:var(--muted);margin:5px 0}
.kpis {display:grid;grid-template-columns:repeat(4,1fr);gap:13px;
 margin-bottom:40px}
.kpi {background:var(--surface);border:1px solid var(--line);
 padding:21px;min-height:120px;position:relative}
.kpi:after {content:"";position:absolute;bottom:0;left:0;width:100%;
 height:3px;background:var(--lime)}
.kpi.teal:after {background:var(--teal)}
.kpi-label {font-size:9px;letter-spacing:1.5px;color:var(--muted)}
.kpi-value {font-size:30px;font-weight:900;margin-top:16px}
.kpi-value.lime {color:var(--lime)}
.kpi-value.teal {color:var(--teal)}
.section {margin-top:45px}
.section-head {display:flex;justify-content:space-between;align-items:end;
 gap:15px;margin-bottom:16px}
.section-head h2 {font-size:20px;margin:0;letter-spacing:.2px}
.section-head p {font-size:10px;color:var(--muted);letter-spacing:1px;margin:0}
.chart-grid,.table-grid,.compare-grid {
 display:grid;grid-template-columns:1fr 1fr;gap:15px}
.panel {background:var(--surface);border:1px solid var(--line);
 border-radius:5px;padding:18px;min-width:0}
.panel-title {font-size:12px;font-weight:800;letter-spacing:1px;
 margin:4px 4px 8px}
.panel-sub {font-size:10px;color:var(--muted);margin:0 4px 10px}
.table-wrap {overflow-x:auto}
table {width:100%;border-collapse:collapse;font-size:12px}
th {font-size:9px;letter-spacing:1px;color:var(--muted);
 text-align:left;padding:13px 9px;border-bottom:1px solid var(--line)}
td {padding:13px 9px;border-bottom:1px solid #202B23}
.rank {color:var(--muted)}
.player {font-weight:700}
.score {color:var(--lime);font-weight:800}
.searchbar {width:100%;background:#0B110D;color:var(--text);
 border:1px solid var(--line);padding:13px 14px;outline:none;
 border-radius:4px;margin:8px 0 14px}
.searchbar:focus,select:focus {border-color:var(--lime)}
.controls {display:grid;grid-template-columns:1fr 1fr;gap:12px}
select {width:100%;background:#0B110D;color:var(--text);
 border:1px solid var(--line);padding:12px;border-radius:4px;outline:none}
.compare-result {margin-top:16px;display:grid;grid-template-columns:1fr 1fr;
 gap:10px}
.person {background:var(--surface2);padding:16px;border:1px solid var(--line)}
.person h3 {font-size:14px;margin:0 0 14px}
.person .big {font-size:30px;font-weight:900;color:var(--lime)}
.person p {font-size:11px;color:var(--muted);margin:7px 0}
.compare-note {font-size:10px;color:var(--muted);margin-top:12px}
.method {background:var(--surface2);border:1px solid var(--line);
 padding:22px;color:var(--muted);font-size:12px;line-height:1.9}
.method strong {color:var(--text)}
.footer {border-top:1px solid var(--line);padding:25px 5%;
 color:var(--muted);font-size:10px;letter-spacing:1.4px;
 display:flex;justify-content:space-between;gap:15px}
.pill {display:inline-block;color:var(--lime);border:1px solid #465B32;
 padding:5px 8px;font-size:9px;letter-spacing:1px}
@media(max-width:900px) {
 .hero {grid-template-columns:1fr}
 .kpis {grid-template-columns:repeat(2,1fr)}
 .chart-grid,.table-grid,.compare-grid {grid-template-columns:1fr}
 .nav {display:none}
}
@media(max-width:520px) {
 .container {padding:28px 4%}
 .topbar {padding:0 4%}
 .kpis {gap:8px}
 .kpi {padding:14px}
 .kpi-value {font-size:23px}
 .controls,.compare-result {grid-template-columns:1fr}
 .footer {flex-direction:column}
}
</style>
</head>
<body>
<header class="topbar">
 <div class="brand">SUPERR<span> SELECTOR</span></div>
 <nav class="nav">
  <a href="#overview">OVERVIEW</a>
  <a href="#rankings">RANKINGS</a>
  <a href="#workspace">ANALYST WORKSPACE</a>
  <a href="#methodology">METHODOLOGY</a>
 </nav>
 <div class="status">● ENGINE ACTIVE</div>
</header>

<main class="container" id="overview">
 <div class="hero">
  <div>
   <div class="eyebrow">CRICKET PERFORMANCE INTELLIGENCE / 01</div>
   <h1>THE PRESSURE<br><span>INDEX.</span></h1>
   <p class="subtitle">A ball-by-ball performance intelligence platform.
   Discover the batters and bowlers who deliver when the match situation
   gets difficult. Built to turn cricket data into selection insight.</p>
   <span class="pill">T20I + IPL · 2022 ONWARD</span>
  </div>
  <div class="spotlight">
   <div class="label">#1 BATTER / CURRENT DATASET</div>
   <h2>__BEST_BATTER__</h2>
   <div class="score">__BATTER_SCORE__</div>
   <p>PRESSURE PERFORMANCE SCORE</p>
   <p>__BATTER_RUNS__ pressure runs · __BATTER_BALLS__ pressure balls</p>
  </div>
 </div>

 <section class="kpis">
  <div class="kpi"><div class="kpi-label">QUALIFIED BATTERS</div>
   <div class="kpi-value">__BATTER_COUNT__</div></div>
  <div class="kpi teal"><div class="kpi-label">QUALIFIED BOWLERS</div>
   <div class="kpi-value teal">__BOWLER_COUNT__</div></div>
  <div class="kpi"><div class="kpi-label">TOP BATTING SCORE</div>
   <div class="kpi-value lime">__BATTER_SCORE__</div></div>
  <div class="kpi teal"><div class="kpi-label">TOP BOWLING SCORE</div>
   <div class="kpi-value teal">__BOWLER_SCORE__</div></div>
 </section>

 <section class="section" id="rankings">
  <div class="section-head"><h2>PERFORMANCE LEADERS</h2>
   <p>TOP 10 / PRESSURE SCORE</p></div>
  <div class="chart-grid">
   <div class="panel"><div class="panel-title">01 / BATTING UNDER PRESSURE</div>
    <div class="panel-sub">Higher score indicates stronger pressure batting performance.</div>
    __BATTING_CHART__
   </div>
   <div class="panel"><div class="panel-title">02 / BOWLING UNDER PRESSURE</div>
    <div class="panel-sub">Higher score indicates stronger pressure bowling performance.</div>
    __BOWLING_CHART__
   </div>
  </div>
 </section>

 <section class="section">
  <div class="section-head"><h2>THE LEADERBOARDS</h2>
   <p>TOP 10 QUALIFIED PLAYERS</p></div>
  <div class="table-grid">
   <div class="panel"><div class="panel-title">BATTING LEADERS</div>
    <div class="table-wrap"><table><thead><tr>
     <th>#</th><th>PLAYER</th><th>SCORE</th><th>RUNS</th>
    </tr></thead><tbody>__BATTING_ROWS__</tbody></table></div>
   </div>
   <div class="panel"><div class="panel-title">BOWLING LEADERS</div>
    <div class="table-wrap"><table><thead><tr>
     <th>#</th><th>PLAYER</th><th>SCORE</th><th>WICKETS</th>
    </tr></thead><tbody>__BOWLING_ROWS__</tbody></table></div>
   </div>
  </div>
 </section>

 <section class="section" id="workspace">
  <div class="section-head"><h2>ANALYST WORKSPACE</h2>
   <p>SEARCH · EXPLORE · COMPARE</p></div>
  <div class="table-grid">
   <div class="panel">
    <div class="panel-title">BATTER EXPLORER</div>
    <p class="panel-sub">Search across all qualified batters.</p>
    <input class="searchbar" id="batterSearch" placeholder="Search batter name...">
    <div class="table-wrap"><table><thead><tr>
     <th>PLAYER</th><th>SCORE</th><th>RUNS</th><th>BALLS</th>
    </tr></thead><tbody id="batterResults"></tbody></table></div>
    <p class="compare-note" id="batterCount"></p>
   </div>
   <div class="panel">
    <div class="panel-title">BOWLER EXPLORER</div>
    <p class="panel-sub">Search across all qualified bowlers.</p>
    <input class="searchbar" id="bowlerSearch" placeholder="Search bowler name...">
    <div class="table-wrap"><table><thead><tr>
     <th>PLAYER</th><th>SCORE</th><th>WICKETS</th><th>ECONOMY</th>
    </tr></thead><tbody id="bowlerResults"></tbody></table></div>
    <p class="compare-note" id="bowlerCount"></p>
   </div>
  </div>

  <div class="section-head" style="margin-top:28px">
   <h2>PLAYER COMPARISON</h2><p>SIDE-BY-SIDE PERFORMANCE</p>
  </div>
  <div class="compare-grid">
   <div class="panel">
    <div class="panel-title">BATTER VS BATTER</div>
    <div class="controls">
     <select id="batterA">__BATTER_OPTIONS__</select>
     <select id="batterB">__BATTER_OPTIONS__</select>
    </div>
    <div class="compare-result" id="batterCompare"></div>
    <div class="compare-note">Comparison uses the generated batting pressure ratings.</div>
   </div>
   <div class="panel">
    <div class="panel-title">BOWLER VS BOWLER</div>
    <div class="controls">
     <select id="bowlerA">__BOWLER_OPTIONS__</select>
     <select id="bowlerB">__BOWLER_OPTIONS__</select>
    </div>
    <div class="compare-result" id="bowlerCompare"></div>
    <div class="compare-note">Comparison uses the generated bowling pressure ratings.</div>
   </div>
  </div>
 </section>

 <section class="section" id="methodology">
  <div class="section-head"><h2>UNDER THE HOOD</h2>
   <p>SCORING METHODOLOGY</p></div>
  <div class="method">
   <strong>THE PRESSURE INDEX / REFERENCE SCORE: 100</strong><br>
   Scores above 100 indicate performance above the non-pressure comparison
   baseline, adjusted for sample reliability. Batting ratings incorporate
   pressure runs, balls faced and strike rate. Bowling ratings incorporate
   pressure runs conceded, legal balls, wickets and economy.
   <br><br>
   <strong>QUALIFICATION:</strong> Minimum 30 pressure balls for batters and
   30 pressure legal balls for bowlers. Pressure is evaluated before each
   delivery. Super Overs are excluded from regular pressure rankings.
   <br><br>
   <strong>DATA SCOPE:</strong> T20 Internationals and IPL matches from 2022 onward.
  </div>
 </section>
</main>
<footer class="footer">
 <span>SUPERR SELECTOR · CRICKET ANALYTICS</span>
 <span>PYTHON · PANDAS · PLOTLY</span>
</footer>

<script>
const BATTERS = __BATTER_JSON__;
const BOWLERS = __BOWLER_JSON__;

function safe(value) {
 return String(value ?? "").replace(/[&<>"']/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

function renderBatters(query="") {
 const filtered = BATTERS.filter(p =>
  p.striker_name.toLowerCase().includes(query.toLowerCase())
 ).sort((a,b) => b.batting_pressure_score-a.batting_pressure_score);
 document.getElementById("batterResults").innerHTML =
  filtered.slice(0,100).map(p => `<tr>
   <td class="player">${safe(p.striker_name)}</td>
   <td class="score">${Number(p.batting_pressure_score).toFixed(2)}</td>
   <td>${p.pressure_runs}</td><td>${p.pressure_balls}</td>
  </tr>`).join("");
 document.getElementById("batterCount").textContent =
  `Showing ${Math.min(filtered.length,100)} of ${filtered.length} matching batters`;
}

function renderBowlers(query="") {
 const filtered = BOWLERS.filter(p =>
  p.bowler_name.toLowerCase().includes(query.toLowerCase())
 ).sort((a,b) => b.bowling_pressure_score-a.bowling_pressure_score);
 document.getElementById("bowlerResults").innerHTML =
  filtered.slice(0,100).map(p => `<tr>
   <td class="player">${safe(p.bowler_name)}</td>
   <td class="score">${Number(p.bowling_pressure_score).toFixed(2)}</td>
   <td>${p.pressure_wickets}</td>
   <td>${Number(p.pressure_economy).toFixed(2)}</td>
  </tr>`).join("");
 document.getElementById("bowlerCount").textContent =
  `Showing ${Math.min(filtered.length,100)} of ${filtered.length} matching bowlers`;
}

function batterCard(p) {
 return `<div class="person">
  <h3>${safe(p.striker_name)}</h3>
  <div class="big">${Number(p.batting_pressure_score).toFixed(2)}</div>
  <p>PRESSURE SCORE</p>
  <p>Runs: <b>${p.pressure_runs}</b></p>
  <p>Balls: <b>${p.pressure_balls}</b></p>
  <p>Strike rate: <b>${Number(p.pressure_strike_rate).toFixed(2)}</b></p>
 </div>`;
}

function bowlerCard(p) {
 return `<div class="person">
  <h3>${safe(p.bowler_name)}</h3>
  <div class="big">${Number(p.bowling_pressure_score).toFixed(2)}</div>
  <p>PRESSURE SCORE</p>
  <p>Wickets: <b>${p.pressure_wickets}</b></p>
  <p>Legal balls: <b>${p.pressure_legal_balls}</b></p>
  <p>Economy: <b>${Number(p.pressure_economy).toFixed(2)}</b></p>
 </div>`;
}

function compareBatters() {
 const a = BATTERS.find(p => p.striker_name === document.getElementById("batterA").value);
 const b = BATTERS.find(p => p.striker_name === document.getElementById("batterB").value);
 document.getElementById("batterCompare").innerHTML =
  a && b ? batterCard(a) + batterCard(b) : "";
}

function compareBowlers() {
 const a = BOWLERS.find(p => p.bowler_name === document.getElementById("bowlerA").value);
 const b = BOWLERS.find(p => p.bowler_name === document.getElementById("bowlerB").value);
 document.getElementById("bowlerCompare").innerHTML =
  a && b ? bowlerCard(a) + bowlerCard(b) : "";
}

document.getElementById("batterSearch").addEventListener("input", e => renderBatters(e.target.value));
document.getElementById("bowlerSearch").addEventListener("input", e => renderBowlers(e.target.value));
["batterA","batterB"].forEach(id =>
 document.getElementById(id).addEventListener("change", compareBatters));
["bowlerA","bowlerB"].forEach(id =>
 document.getElementById(id).addEventListener("change", compareBowlers));

renderBatters();
renderBowlers();
compareBatters();
compareBowlers();
</script>
</body>
</html>
"""

replacements = {
 "__BEST_BATTER__": escape(str(best_batter["striker_name"])),
 "__BATTER_SCORE__": f'{best_batter["batting_pressure_score"]:.2f}',
 "__BATTER_RUNS__": str(best_batter["pressure_runs"]),
 "__BATTER_BALLS__": str(best_batter["pressure_balls"]),
 "__BOWLER_SCORE__": f'{best_bowler["bowling_pressure_score"]:.2f}',
 "__BATTER_COUNT__": f"{len(batters):,}",
 "__BOWLER_COUNT__": f"{len(bowlers):,}",
 "__BATTING_CHART__": batting_chart,
 "__BOWLING_CHART__": bowling_chart,
 "__BATTING_ROWS__": batting_rows,
 "__BOWLING_ROWS__": bowling_rows,
 "__BATTER_OPTIONS__": batter_options,
 "__BOWLER_OPTIONS__": bowler_options,
 "__BATTER_JSON__": batter_json,
 "__BOWLER_JSON__": bowler_json,
}

for key, value in replacements.items():
    html = html.replace(key, value)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(html, encoding="utf-8")

print("SUPERR SELECTOR ANALYST DASHBOARD CREATED")
print(f"Qualified batters: {len(batters)}")
print(f"Qualified bowlers: {len(bowlers)}")
print(f"Saved to: {OUTPUT}")

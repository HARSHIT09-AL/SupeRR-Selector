from pathlib import Path
import pandas as pd
import json
import html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
SITE = ROOT / "dashboard" / "website"
ASSETS = SITE / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

batters = pd.read_csv(DATA / "batter_pressure_ratings.csv")
bowlers = pd.read_csv(DATA / "bowler_pressure_ratings.csv")

BATTER_COLUMNS = [
    "striker_name", "batting_pressure_score", "pressure_runs",
    "pressure_balls", "pressure_strike_rate"
]
BOWLER_COLUMNS = [
    "bowler_name", "bowling_pressure_score", "pressure_runs_conceded",
    "pressure_legal_balls", "pressure_wickets", "pressure_economy"
]

batters = batters[BATTER_COLUMNS].copy()
bowlers = bowlers[BOWLER_COLUMNS].copy()

(ASSETS / "data.js").write_text(
    "const BATTERS = " + batters.to_json(orient="records") + ";\n"
    "const BOWLERS = " + bowlers.to_json(orient="records") + ";\n",
    encoding="utf-8"
)

css = r"""
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700;800;900&display=swap');
:root {
 --bg:#0B100E; --panel:#121A16; --panel2:#19231D;
 --line:#2A382F; --white:#F3F1E8; --muted:#91A095;
 --lime:#D5F477; --orange:#FF875C; --teal:#65D7C0;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--white);
 font-family:'DM Sans',Arial,sans-serif}
a{color:inherit;text-decoration:none}
button,input,select{font:inherit}
.navbar{height:76px;padding:0 5%;display:flex;align-items:center;
 justify-content:space-between;border-bottom:1px solid var(--line);
 background:#0B100E;position:sticky;top:0;z-index:30}
.logo{font-weight:900;font-size:19px;letter-spacing:1.4px}
.logo span{color:var(--lime)}
.navlinks{display:flex;align-items:center;gap:25px}
.navlinks a{font-size:11px;color:var(--muted);letter-spacing:1px}
.navlinks a:hover,.navlinks a.active{color:var(--lime)}
.navlinks a.active{border-bottom:2px solid var(--lime);padding-bottom:9px}
.live{font:10px 'DM Mono',monospace;color:var(--lime);
 border:1px solid #53633B;padding:9px 12px}
.wrap{max-width:1450px;margin:auto;padding:55px 5% 75px}
.kicker{font:10px 'DM Mono',monospace;color:var(--lime);
 letter-spacing:2.5px;text-transform:uppercase}
h1{font-size:clamp(43px,7vw,88px);line-height:.94;
 letter-spacing:-4px;margin:18px 0;font-weight:900}
h1 em{color:var(--lime);font-style:normal}
h2{font-size:23px;letter-spacing:-.5px;margin:0}
h3{margin:0;font-size:15px}
.lead{max-width:620px;color:var(--muted);font-size:15px;line-height:1.8}
.hero{display:grid;grid-template-columns:1.35fr .75fr;gap:35px;
 align-items:center;margin-bottom:45px}
.feature{background:var(--panel);border:1px solid var(--line);
 padding:28px;position:relative;overflow:hidden}
.feature:after{content:"";position:absolute;width:190px;height:190px;
 border:1px solid #D5F47755;border-radius:50%;right:-80px;top:-85px;
 box-shadow:0 0 0 25px #D5F47709,0 0 0 50px #D5F47706}
.feature .name{font-size:29px;font-weight:900;margin:18px 0 8px}
.feature .number{font-size:54px;font-weight:900;color:var(--lime)}
.small-label{font:10px 'DM Mono',monospace;color:var(--muted);
 letter-spacing:1.5px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}
.metric{background:var(--panel);border:1px solid var(--line);
 padding:22px;min-height:125px}
.metric strong{display:block;font-size:34px;margin-top:15px}
.metric .accent{color:var(--lime)}
.metric .teal{color:var(--teal)}
.section{margin-top:48px}
.section-head{display:flex;align-items:end;justify-content:space-between;
 gap:15px;margin-bottom:17px}
.section-head p{font:10px 'DM Mono',monospace;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:15px}
.panel{background:var(--panel);border:1px solid var(--line);
 padding:22px;min-width:0}
.panel-title{font-size:13px;font-weight:800;letter-spacing:1px}
.panel-note{color:var(--muted);font-size:11px;margin:7px 0 12px}
.btn{display:inline-flex;align-items:center;justify-content:center;
 background:var(--lime);color:#11180F;padding:13px 18px;
 font-size:11px;font-weight:900;letter-spacing:1px;border:0;cursor:pointer}
.btn.secondary{background:transparent;color:var(--lime);
 border:1px solid #617344}
.btn:hover{transform:translateY(-1px);filter:brightness(1.05)}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}
.tablebox{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:12px}
th{text-align:left;color:var(--muted);font:10px 'DM Mono',monospace;
 letter-spacing:1px;padding:14px 10px;border-bottom:1px solid var(--line)}
td{padding:14px 10px;border-bottom:1px solid #263229}
td.score{color:var(--lime);font-weight:800}
td.name{font-weight:700}
tr:hover td{background:#D5F47708}
.search{width:100%;padding:14px;background:#0B100E;
 border:1px solid var(--line);color:var(--white);outline:none;margin:12px 0}
.search:focus,select:focus{border-color:var(--lime)}
.controls{display:flex;gap:12px;flex-wrap:wrap;margin:15px 0}
select{background:#0B100E;color:var(--white);padding:12px;
 border:1px solid var(--line);min-width:180px}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px}
.playercard{background:var(--panel2);border:1px solid var(--line);padding:20px}
.playercard .big{font-size:35px;color:var(--lime);font-weight:900;margin:12px 0}
.playercard p{font-size:12px;color:var(--muted)}
.profile-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.profile-stat{background:var(--panel);border:1px solid var(--line);padding:20px}
.profile-stat strong{display:block;font-size:29px;color:var(--lime);margin-top:12px}
.rulegrid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.rule{background:var(--panel);border:1px solid var(--line);padding:22px}
.rule p{color:var(--muted);font-size:13px;line-height:1.8}
.rule .index{font:11px 'DM Mono',monospace;color:var(--orange)}
.footer{border-top:1px solid var(--line);padding:24px 5%;
 display:flex;justify-content:space-between;color:var(--muted);
 font:10px 'DM Mono',monospace;letter-spacing:1px}
.empty{color:var(--muted);padding:20px}
@media(max-width:850px){
 .hero{grid-template-columns:1fr}
 .grid4{grid-template-columns:repeat(2,1fr)}
 .navlinks{gap:10px}.navlinks a{font-size:9px}
 .cards,.rulegrid{grid-template-columns:1fr}
}
@media(max-width:560px){
 .navbar{padding:0 4%;height:auto;min-height:68px;flex-wrap:wrap}
 .navlinks{width:100%;overflow:auto;padding:12px 0}
 .wrap{padding:35px 4% 55px}
 h1{letter-spacing:-2px}
 .grid4{grid-template-columns:1fr 1fr}
 .metric{padding:14px}.metric strong{font-size:25px}
 .compare,.profile-grid{grid-template-columns:1fr}
 .footer{flex-direction:column;gap:10px}
}
"""

(ASSETS / "style.css").write_text(css, encoding="utf-8")

shell = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ | SupeRR Selector</title>
<link rel="stylesheet" href="assets/style.css">
<script src="assets/data.js"></script>
<script src="assets/app.js" defer></script>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
</head><body>
<header class="navbar">
<a class="logo" href="index.html">SUPERR <span>SELECTOR</span></a>
<nav class="navlinks">
<a href="index.html" data-nav="home">HOME</a>
<a href="analyst.html" data-nav="analyst">ANALYST</a>
<a href="rankings.html" data-nav="rankings">RANKINGS</a>
<a href="methodology.html" data-nav="methodology">METHODOLOGY</a>
</nav><div class="live">● SYSTEM ACTIVE</div>
</header>
<main class="wrap">__CONTENT__</main>
<footer class="footer"><span>SUPERR SELECTOR / CRICKET INTELLIGENCE</span>
<span>DATA-DRIVEN PLAYER PERFORMANCE</span></footer>
<script>document.querySelectorAll('[data-nav]').forEach(a=>{
if(a.dataset.nav==='__PAGE__')a.classList.add('active')});</script>
</body></html>"""

def page(filename, title, nav, content):
    output = shell.replace("__TITLE__", title).replace(
        "__CONTENT__", content).replace("__PAGE__", nav)
    (SITE / filename).write_text(output, encoding="utf-8")

home = f"""
<div class="hero">
 <div><div class="kicker">Cricket performance intelligence / 001</div>
 <h1>WHEN THE GAME<br>GETS TIGHT.<br><em>WHO DELIVERS?</em></h1>
 <p class="lead">A new lens on cricket performance. SupeRR Selector
 identifies players who deliver under pressure through ball-by-ball
 analysis, contextual benchmarks and reliability-adjusted ratings.</p>
 <div class="actions">
  <a class="btn" href="analyst.html">ENTER ANALYST WORKSPACE ↗</a>
  <a class="btn secondary" href="rankings.html">EXPLORE RANKINGS</a>
 </div></div>
 <div class="feature"><div class="small-label">TOP BATTER / CURRENT DATASET</div>
 <div class="name">{html.escape(str(best_batter_name := batters.iloc[batters["batting_pressure_score"].argmax()]["striker_name"]))}</div>
 <div class="number">{batters["batting_pressure_score"].max():.2f}</div>
 <div class="small-label">PRESSURE PERFORMANCE SCORE</div>
 <p class="lead">The highest-rated batter in the current qualified dataset.</p>
 </div>
</div>
<div class="grid4">
 <div class="metric"><div class="small-label">QUALIFIED BATTERS</div><strong>{len(batters):,}</strong></div>
 <div class="metric"><div class="small-label">QUALIFIED BOWLERS</div><strong class="teal">{len(bowlers):,}</strong></div>
 <div class="metric"><div class="small-label">TOP BATTING SCORE</div><strong class="accent">{batters["batting_pressure_score"].max():.1f}</strong></div>
 <div class="metric"><div class="small-label">TOP BOWLING SCORE</div><strong class="teal">{bowlers["bowling_pressure_score"].max():.1f}</strong></div>
</div>
<section class="section">
 <div class="section-head"><h2>THE LEADING PERFORMERS</h2>
 <p>TOP 5 / PRESSURE SCORE</p></div>
 <div class="cards">
  <div class="panel"><div class="panel-title">BATTING / UNDER PRESSURE</div>
   <div id="homeBatting" style="height:310px"></div></div>
  <div class="panel"><div class="panel-title">BOWLING / UNDER PRESSURE</div>
   <div id="homeBowling" style="height:310px"></div></div>
 </div>
</section>
<section class="section">
 <div class="section-head"><h2>BUILT FOR BETTER DECISIONS</h2><p>EXPLORE THE PLATFORM</p></div>
 <div class="cards">
  <a class="panel" href="analyst.html"><div class="kicker">01 / ANALYSE</div><h2>Analyst workspace ↗</h2><p class="lead">Search players, explore their pressure numbers and compare two players side by side.</p></a>
  <a class="panel" href="rankings.html"><div class="kicker">02 / DISCOVER</div><h2>Complete rankings ↗</h2><p class="lead">Explore qualified batters and bowlers, sort the leaderboard and open individual profiles.</p></a>
 </div>
</section>
"""
page("index.html", "Home", "home", home)

analyst = """
<div class="kicker">Performance intelligence / Workspace 002</div>
<h1>THE <em>ANALYST</em><br>ROOM.</h1>
<p class="lead">Search the qualified player pool. Inspect pressure performance.
Compare players using the same rating framework.</p>
<section class="section">
 <div class="section-head"><h2>PLAYER EXPLORER</h2><p>LIVE SEARCH / ALL QUALIFIED PLAYERS</p></div>
 <div class="cards">
  <div class="panel"><div class="panel-title">BATTER SEARCH</div>
   <input class="search" id="bSearch" placeholder="Type a batter name...">
   <div class="tablebox"><table><thead><tr><th>PLAYER</th><th>SCORE</th><th>RUNS</th><th>BALLS</th></tr></thead><tbody id="bResults"></tbody></table></div>
   <p class="small-label" id="bCount"></p>
  </div>
  <div class="panel"><div class="panel-title">BOWLER SEARCH</div>
   <input class="search" id="wSearch" placeholder="Type a bowler name...">
   <div class="tablebox"><table><thead><tr><th>PLAYER</th><th>SCORE</th><th>WICKETS</th><th>ECONOMY</th></tr></thead><tbody id="wResults"></tbody></table></div>
   <p class="small-label" id="wCount"></p>
  </div>
 </div>
</section>
<section class="section">
 <div class="section-head"><h2>HEAD-TO-HEAD</h2><p>PLAYER COMPARISON</p></div>
 <div class="cards">
  <div class="panel"><div class="panel-title">BATTER VS BATTER</div>
   <div class="controls"><select id="bA"></select><select id="bB"></select></div>
   <div class="compare" id="bCompare"></div></div>
  <div class="panel"><div class="panel-title">BOWLER VS BOWLER</div>
   <div class="controls"><select id="wA"></select><select id="wB"></select></div>
   <div class="compare" id="wCompare"></div></div>
 </div>
</section>
"""
page("analyst.html", "Analyst Workspace", "analyst", analyst)

rankings = """
<div class="kicker">The leaderboard / 003</div>
<h1>THE <em>RANKINGS.</em></h1>
<p class="lead">Explore every qualified player in the current dataset.
Sort by pressure score and open a profile for a closer look.</p>
<div class="section">
 <div class="controls"><button class="btn" id="showBatters">BATTERS</button>
 <button class="btn secondary" id="showBowlers">BOWLERS</button>
 <input class="search" id="rankSearch" placeholder="Search players..." style="max-width:340px"></div>
 <div class="panel"><div class="tablebox"><table><thead id="rankHead"></thead>
 <tbody id="rankBody"></tbody></table></div><p class="small-label" id="rankCount"></p></div>
</div>
"""
page("rankings.html", "Player Rankings", "rankings", rankings)

profile = """
<div class="kicker">Player intelligence / 004</div>
<div id="profileContent"><h1>PLAYER <em>PROFILE.</em></h1>
<p class="lead">Select a player from the rankings to view their performance profile.</p></div>
"""
page("profile.html", "Player Profile", "", profile)

methodology = """
<div class="kicker">Inside the engine / 005</div>
<h1>THE SCIENCE<br>OF <em>PRESSURE.</em></h1>
<p class="lead">SupeRR Selector evaluates performance before each delivery
and compares pressure performance against a non-pressure baseline.</p>
<div class="section rulegrid">
 <div class="rule"><div class="index">01 / SECOND INNINGS</div><h2>Chase pressure</h2>
 <p>Required run rate at least 9; or final 18 legal balls with required rate
 at least 7; or six or more wickets down with 36 or fewer legal balls remaining.</p></div>
 <div class="rule"><div class="index">02 / FIRST INNINGS</div><h2>Innings pressure</h2>
 <p>Four or more wickets down after 70% of available legal balls; or at least
 85% of available legal balls completed.</p></div>
 <div class="rule"><div class="index">03 / BATTING SCORE</div><h2>Batting impact</h2>
 <p>Pressure runs, balls faced and strike rate are compared with a
 non-pressure baseline for the same format, innings and phase. A
 sample-reliability adjustment reduces small-sample influence.</p></div>
 <div class="rule"><div class="index">04 / BOWLING SCORE</div><h2>Bowling impact</h2>
 <p>Pressure runs conceded, legal balls and bowler-credited wickets are
 compared with non-pressure phase baselines, with reliability adjustment.</p></div>
 <div class="rule"><div class="index">05 / QUALIFICATION</div><h2>Minimum sample</h2>
 <p>Batters require at least 30 pressure balls. Bowlers require at least
 30 pressure legal balls. Super Overs are excluded from regular rankings.</p></div>
 <div class="rule"><div class="index">06 / INTERPRETATION</div><h2>Reference score: 100</h2>
 <p>100 is the baseline reference. A score above 100 indicates better
 performance than the relevant non-pressure benchmark after reliability
 adjustment. Scores are not probabilities or predictions.</p></div>
</div>
"""
page("methodology.html", "Methodology", "methodology", methodology)

js = r"""
function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function score(n){return Number(n).toFixed(2)}
function chart(id, data, name, scoreKey, color){
 if(!window.Plotly)return;
 const d=data.slice().sort((a,b)=>b[scoreKey]-a[scoreKey]).slice(0,5).reverse();
 Plotly.newPlot(id,[{type:"bar",orientation:"h",x:d.map(p=>p[scoreKey]),
 y:d.map(p=>p[name]),marker:{color},text:d.map(p=>score(p[scoreKey])),
 textposition:"outside",hovertemplate:"<b>%{y}</b><br>Score %{x:.2f}<extra></extra>"}],
 {paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",
 font:{color:"#F3F1E8",family:"DM Sans"},margin:{l:10,r:45,t:8,b:35},
 xaxis:{gridcolor:"#2A382F",title:"Pressure score"},
 yaxis:{gridcolor:"rgba(0,0,0,0)"}},{displayModeBar:false,responsive:true});
}
function playerLink(type,name){return "profile.html?type="+type+"&name="+encodeURIComponent(name)}
function renderExplorer(){
 const b=document.getElementById("bResults"),w=document.getElementById("wResults");
 if(!b||!w)return;
 function rb(q=""){
  const d=BATTERS.filter(p=>p.striker_name.toLowerCase().includes(q.toLowerCase())).sort((a,b)=>b.batting_pressure_score-a.batting_pressure_score);
  b.innerHTML=d.slice(0,40).map(p=>`<tr><td class="name"><a href="${playerLink("batter",p.striker_name)}">${esc(p.striker_name)}</a></td><td class="score">${score(p.batting_pressure_score)}</td><td>${p.pressure_runs}</td><td>${p.pressure_balls}</td></tr>`).join("");
  document.getElementById("bCount").textContent=`Showing ${Math.min(40,d.length)} of ${d.length} matching batters`;
 }
 function rw(q=""){
  const d=BOWLERS.filter(p=>p.bowler_name.toLowerCase().includes(q.toLowerCase())).sort((a,b)=>b.bowling_pressure_score-a.bowling_pressure_score);
  w.innerHTML=d.slice(0,40).map(p=>`<tr><td class="name"><a href="${playerLink("bowler",p.bowler_name)}">${esc(p.bowler_name)}</a></td><td class="score">${score(p.bowling_pressure_score)}</td><td>${p.pressure_wickets}</td><td>${Number(p.pressure_economy).toFixed(2)}</td></tr>`).join("");
  document.getElementById("wCount").textContent=`Showing ${Math.min(40,d.length)} of ${d.length} matching bowlers`;
 }
 document.getElementById("bSearch").addEventListener("input",e=>rb(e.target.value));
 document.getElementById("wSearch").addEventListener("input",e=>rw(e.target.value));
 rb();rw();
 function fill(id,data,key){document.getElementById(id).innerHTML=data.slice().sort((a,b)=>a[key].localeCompare(b[key])).map(p=>`<option>${esc(p[key])}</option>`).join("")}
 fill("bA",BATTERS,"striker_name");fill("bB",BATTERS,"striker_name");
 fill("wA",BOWLERS,"bowler_name");fill("wB",BOWLERS,"bowler_name");
 function bc(){
  const a=BATTERS.find(p=>p.striker_name===bA.value),b=BATTERS.find(p=>p.striker_name===bB.value);
  bCompare.innerHTML=[a,b].map(p=>`<div class="playercard"><h3>${esc(p.striker_name)}</h3><div class="big">${score(p.batting_pressure_score)}</div><p>Pressure score</p><p>Runs: ${p.pressure_runs}</p><p>Balls: ${p.pressure_balls}</p><p>Strike rate: ${score(p.pressure_strike_rate)}</p></div>`).join("");
 }
 function wc(){
  const a=BOWLERS.find(p=>p.bowler_name===wA.value),b=BOWLERS.find(p=>p.bowler_name===wB.value);
  wCompare.innerHTML=[a,b].map(p=>`<div class="playercard"><h3>${esc(p.bowler_name)}</h3><div class="big">${score(p.bowling_pressure_score)}</div><p>Pressure score</p><p>Wickets: ${p.pressure_wickets}</p><p>Legal balls: ${p.pressure_legal_balls}</p><p>Economy: ${score(p.pressure_economy)}</p></div>`).join("");
 }
 ["bA","bB"].forEach(id=>document.getElementById(id).addEventListener("change",bc));
 ["wA","wB"].forEach(id=>document.getElementById(id).addEventListener("change",wc));
 bc();wc();
}
function renderRankings(){
 const body=document.getElementById("rankBody");if(!body)return;
 let type="batter";
 function draw(){
  const q=document.getElementById("rankSearch").value.toLowerCase();
  const isB=type==="batter",data=isB?BATTERS:BOWLERS;
  const name=isB?"striker_name":"bowler_name",key=isB?"batting_pressure_score":"bowling_pressure_score";
  const stat=isB?"pressure_runs":"pressure_wickets",statName=isB?"RUNS":"WICKETS";
  const d=data.filter(p=>p[name].toLowerCase().includes(q)).sort((a,b)=>b[key]-a[key]);
  rankHead.innerHTML=`<tr><th>RANK</th><th>PLAYER</th><th>PRESSURE SCORE</th><th>${statName}</th></tr>`;
  rankBody.innerHTML=d.map((p,i)=>`<tr><td>${String(i+1).padStart(2,"0")}</td><td class="name"><a href="${playerLink(type,p[name])}">${esc(p[name])}</a></td><td class="score">${score(p[key])}</td><td>${p[stat]}</td></tr>`).join("");
  rankCount.textContent=`${d.length} qualified ${type}s`;
 }
 showBatters.onclick=()=>{type="batter";showBatters.className="btn";showBowlers.className="btn secondary";draw()};
 showBowlers.onclick=()=>{type="bowler";showBowlers.className="btn";showBatters.className="btn secondary";draw()};
 rankSearch.oninput=draw;draw();
}
function renderProfile(){
 const box=document.getElementById("profileContent");if(!box)return;
 const params=new URLSearchParams(location.search),type=params.get("type"),name=params.get("name");
 const batter=type==="batter",data=batter?BATTERS:BOWLERS;
 const key=batter?"striker_name":"bowler_name",p=data.find(x=>x[key]===name);
 if(!p){box.innerHTML="<h1>PLAYER <em>NOT FOUND.</em></h1><a class='btn' href='rankings.html'>BACK TO RANKINGS</a>";return}
 const scoreKey=batter?"batting_pressure_score":"bowling_pressure_score";
 const stats=batter?[["PRESSURE RUNS",p.pressure_runs],["PRESSURE BALLS",p.pressure_balls],["PRESSURE STRIKE RATE",score(p.pressure_strike_rate)]]:[["RUNS CONCEDED",p.pressure_runs_conceded],["LEGAL BALLS",p.pressure_legal_balls],["WICKETS",p.pressure_wickets],["ECONOMY",score(p.pressure_economy)]];
 box.innerHTML=`<div class="kicker">Player profile / ${batter?"Batter":"Bowler"}</div><h1>${esc(name)}<br><em>PROFILE.</em></h1><div class="feature"><div class="small-label">PRESSURE PERFORMANCE SCORE</div><div class="number">${score(p[scoreKey])}</div><div class="small-label">REFERENCE SCORE: 100</div></div><section class="section profile-grid">${stats.map(s=>`<div class="profile-stat"><div class="small-label">${s[0]}</div><strong>${s[1]}</strong></div>`).join("")}</section><div class="actions"><a class="btn" href="rankings.html">BACK TO RANKINGS</a><a class="btn secondary" href="analyst.html">OPEN ANALYST WORKSPACE</a></div>`;
}
document.addEventListener("DOMContentLoaded",()=>{
 if(document.getElementById("homeBatting")){
  chart("homeBatting",BATTERS,"striker_name","batting_pressure_score","#D5F477");
  chart("homeBowling",BOWLERS,"bowler_name","bowling_pressure_score","#65D7C0");
 }
 renderExplorer();renderRankings();renderProfile();
});
"""
(ASSETS / "app.js").write_text(js, encoding="utf-8")

print("SUPERR SELECTOR WEBSITE CREATED")
for filename in ["index.html", "analyst.html", "rankings.html", "profile.html", "methodology.html"]:
    print("Created:", SITE / filename)
print("Qualified batters:", len(batters))
print("Qualified bowlers:", len(bowlers))


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
}

function renderHeadToHead(){
 const bA=document.getElementById("bA"),bB=document.getElementById("bB");
 const wA=document.getElementById("wA"),wB=document.getElementById("wB");
 if(!bA||!bB||!wA||!wB)return;

 function fill(select,data,key){
  select.innerHTML=data.slice().sort((a,b)=>a[key].localeCompare(b[key]))
   .map(p=>`<option value="${esc(p[key])}">${esc(p[key])}</option>`).join("");
 }
 fill(bA,BATTERS,"striker_name");fill(bB,BATTERS,"striker_name");
 fill(wA,BOWLERS,"bowler_name");fill(wB,BOWLERS,"bowler_name");

 function comparisonTable(container,a,b,nameA,nameB,rows){
  const body=rows.map(r=>{
   const x=Number(r[1]),y=Number(r[2]);
   let edge="?";
   if(r[4] && x!==y){
    const firstWins=r[5] ? x<y : x>y;
    edge=firstWins ? esc(nameA) : esc(nameB);
   }
   return `<tr><td>${esc(r[0])}</td><td>${esc(r[3](r[1]))}</td><td>${esc(r[3](r[2]))}</td><td class="score">${edge}</td></tr>`;
  }).join("");
  container.innerHTML=`<div class="tablebox"><table class="compare-table">
   <thead><tr><th>METRIC</th><th>${esc(nameA)}</th><th>${esc(nameB)}</th><th>EDGE</th></tr></thead>
   <tbody>${body}</tbody></table></div>`;
 }

 function updateBatters(){
  const a=BATTERS.find(p=>p.striker_name===bA.value);
  const b=BATTERS.find(p=>p.striker_name===bB.value);
  if(!a||!b)return;
  comparisonTable(document.getElementById("bCompare"),a,b,a.striker_name,b.striker_name,[
   ["Pressure score",a.batting_pressure_score,b.batting_pressure_score,score,true,false],
   ["Pressure runs",a.pressure_runs,b.pressure_runs,v=>String(v),false,false],
   ["Pressure balls",a.pressure_balls,b.pressure_balls,v=>String(v),false,false],
   ["Strike rate",a.pressure_strike_rate,b.pressure_strike_rate,score,true,false]
  ]);
 }

 function updateBowlers(){
  const a=BOWLERS.find(p=>p.bowler_name===wA.value);
  const b=BOWLERS.find(p=>p.bowler_name===wB.value);
  if(!a||!b)return;
  comparisonTable(document.getElementById("wCompare"),a,b,a.bowler_name,b.bowler_name,[
   ["Pressure score",a.bowling_pressure_score,b.bowling_pressure_score,score,true,false],
   ["Wickets",a.pressure_wickets,b.pressure_wickets,v=>String(v),true,false],
   ["Legal balls",a.pressure_legal_balls,b.pressure_legal_balls,v=>String(v),false,false],
   ["Economy",a.pressure_economy,b.pressure_economy,score,true,true]
  ]);
 }

 [bA,bB].forEach(el=>el.addEventListener("change",updateBatters));
 [wA,wB].forEach(el=>el.addEventListener("change",updateBowlers));
 updateBatters();updateBowlers();
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
 renderExplorer();renderHeadToHead();renderRankings();renderProfile();
});

/* SupeRR Selector. Plain browser JavaScript; no CDN, account or network dependency. */
'use strict';
let DATA;
const state = {page:'rankings',role:'batters',scope:'Combined',player:null,search:'',all:false,match:null,year:'All',innings:'1',over:null};
const main = document.getElementById('main');
const PINK = 'var(--pink)', TEAL = 'var(--teal)', GREY = 'var(--chart-muted)';
let matchRequest = 0;
const matchCache = new Map();
const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const fmt = (value, digits=0) => value == null ? '—' : Number(value).toLocaleString('en-IN',{minimumFractionDigits:digits,maximumFractionDigits:digits});
const signed = (value,digits=2) => value == null ? '—' : `${value>0?'+':''}${fmt(value,digits)}`;
const initials = name => name.split(' ').filter(Boolean).map(n=>n[0]).slice(0,2).join('');
const rows = () => DATA.rankings[state.scope][state.role];
const current = () => rows().find(r=>r.id===Number(state.player)) || rows()[0];
const titleRole = () => state.role==='batters'?'Batters':'Bowlers';
const option = (value,label,selected) => `<option value="${esc(value)}" ${String(value)===String(selected)?'selected':''}>${esc(label)}</option>`;
const tag = (text,kind='') => `<span class="tag ${kind}">${esc(text)}</span>`;
const svg = (body,width=560,height=280,label='Chart') => `<svg class="chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(label)}">${body}</svg>`;


function icon(name='chart') {
  const paths = {
    chart:'<path d="M4 19V5m0 14h16M8 15v-4m5 4V7m5 8V3"/>',
    bat:'<path d="m14 3 3 3-3 3-3-3 3-3Zm-3 3-8 8 6 6 8-8-3-3M6 17l-3 3"/>',
    ball:'<circle cx="12" cy="12" r="8"/><path d="M5 7c7 0 12 5 12 12M7 5c0 7 5 12 12 12"/>',
    arrow:'<path d="M5 19 19 5M7 5h12v12"/>',
    report:'<path d="M14 3H5v18h14V8l-5-5Zm0 0v5h5M8 12h8m-8 4h6"/>',
    download:'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
    search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    target:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    shield:'<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/>'
  };
  return `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${paths[name]||paths.chart}</svg>`;
}

function stat(label,value,note,iconName='chart'){
  return `<div class="stat"><div class="stat-top">${esc(label)}<span class="stat-icon" aria-hidden="true">${icon({'▤':'report','◌':'ball','⌁':'chart','◎':'target'}[iconName]||iconName)}</span></div><div class="stat-value numeric">${value}</div><div class="stat-detail">${note}</div></div>`;
}
function scopeSelect(){return `<label class="select-wrap"><span class="field-label">Competition</span><select id="scope-select" aria-label="Competition scope">${['Combined','IPL','T20I'].map(s=>option(s,s==='Combined'?'IPL + T20I':s,state.scope)).join('')}</select></label>`;}
function roleControl(){return `<div class="segmented" role="group" aria-label="Player category">${['batters','bowlers'].map(role=>`<button class="segment ${state.role===role?'active':''}" data-role="${role}" aria-pressed="${state.role===role}">${icon(role==='batters'?'bat':'ball')}${role==='batters'?'Batters':'Bowlers'}</button>`).join('')}</div>`;}
function header(eyebrow,title,description,actions=''){
  if(state.page==='rankings') return `<div class="page-heading workspace-hero"><div class="hero-dots" aria-hidden="true"></div><div class="hero-copy"><div class="eyebrow">SUPERR SELECTOR <span>/</span> SEASON 02</div><h1>The selection <span>room.</span></h1><p>Find the players who deliver under pressure.<br>Every selection, backed by match evidence.</p><div class="hero-meta"><span><i class="live-dot"></i> PERFORMANCE INTELLIGENCE</span><span>IPL + T20I · 2022–2026</span></div></div><div class="hero-art" aria-hidden="true"><span class="hero-edition">THE ROYALS WAY</span><img src="assets/png-transparent-rajasthan-royals-logo-pink-sports-cricket-teams-thumbnail.png" alt=""><div class="hero-art-caption">PERFORMANCE.<br><strong>UNDER PRESSURE.</strong></div></div></div>`;
  return `<div class="page-heading"><div><div class="eyebrow">${eyebrow}</div><h1>${title}</h1><p>${description}</p></div>${actions?`<div class="actions">${actions}</div>`:''}</div>`;
}
function caveat(){return `<div class="notice"><span aria-hidden="true">ⓘ</span><div><strong>Read the numbers in context.</strong> Pressure is a phase-and-wicket proxy. Extras in the source are not reliable run amounts, so scoring rates use legal-ball bat runs. These are model rankings, not claims about official economy or exact chase difficulty. <a href="#methodology">See assumptions</a></div></div>`;}
function download(name,content,type='text/csv;charset=utf-8'){
  const url=URL.createObjectURL(new Blob([content],{type})); const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function toast(message){const el=document.getElementById('toast');el.textContent=message;el.classList.add('visible');setTimeout(()=>el.classList.remove('visible'),3200);}
function exportRankings(){
  const quote = x => `"${String(x??'').replace(/"/g,'""')}"`;
  const header=['Rank','Player','Scope','Category','Rating','Pressure balls','Pressure matches','Pressure legal-ball SR','Bat runs per six legal balls','Wickets per 100 legal balls','Ordinary impact','Pressure impact','Scenario rank minimum','Scenario rank maximum','Ineligible scenarios','Reasons','Limitation'];
  const out = rows().slice(0,10).map(r=>[r.rank,r.name,state.scope,state.role,r.score.toFixed(2),r.pressure.balls,r.pressure_matches,r.pressure.sr,r.pressure.run_rate,r.pressure.wicket_rate,r.normal.impact,r.pressure.impact,...r.sensitivity,r.sensitivity_missing,r.reasons.join(' '),r.limitation]);
  download(`top_10_${state.role}_${state.scope.toLowerCase()}.csv`,'\ufeff'+[header,...out].map(row=>row.map(quote).join(',')).join('\r\n'));
  toast(`Downloaded ${state.scope} top 10 ${state.role}`);
}

function navigate(page,extra={}){
  Object.assign(state,extra,{page});
  const hash = page==='players' ? `players/${state.role}/${state.player||current()?.id}` : page==='matches'&&state.match ? `matches/${state.match}` : page;
  if(location.hash.slice(1)!==hash) location.hash=hash;
  else render();
}
function route(){
  const [page,part,id]=location.hash.replace('#','').split('/');
  if(page==='main'){main.focus();return;}
  if(['rankings','players','matches','methodology','simulator'].includes(page)) state.page=page;
  else state.page='rankings';
  if(page==='players'&&['batters','bowlers'].includes(part)){state.role=part;state.player=Number(id)||null;}
  if(page==='matches'&&Number(part)){state.match=Number(part);state.year='All';}
  render();
}
function render(){
  matchRequest++;
  document.querySelectorAll('.nav-link').forEach(b=>{b.classList.toggle('active',b.dataset.page===state.page);b.setAttribute('aria-current',b.dataset.page===state.page?'page':'false');});
  const titles={rankings:'Rankings',players:'Player lab',matches:'Match explorer',methodology:'Methodology',simulator:'Scenario lab'};
  document.getElementById('breadcrumb').textContent=titles[state.page];
  document.title=`${titles[state.page]} · SupeRR Selector`;
  ({rankings:renderRankings,players:renderPlayer,matches:renderMatches,methodology:renderMethodology,simulator:renderSimulator})[state.page]();
}

function tableRows(){
  const selected=current();
  const pool = state.all || state.search ? rows() : rows().slice(0,10);
  const list = pool.filter(r=>r.name.toLowerCase().includes(state.search.toLowerCase()));
  return list.map(r=>`<tr class="ranking-row ${pakistanReview(r)?'ipl-review':''} ${r.id===selected?.id?'selected':''}" data-select-player="${r.id}">
    <td><span class="rank-num ${r.rank<=3?'podium':''}">${String(r.rank).padStart(2,'0')}</span></td>
    <td><button class="player-button" data-select-player="${r.id}" aria-label="Preview ${esc(r.name)}"><span class="player-cell"><span class="avatar">${esc(initials(r.name))}</span><span><span class="player-name">${esc(r.name)} ${availabilityBadge(r)}</span><span class="player-sub" style="display:block">${esc(r.teams.slice(0,2).join(' / '))}</span></span></span></button></td>
    <td class="rating-cell"><strong class="numeric">${fmt(r.score,1)}</strong><div class="mini-track"><div class="mini-fill" style="width:${r.score}%"></div></div></td>
    <td class="numeric sample-col">${fmt(r.pressure.balls)}</td>
    <td class="numeric optional">${r.pressure_matches}</td>
    <td class="numeric optional">${r.sensitivity[0]}–${r.sensitivity[1]}${r.sensitivity_missing?'*':''}</td>
  </tr>`).join('') || '<tr><td colspan="6"><div class="empty">No eligible players match your search.</div></td></tr>';
}
function spotlight(r){
  if(!r)return '<div class="panel empty">No eligible players.</div>';
  const batter=state.role==='batters';
  return `<div class="spotlight"><div class="spotlight-top"><div class="eyebrow" style="margin:0">PLAYER DOSSIER</div>${tag(`#${r.rank} ${state.scope}`)}</div><h2>${esc(r.name)}</h2><p>${esc((batter?r.batting_style:r.bowling_style)||titleRole())}</p><div class="score-row"><div><div class="score-caption">PRESSURE RATING</div><div class="score-big numeric">${fmt(r.score,1)} <small>/ 100</small></div></div><span class="rating-seal" aria-hidden="true">${icon("shield")}</span></div><div class="spotlight-stats"><div><strong class="numeric">${fmt(batter?r.pressure.sr:r.pressure.run_rate,batter?1:2)}</strong><span>${batter?'Legal-ball strike rate':'Bat runs / six legal balls'}</span></div><div><strong class="numeric">${r.pressure_matches}</strong><span>Pressure matches with 6+ balls</span></div></div><button class="btn" data-open-player="${r.id}">Explore player evidence ${icon("arrow")}</button></div>
    <div class="panel why-card"><h3>Why this player?</h3>${[r.reasons[0],r.reasons[2],r.reasons[3]].map(t=>`<div class="reason-item"><span class="reason-mark" aria-hidden="true">↗</span><span>${esc(t)}</span></div>`).join('')}<p class="muted-note" style="margin:12px 0 0">Scenario ranks ${r.sensitivity[0]}–${r.sensitivity[1]}.${r.sensitivity_missing?` Ineligible in ${r.sensitivity_missing}/5 alternatives.`:''} This range is not a confidence interval.</p></div>`;
}
function renderRankings(){
  const meta=DATA.meta;
  main.innerHTML=header('THE PRESSURE INDEX','Who delivers when it matters?','Explore the players who outperform their context in pivotal T20 situations.',`<a class="btn" href="report.html" target="_blank" rel="noopener">Read report ↗</a><button class="btn primary" data-action="export">↓ Export top 10</button>`)
    + `<div class="stats-grid">${stat('Matches analysed',fmt(meta.analysed_matches),`${meta.source_matches} match records supplied`,'▤')}${stat('Legal deliveries',fmt(meta.legal_balls),'After exclusions and sequence checks','◌')}${stat('Pressure deliveries',fmt(meta.pressure_balls),`<span class="pink-text">${fmt(100*meta.pressure_balls/meta.legal_balls,1)}%</span> of retained legal balls`,'⌁')}${stat(`Eligible ${state.role}`,fmt(rows().length),`${state.scope} · 60 balls + 8 matches minimum`,'◎')}</div>`
    + `<div class="section-heading"><div><div class="section-kicker">PLAYER EVALUATION</div><h2>Pressure rankings</h2><p>A shortlist built on performance, uplift and repeatability.</p></div><div class="actions"><a class="btn" href="report.html" target="_blank" rel="noopener">${icon('report')} Read report</a><button class="btn primary" data-action="export">${icon('download')} Export top 10</button></div></div>`
    + `<div class="toolbar">${roleControl()}<div class="filters">${scopeSelect()}<label class="search-field">${icon('search')}<span class="sr-only">Search eligible players</span><input id="player-search" type="search" placeholder="Search a player…" value="${esc(state.search)}"></label></div></div>`
    + `<p class="review-legend"><span class="availability-flag">⚑ Pakistan · IPL review</span> marks Pakistan representation. Players stay ranked on performance; check IPL availability separately. <a href="#methodology">How to read this flag</a></p>`
    + `<div class="content-grid"><section class="panel"><div class="panel-head"><div><h2>Top 10 ${state.role}</h2><p>${state.scope==='Combined'?'Default submission ranking':'Exploratory competition ranking'} · select a player to see why</p></div>${tag(state.scope==='Combined'?'IPL + T20I':state.scope,'pink')}</div><div class="table-wrap"><table class="rank-table"><thead><tr><th>#</th><th>Player</th><th>Rating / 100</th><th class="sample-col">P. balls</th><th class="optional">Matches</th><th class="optional">Rank range</th></tr></thead><tbody id="ranking-body">${tableRows()}</tbody></table></div><div class="table-note"><label class="toggle-all"><input type="checkbox" id="all-players" ${state.all?'checked':''}> Show all eligible players</label><span>* Ineligible in some scenarios</span></div></section><aside class="stack" id="spotlight">${spotlight(current())}</aside></div>`
    + `<div class="below-grid"><section class="panel"><div class="panel-head"><div><h2>Usual vs. under pressure</h2><p>${state.role==='batters'?'Legal-ball strike rate · raw rates, before context adjustment':'Bat runs / six legal balls · lower is better'}</p></div></div><div class="panel-body"><div class="chart-legend"><span><i class="legend-dot" style="background:${GREY}"></i>Ordinary</span><span><i class="legend-dot" style="background:${PINK}"></i>Pressure</span></div>${comparisonChart(rows().slice(0,6))}</div></section><section class="panel"><div class="panel-head"><div><h2>Performance meets evidence</h2><p>More pressure balls help put a strong rating in perspective.</p></div></div><div class="panel-body">${scatterChart(rows())}<div class="chart-legend"><span><i class="legend-dot" style="background:${PINK}"></i>Top 10</span><span><i class="legend-dot" style="background:var(--chart-muted)"></i>Other eligible players</span></div></div></section></div>`+caveat();
}

function comparisonChart(list){
  const metric=state.role==='batters'?'sr':'run_rate';
  const values=list.flatMap(r=>[r.normal[metric],r.pressure[metric]]);
  const lo=Math.max(0,Math.floor(Math.min(...values)*.8));const hi=Math.max(...values)*1.12;
  const x=v=>145+(v-lo)/(hi-lo||1)*340;let body='';
  for(let i=0;i<4;i++){const val=lo+(hi-lo)*i/3;body+=`<line class="chart-grid" x1="${x(val)}" x2="${x(val)}" y1="4" y2="238"/><text x="${x(val)}" y="259" text-anchor="middle">${fmt(val,metric==='sr'?0:1)}</text>`;}
  list.forEach((r,i)=>{const y=22+i*39;body+=`<text class="chart-label" x="0" y="${y+4}">${esc(r.name.length>20?r.name.slice(0,19)+'…':r.name)}</text><line x1="${x(r.normal[metric])}" x2="${x(r.pressure[metric])}" y1="${y}" y2="${y}" stroke="var(--chart-link)" stroke-width="3"/><circle cx="${x(r.normal[metric])}" cy="${y}" r="5" fill="${GREY}"><title>Ordinary ${r.name}: ${r.normal[metric]}</title></circle><circle cx="${x(r.pressure[metric])}" cy="${y}" r="5" fill="${PINK}"><title>Pressure ${r.name}: ${r.pressure[metric]}</title></circle><text class="chart-value" x="${x(r.pressure[metric])+10}" y="${y+4}">${fmt(r.pressure[metric],metric==='sr'?0:1)}</text>`;});
  return svg(body,540,273,'Ordinary and pressure rates for the top six players');
}
function scatterChart(list){
  const max=Math.max(...list.map(r=>r.pressure.balls))*1.12;const x=v=>43+v/max*440,y=v=>220-v/100*196;
  let body='';for(let i=0;i<=4;i++){const value=i*25;body+=`<line class="chart-grid" x1="43" x2="492" y1="${y(value)}" y2="${y(value)}"/><text x="31" y="${y(value)+4}" text-anchor="end">${value}</text><text x="${x(max*i/4)}" y="239" text-anchor="middle">${fmt(max*i/4)}</text>`;}
  list.slice().reverse().forEach(r=>{body+=`<circle cx="${x(r.pressure.balls)}" cy="${y(r.score)}" r="${r.rank<=10?5:3.5}" fill="${r.rank<=10?PINK:'var(--chart-muted)'}" fill-opacity="${r.rank<=10?.9:.55}" data-open-player="${r.id}" tabindex="0" role="button" aria-label="Open ${esc(r.name)}"><title>${esc(r.name)}: rating ${fmt(r.score,1)}, ${r.pressure.balls} pressure balls</title></circle>`;});
  body+=`<text x="265" y="263" text-anchor="middle">Pressure balls</text><text x="5" y="12">Rating</text>`;
  return svg(body,540,273,'Rating versus pressure balls. Each point opens a player profile.');
}

function renderPlayer(){
  const r=current();if(!r){main.innerHTML='<div class="empty">No eligible players in this scope.</div>';return;}
  state.player=r.id;const batting=state.role==='batters';
  main.innerHTML=header('LOOK BEYOND THE RANK','The player lab.','Follow the evidence from match performances to the final rating.',`<button class="btn" data-page="rankings">← Back to rankings</button>`)
    + `<div class="toolbar">${roleControl()}<div class="filters">${scopeSelect()}<label><span class="sr-only">Choose a player</span><select id="profile-player" class="profile-selector">${rows().map(p=>option(p.id,`#${p.rank} ${p.name}`,r.id)).join('')}</select></label></div></div>`
    + identityHeader(r) + labIntelligence(r) + labOverview(r)
    + `<div class="stats-grid">${stat('Pressure balls',fmt(r.pressure.balls),'Minimum for eligibility: 60')}${stat('Pressure matches',r.pressure_matches,'Matches with at least 6 pressure balls')}${stat('Above-context matches',`${r.successful_matches} / ${r.pressure_matches}`,'Unsmooothed observed match count'.replace('Unsmooothed','Unsmoothed'))}${stat('Scenario rank range',`${r.sensitivity[0]}–${r.sensitivity[1]}`,`${r.sensitivity_missing} of 5 alternatives ineligible`)}</div>`
    + `<div class="content-grid"><section class="panel"><div class="panel-head"><div><h2>Does pressure change the performance?</h2><p>Raw scoring rates shown alongside context-adjusted impact.</p></div></div><div class="panel-body"><div class="metric-comparison"><div class="comparison-cell"><span>ORDINARY SITUATIONS</span><strong>${fmt(batting?r.normal.sr:r.normal.run_rate,batting?1:2)}</strong><small>${batting?'Legal-ball strike rate':'Bat runs / six legal balls'} · ${fmt(r.normal.balls)} balls</small></div><div class="comparison-cell pressure"><span>UNDER PRESSURE</span><strong>${fmt(batting?r.pressure.sr:r.pressure.run_rate,batting?1:2)}</strong><small>${batting?'Legal-ball strike rate':'Bat runs / six legal balls'} · ${fmt(r.pressure.balls)} balls</small></div></div><div class="table-wrap"><table class="metric-table"><thead><tr><th>Metric</th><th>Ordinary</th><th>Pressure</th><th>Pressure peers</th></tr></thead><tbody><tr><td>${batting?'Striker dismissals':'Credited wickets'} / 100 balls</td><td>${fmt(r.normal.wicket_rate,2)}</td><td>${fmt(r.pressure.wicket_rate,2)}</td><td>${fmt(r.pressure.expected_wicket_rate,2)}</td></tr><tr><td>${batting?'Legal-ball strike rate':'Bat runs / six legal balls'}</td><td>${fmt(batting?r.normal.sr:r.normal.run_rate,2)}</td><td>${fmt(batting?r.pressure.sr:r.pressure.run_rate,2)}</td><td>${fmt(batting?r.pressure.expected_sr:r.pressure.expected_run_rate,2)}</td></tr><tr><td>Boundary balls</td><td>${fmt(r.normal.boundary_pct,1)}%</td><td>${fmt(r.pressure.boundary_pct,1)}%</td><td>—</td></tr><tr><td>Context-adjusted impact / ball</td><td>${signed(r.normal.impact,3)}</td><td>${signed(r.pressure.impact,3)}</td><td>0.000</td></tr></tbody></table></div><p class="muted-note" style="margin:14px 0 0">Peer expectations match this player's mix of competition, phase and innings, with year and role where sufficient data exists. Positive impact means better than that context.</p></div></section>
    <section class="panel"><div class="panel-head"><div><h2>Inside the rating</h2><p>Percentile among eligible ${state.scope} ${state.role}</p></div></div><div class="panel-body">${[['quality','Pressure performance','50%'],['uplift','Improvement vs. baseline','30%'],['consistency','Repeatability','20%']].map(([key,label,weight])=>`<div class="component-row"><div class="component-label"><span>${label} <span class="subtle">(${weight})</span></span><strong>${fmt(r.components[key],1)}</strong></div><div class="component-track"><div class="component-fill" style="width:${r.components[key]}%"></div></div></div>`).join('')}<p class="muted-note">Performance and uplift are shrunk toward the context average to reduce small-sample effects. The final rating is relative, not a success probability.</p></div></section></div>`
    + `<div class="below-grid"><section class="panel"><div class="panel-head"><div><h2>The selection case</h2><p>Four measured reasons, with the caveat kept visible.</p></div></div><div class="panel-body"><ol class="evidence-list">${r.reasons.map((reason,i)=>`<li><strong>0${i+1}</strong>${esc(reason)}</li>`).join('')}</ol><div class="notice"><div><strong>Limitation.</strong> ${esc(r.limitation)}</div></div></div></section><section class="panel"><div class="panel-head"><div><h2>Would the rank hold up?</h2><p>Five alternative assumptions · default rank #${r.rank}</p></div></div><table class="scenario-table"><thead><tr><th>Alternative</th><th>Rank</th></tr></thead><tbody>${Object.entries(r.scenario_ranks).map(([name,rank])=>`<tr><td>${esc(name)}</td><td>${rank?`#${rank}`:tag('Ineligible','amber')}</td></tr>`).join('')}</tbody></table><div class="panel-body" style="padding-top:15px"><p class="muted-note" style="margin:0">The rank range is a sensitivity check, not a confidence interval. Eligibility and peer populations can change between scenarios.</p></div></section></div>`
    + `<div class="below-grid"><section class="panel"><div class="panel-head"><div><h2>Across the seasons</h2><p>Mean context-adjusted pressure impact per ball</p></div></div><div class="panel-body"><div class="season-grid">${DATA.meta.years.map(year=>{const s=r.seasons.find(s=>s.year===year);return `<div class="season-cell ${s?(s.impact>=0?'positive':'negative'):''}"><span>${year}</span><strong>${s?signed(s.impact,2):'—'}</strong><small>${s?`${s.balls} balls`:'No sample'}</small></div>`;}).join('')}</div><p class="muted-note" style="margin:14px 0 0">Season cells have no separate minimum-sample gate; read the ball counts. Green is above context, pink is below.</p></div></section><section class="panel"><div class="panel-head"><div><h2>Pressure by innings phase</h2><p>How much of the evidence comes from each phase?</p></div></div><div class="panel-body">${r.phases.map(p=>`<div class="component-row"><div class="component-label"><span>${esc(p.phase)}</span><strong>${p.balls} balls · ${signed(p.impact,3)} impact</strong></div><div class="component-track"><div class="component-fill" style="background:${p.impact>=0?TEAL:PINK};width:${100*p.balls/r.pressure.balls}%"></div></div></div>`).join('')}</div></section></div>`
    + `<section class="panel" style="margin-top:22px"><div class="panel-head"><div><h2>Match evidence</h2><p>Highest total pressure impact first. Includes matches below the six-ball consistency gate.</p></div></div><div class="table-wrap"><table><thead><tr><th>Match</th><th>Date</th><th>Pressure balls</th><th>${batting?'Runs':'Credited wickets'}</th><th>Impact / ball</th><th></th></tr></thead><tbody>${r.matches.slice().sort((a,b)=>b.impact*b.balls-a.impact*a.balls).slice(0,8).map(s=>{const m=DATA.matches.find(m=>m.id===s.match_id);return `<tr><td>${esc(m?`${m.home} vs ${m.away}`:s.match_id)}</td><td>${esc(m?.date)}</td><td>${s.balls}</td><td>${batting?s.runs:s.wickets}</td><td style="color:${s.impact>=0?TEAL:PINK}">${signed(s.impact,3)}</td><td><button class="text-button" data-open-match="${s.match_id}">Explore ↗</button></td></tr>`;}).join('')}</tbody></table></div></section>`+caveat();
}

async function renderMatches(){
  const request=++matchRequest;
  const candidates=DATA.matches.filter(m=>state.year==='All'||m.date.startsWith(state.year));
  let match=candidates.find(m=>m.id===Number(state.match));
  if(!match){match=candidates.slice().sort((a,b)=>b.pressure_balls-a.pressure_balls)[0];state.match=match?.id;}
  main.innerHTML=header('REPLAY THE CONTEXT','Match intelligence.','Inspect the pressure before each ball and see exactly why it was flagged.')
    + `<div class="match-filters"><div><label for="match-year">Calendar year</label><select id="match-year">${['All',...DATA.meta.years].map(y=>option(y,y==='All'?'All years':y,state.year)).join('')}</select></div><div><label for="match-select">Match</label><select id="match-select">${candidates.map(m=>option(m.id,`${m.date} · ${m.home} vs ${m.away} · ${m.format}`,match?.id)).join('')}</select></div><div><label for="innings-select">Innings</label><select id="innings-select">${['1','2'].map(i=>option(i,`Innings ${i}`,state.innings)).join('')}</select></div></div><div id="match-detail"><div class="loading-state"><div class="spinner"></div><p>Loading match evidence…</p></div></div>`;
  if(!match){document.getElementById('match-detail').innerHTML='<div class="empty">No matches in this selection.</div>';return;}
  try{
    if(!matchCache.has(match.id)){const res=await fetch(`data/matches/${match.id}.json`);if(!res.ok)throw new Error('Match data could not be loaded');matchCache.set(match.id,await res.json());}
    if(request!==matchRequest)return;
    renderMatchDetail(matchCache.get(match.id));
  }catch(error){if(request===matchRequest)document.getElementById('match-detail').innerHTML=`<div class="error-state"><h2>Could not load this match</h2><p>${esc(error.message)}</p><button class="btn" data-action="retry-match">Try again</button></div>`;}
}
function renderMatchDetail(data){
  const points=data.innings[state.innings];const m=data.meta;
  if(!points){document.getElementById('match-detail').innerHTML='<div class="panel empty">This innings is absent or failed data checks. Try the other innings.</div>';return;}
  const grouped=new Map();for(const p of points){const over=Number(p[0].split('.')[0])+1;if(!grouped.has(over))grouped.set(over,[]);grouped.get(over).push(p);}
  if(!state.over||!grouped.has(state.over)){state.over=Array.from(grouped.keys()).sort((a,b)=>meanScore(grouped.get(b))-meanScore(grouped.get(a)))[0];}
  const legal=points.filter(p=>p[7]);
  document.getElementById('match-detail').innerHTML=`<section class="panel"><div class="match-title"><div class="match-summary">${tag(m.format,'pink')}${tag(m.stage)}<span class="muted-note">${esc(m.date)} · ${esc(m.country)}</span></div><h2>${esc(m.home)} <span style="color:var(--muted);font-weight:400">vs</span> ${esc(m.away)}</h2><p>${esc(m.result)} <span class="subtle">(supplied result)</span></p></div><div class="panel-head"><div><h2>Innings ${state.innings} · pressure timeline</h2><p>Average pre-delivery pressure by over. Select an over to inspect its deliveries.</p></div>${tag(`${legal.filter(p=>p[1]>=55).length} pressure balls`,'pink')}</div><div class="panel-body"><div class="chart-legend"><span><i class="legend-dot" style="background:${PINK}"></i>At / above threshold</span><span><i class="legend-dot" style="background:var(--chart-muted)"></i>Below threshold</span><span>Dashed line: threshold 55</span></div>${timelineChart(grouped)}<p class="timeline-note">This chart shows pressure points, not win probability. Over averages may hide a threshold crossing within an over; inspect the delivery rows below.</p></div></section>
    <div class="stats-grid" style="margin-top:20px">${stat('Retained legal balls',legal.length,'Only this innings')}${stat('Runs off the bat',fmt(legal.reduce((s,p)=>s+p[3],0)),'Retained legal balls only; not team total')}${stat('High-pressure share',fmt(100*legal.filter(p=>p[1]>=55).length/Math.max(1,legal.length),1)+'%','Of retained legal balls')}${stat('Wicket events',points.filter(p=>p[6]).length,'All source rows in this innings')}</div>
    <section class="panel"><div class="panel-head"><div><h2>Over ${state.over} · delivery evidence</h2><p>State and pressure are measured before the displayed outcome.</p></div><label class="select-wrap"><span class="field-label">Over</span><select id="over-select">${Array.from(grouped.keys()).map(o=>option(o,`Over ${o}`,state.over)).join('')}</select></label></div><div class="delivery-list"><table><thead><tr><th>Ball</th><th>Pressure</th><th>Wkts before</th><th>Batter / bowler</th><th>Outcome</th><th>Why this pressure?</th></tr></thead><tbody>${grouped.get(state.over).map(p=>`<tr><td>${esc(p[0])}</td><td><span class="pressure-badge ${p[1]>=55?'high':''}">${p[1]}</span></td><td>${p[2]}</td><td><strong>${esc(DATA.players[p[4]]?.name||p[4])}</strong><br><span class="subtle">${esc(DATA.players[p[5]]?.name||p[5])}</span></td><td>${p[6]?'<strong style="color:var(--pink)">Wicket</strong>':`${p[3]} bat run${p[3]===1?'':'s'}`}<br><span class="muted-note">${p[7]?'Retained legal ball':`${esc(p[8])} · excluded`}</span></td><td>${esc(p[9])}</td></tr>`).join('')}</tbody></table></div></section>`+caveat();
}
const meanScore=points=>points.reduce((s,p)=>s+p[1],0)/points.length;
function timelineChart(grouped){
  const x=o=>48+(o-1)*42,y=p=>217-p*1.85;let body='';
  for(const val of [0,25,50,75,100])body+=`<line class="chart-grid" x1="44" x2="900" y1="${y(val)}" y2="${y(val)}"/><text x="32" y="${y(val)+4}" text-anchor="end">${val}</text>`;
  for(const [over,points]of grouped){const p=meanScore(points);body+=`<rect x="${x(over)}" y="${y(p)}" width="27" height="${p*1.85}" rx="3" fill="${p>=55?PINK:'var(--chart-muted)'}" opacity="${over===state.over?1:.65}" data-over="${over}" role="button" tabindex="0" aria-label="Inspect over ${over}, pressure ${fmt(p,1)}"><title>Over ${over}: average pressure ${fmt(p,1)}; ${points.filter(p=>p[6]).length} wickets</title></rect><text x="${x(over)+13.5}" y="237" text-anchor="middle">${over}</text>${over===state.over?`<circle cx="${x(over)+13.5}" cy="250" r="3" fill="${PINK}"/>`:''}`;}
  body+=`<line x1="44" x2="900" y1="${y(55)}" y2="${y(55)}" stroke="${PINK}" stroke-dasharray="5 4" opacity=".7"/><text x="903" y="${y(55)+4}" fill="${PINK}">55</text><text x="460" y="272" text-anchor="middle">Over number (1–20)</text>`;
  return svg(body,940,280,'Pressure by over; select an over for delivery evidence');
}

function renderMethodology(){
  const m=DATA.meta;
  main.innerHTML=header('OPEN THE MODEL','Behind the selection.','Inspect the definition, calculations, exclusions and limits of the analysis.',`<a class="btn" href="data/METHODOLOGY.md" download>↓ Methodology .md</a><a class="btn primary" href="report.html" target="_blank" rel="noopener">Printable report ↗</a>`)
    + `<div class="method-grid"><section class="panel prose"><div class="eyebrow">01 / THE QUESTION</div><h2>Who repeatedly outperforms their context?</h2><p>The project ranks batters and bowlers in pivotal T20 situations and compares their pressure performance with their own ordinary-situation baseline. The Combined lists are the default submission output. IPL and T20I views are separate exploratory rankings.</p><div class="eyebrow" style="margin-top:25px">02 / THE PRESSURE DEFINITION</div><h2>Before the ball. Never after it.</h2><p>A shared phase-and-wicket score flags pivotal passages. It does not measure emotional pressure or imply equal difficulty for batting and bowling.</p><div class="table-wrap"><table><thead><tr><th>Signal known before delivery</th><th>Points</th></tr></thead><tbody><tr><td>Overs 1–6 / 7–15 / 16–18 / 19–20</td><td>10 / 20 / 60 / 75</td></tr><tr><td>3+ wickets lost by over 10</td><td>+30</td></tr><tr><td>Otherwise 4+ wickets lost, overs 11–15</td><td>+20</td></tr><tr><td>2+ wickets in previous 12 legal balls</td><td>+20</td></tr><tr><td>Knockout stage</td><td>+10</td></tr></tbody></table></div><div class="formula">Pressure ≥ 55 → high pressure. Maximum score: 100.</div><p>Death overs are a useful finishing-pressure proxy, but can occur in already-decided matches. Collapses identify pivotal passages and may make a bowler's task easier. Both limitations remain visible.</p><div class="eyebrow" style="margin-top:25px">03 / FAIRER COMPARISONS</div><h2>Context first, ranking second.</h2><p>Expected performance comes from deliveries with the same IPL/T20I format, phase and innings. Year and batting position or bowling type are included where a group has at least 200 balls. Small groups fall back to broader contexts. These descriptive expectations use the full historical sample.</p><p>Delivery impact gives 65% weight to standardized scoring/run prevention and 35% to standardized survival/wicket taking. Positive impact means above context average. The scoring and wicket components use the same legal-ball sample.</p><div class="formula">Rating = 50% pressure performance + 30% baseline uplift + 20% repeatability</div><p>Components are converted to percentiles within the eligible category and scope. Performance and uplift receive sample-size shrinkage. Repeatability is the smoothed fraction of above-context pressure matches. An 80 rating is not an 80% success probability.</p><div class="eyebrow" style="margin-top:25px">04 / EVIDENCE & RELIABILITY</div><h2>Enough opportunities to make a case.</h2><ul><li>At least 60 pressure balls and 60 ordinary balls.</li><li>At least 8 pressure matches with 6+ pressure balls in each.</li><li>Five alternatives: two pressure thresholds, two weighting schemes, and removal of each player's best pressure match.</li><li>Scenario ranges show ranking sensitivity, not confidence intervals.</li></ul><h3>Identity, photos and IPL availability</h3><p>Country labels use official profile nationality when available, otherwise international-team representation from the supplied mapping. Representation is not citizenship. Amber Pakistan flags request an individual IPL availability check; they never remove players or change ratings. Passport exceptions, registration and board clearances must be checked. <a href="https://www.cricbuzz.com/cricket-news/140773/mohammad-amir-rules-out-entering-ipl-auction" target="_blank" rel="noopener">Participation context</a>.</p><p>External profiles are dated snapshots, not a live roster service. Portraits load from the credited publisher; unavailable images show initials. Recent form uses the last eight retained appearances, sorted by date, within the selected scope and role. Situation buckets may overlap. Sample averages use retained legal-ball bat runs divided by striker dismissals (batting) or credited wickets (bowling), and are not official career averages.</p><h3>Known limitations</h3><ul>${m.limitations.map(l=>`<li>${esc(l)}</li>`).join('')}</ul></section>
    <aside class="stack" style="grid-template-columns:1fr"><section class="panel"><div class="panel-head"><div><h2>Data quality audit</h2><p>Exclusions are part of the result.</p></div>${tag('SOURCE CHECK','teal')}</div><div class="panel-body"><div class="audit-item"><span>Supplied delivery rows</span><strong>${fmt(m.source_rows)}</strong></div><div class="audit-item"><span>Retained legal deliveries</span><strong>${fmt(m.legal_balls)}</strong></div>${Object.entries(m.audit).map(([k,v])=>`<div class="audit-item"><span>${esc(k.replaceAll('_',' '))}</span><strong>${fmt(v)}</strong></div>`).join('')}<p class="muted-note" style="margin:15px 0 0">Counters describe different checks and are not all additive. Quarantined innings: ${m.quarantined_innings.map(q=>`${q.match_id}, innings ${q.innings}`).join('; ')||'None'}.</p></div></section><section class="panel why-card"><h3>The extras issue</h3><p class="muted-note">The field named <code>extras1_runs</code> behaves as a type code: ordinary deliveries carry 6, wides 2, byes 4. Treating those numbers as runs would corrupt every match total.</p><p class="muted-note">This version uses runs off the bat on identifiable legal balls. It does not invent team totals, chase targets or official economy.</p>${tag('DOCUMENTED LIMITATION','amber')}</section><section class="panel"><div class="panel-head"><div><h2>Eligibility explorer</h2><p>Why a player may be missing from the ranking</p></div></div><div class="panel-body"><div class="filters" style="margin-bottom:12px"><select id="excluded-role" aria-label="Excluded player category">${['batters','bowlers'].map(r=>option(r,r,state.role)).join('')}</select><select id="excluded-scope" aria-label="Excluded competition scope">${['Combined','IPL','T20I'].map(s=>option(s,s,state.scope)).join('')}</select></div><input type="search" class="audit-search" id="excluded-search" placeholder="Search excluded players…" aria-label="Search excluded players"><div class="audit-table"><table><thead><tr><th>Player</th><th>Eligibility issue</th></tr></thead><tbody id="excluded-body">${excludedRows('')}</tbody></table></div></div></section><section class="panel why-card"><h3>Reproduce the analysis</h3><p class="muted-note">Run the builder from the project folder:</p><code style="font-size:10px;word-break:break-word">python -m analysis.build --data-dir data/raw</code><p class="muted-note" style="margin:14px 0 0">Source fingerprints are in <code>reports/data_audit.json</code>. The report and CSVs are built from the same rankings as this dashboard.</p></section></aside></div>`;
}
function excludedRows(query){
  const list=DATA.excluded[state.scope][state.role].filter(r=>r.name.toLowerCase().includes(query.toLowerCase())).slice(0,60);
  return list.map(r=>`<tr><td><strong>${esc(r.name)}</strong><br>${r.pressure_balls} pressure balls<br>${r.pressure_matches} qualifying matches</td><td>${esc(r.reason)}</td></tr>`).join('')||'<tr><td colspan="2">No excluded players match.</td></tr>';
}

document.addEventListener('click',event=>{
  const el=event.target.closest('[data-page],[data-role],[data-select-player],[data-open-player],[data-open-match],[data-over],[data-action]');if(!el||!DATA)return;
  if(el.dataset.page){navigate(el.dataset.page);return;}
  if(el.dataset.role){state.role=el.dataset.role;state.player=null;state.search='';if(state.page==='players')navigate('players',{player:rows()[0]?.id});else render();return;}
  if(el.dataset.openPlayer){navigate('players',{player:Number(el.dataset.openPlayer)});return;}
  if(el.dataset.selectPlayer){state.player=Number(el.dataset.selectPlayer);document.getElementById('ranking-body').innerHTML=tableRows();document.getElementById('spotlight').innerHTML=spotlight(current());return;}
  if(el.dataset.openMatch){navigate('matches',{match:Number(el.dataset.openMatch),year:'All',innings:'1',over:null});return;}
  if(el.dataset.over){state.over=Number(el.dataset.over);renderMatchDetail(matchCache.get(state.match));return;}
  if(el.dataset.action==='export')exportRankings();
  if(el.dataset.action==='retry-match')renderMatches();
});
document.addEventListener('keydown',e=>{const el=e.target.closest('svg [role=button]');if(el&&['Enter',' '].includes(e.key)){e.preventDefault();el.dispatchEvent(new MouseEvent('click',{bubbles:true}));}});
document.addEventListener('change',event=>{
  const {id,value,checked}=event.target;if(!DATA)return;
  if(id==='scope-select'){state.scope=value;state.player=null;state.search='';render();}
  if(id==='all-players'){state.all=checked;document.getElementById('ranking-body').innerHTML=tableRows();}
  if(id==='profile-player')navigate('players',{player:Number(value)});
  if(id==='match-year'){state.year=value;state.match=null;state.over=null;renderMatches();}
  if(id==='match-select'){state.match=Number(value);state.over=null;renderMatches();}
  if(id==='innings-select'){state.innings=value;state.over=null;if(matchCache.has(state.match))renderMatchDetail(matchCache.get(state.match));else renderMatches();}
  if(id==='over-select'){state.over=Number(value);renderMatchDetail(matchCache.get(state.match));}
  if(id==='excluded-role'||id==='excluded-scope'){state[id==='excluded-role'?'role':'scope']=value;document.getElementById('excluded-body').innerHTML=excludedRows(document.getElementById('excluded-search').value);}
});
document.addEventListener('input',event=>{
  if(!DATA)return;
  if(event.target.id==='player-search'){state.search=event.target.value;document.getElementById('ranking-body').innerHTML=tableRows();}
  if(event.target.id==='excluded-search')document.getElementById('excluded-body').innerHTML=excludedRows(event.target.value);
});
window.addEventListener('hashchange',()=>{if(DATA)route();});
async function init(){
  try{
    const response=await fetch('data/dashboard.json');if(!response.ok)throw new Error(`Data request returned ${response.status}`);
    DATA=await response.json();
    const extras=await Promise.allSettled(['data/profiles.json','data/player_details.json','data/player_insights.json'].map(async url=>{const r=await fetch(url);if(!r.ok)throw new Error(url);return r.json();}));
    if(extras[0].status==='fulfilled') PROFILES=extras[0].value;
    if(extras[1].status==='fulfilled') DETAILS=extras[1].value;
    if(extras[2].status==='fulfilled') INSIGHTS=extras[2].value;
    document.getElementById('date-range').textContent=`${DATA.meta.date_from.slice(0,4)}–${DATA.meta.date_to.slice(0,4)} DATASET`;
    document.getElementById('sidebar-coverage').textContent=`${fmt(DATA.meta.analysed_matches)} matches · IPL + T20I`;
    route();
  }catch(error){main.innerHTML=`<div class="error-state"><div class="eyebrow">LET'S GET YOU RUNNING</div><h1>The dataset couldn't load.</h1><p>Start the project with <code>python app.py</code>, then open <a href="http://127.0.0.1:8501">http://127.0.0.1:8501</a>. Opening this HTML file directly will not load local JSON data.</p><p>If the generated data is missing, run <code>python -m analysis.build --data-dir data/raw</code>.</p><p class="muted-note">${esc(error.message)}</p></div>`;}
}
init();

/* Seeded empirical resampling. This is a conditional illustration, not a calibrated forecast. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.ScenarioEngine=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const empty=()=>Array(21).fill(0), sum=a=>a.reduce((x,y)=>x+y,0);
  function normalize(a){const n=sum(a);if(!n)throw new Error('No historical distribution is available.');return a.map(x=>x/n);}
  function shrink(counts,prior,k=60){const c=counts||empty(),n=sum(c);return c.map((x,i)=>(x+k*prior[i])/(n+k));}
  function phase(over){return over<=6?'Powerplay':over<=15?'Middle':'Death';}
  function pressure(over,lost,recent,knockout=false){let p=over<=6?10:over<=15?20:over<=18?60:75;if(over<=10&&lost>=3)p+=30;else if(over<=15&&lost>=4)p+=20;if(recent>=2)p+=20;if(knockout)p+=10;return Math.min(100,p);}
  function rng(seed){let a=seed>>>0;return ()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};}
  function tiltScoring(p,sr){
    if(sr==null)return p.slice();
    const live=sum(p.slice(0,7)),fixed=p.slice(7).reduce((s,x,i)=>s+x*(i%7),0);
    if(live<=0)return p.slice();
    const target=Math.max(0,Math.min(6,(sr/100-fixed)/live));
    function tilted(theta){const q=p.slice(0,7).map((x,r)=>x*Math.exp(theta*r)),n=sum(q);return q.map(x=>x/n*live);}
    let lo=-25,hi=25;
    for(let i=0;i<70;i++){const mid=(lo+hi)/2,q=tilted(mid),mean=q.reduce((s,x,r)=>s+x*r,0)/live;if(mean<target)lo=mid;else hi=mid;}
    return tilted((lo+hi)/2).concat(p.slice(7));
  }
  function distribution(model,bid,wid,ph,high,sr=null){
    const key=ph+'|'+(high?'H':'L');
    const global=normalize(model.league.All.map(x=>x+1e-6));
    const league=shrink(model.league[key],shrink(model.league[ph],global,200),200);
    const b=model.batters[bid],w=model.bowlers[wid];
    function profile(p,opponent){if(!p)return league;let q=shrink(p.contexts.All,league);q=shrink(p.contexts[ph],q);q=shrink(p.contexts[key],q);return opponent?shrink(p.versus[key+'|'+opponent],q):q;}
    const bp=profile(b,w?.style),wp=profile(w,b?.hand);
    let result=b&&w?bp.map((x,i)=>(x+wp[i])/2):b?bp:w?wp:league;
    if(b&&w)result=shrink(model.pairs[bid+':'+wid]?.[key],result,120);
    return b?tiltScoring(result,sr):result;
  }
  function validate(c){
    for(const [key,min,max] of [['overs',1,20],['wickets',0,10],['required',0,720],['quota',0,4]]){
      if(!Number.isInteger(c[key])||c[key]<min||c[key]>max)throw new Error(`${key} must be a whole number from ${min} to ${max}.`);
    }
    if(c.batter!=null&&c.bowler!=null&&String(c.batter)===String(c.bowler))throw new Error('Choose two different players.');
    if(c.quota>Math.ceil(c.overs/2))throw new Error('The selected bowler cannot bowl consecutive overs. Reduce the remaining quota.');
    if(c.sr!=null&&(!Number.isFinite(c.sr)||c.sr<0||c.sr>400))throw new Error('What-if strike rate must be between 0 and 400.');
  }
  function describe(a){a.sort((x,y)=>x-y);return {p10:a[Math.floor((a.length-1)*.1)],median:a[Math.floor((a.length-1)*.5)],p90:a[Math.floor((a.length-1)*.9)],mean:sum(a)/a.length};}
  function simulate(model,c,trials=2000){
    validate(c);
    if(!model.batters[c.batter]||!model.bowlers[c.bowler])throw new Error('Player evidence is unavailable in this competition.');
    if(!Number.isInteger(trials)||trials<1||trials>10000)throw new Error('Invalid simulation count.');
    const random=rng(c.seed??20261112),balls=c.overs*6,cache=new Map(),paths=Array.from({length:balls+1},()=>[]);
    const team=[],bat=[],batBalls=[],bowl=[],wkts=[],bowlBalls=[],used=[];
    let hits=0,survives=0;
    for(let trial=0;trial<trials;trial++){
      let runs=0,left=c.wickets,striker=1,partner=0,br=0,bb=0,wr=0,ww=0,wb=0,alive=true;
      const falls=c.collapse?[-1,-2]:[];
      paths[0].push(0);
      for(let ball=0;ball<balls;ball++){
        if(runs>=c.required||left===0){paths[ball+1].push(runs);continue;}
        const oi=Math.floor(ball/6),over=21-c.overs+oi,ph=phase(over);
        const selectedBowler=oi%2===0&&Math.floor(oi/2)<c.quota;
        const high=pressure(over,10-left,falls.filter(at=>ball-at<12).length,c.knockout)>=55;
        const cacheKey=[striker,selectedBowler,ph,high].join('|');
        if(!cache.has(cacheKey)){
          const p=distribution(model,striker?c.batter:null,selectedBowler?c.bowler:null,ph,high,striker?c.sr:null);
          let running=0;cache.set(cacheKey,p.map(x=>running+=x));
        }
        const u=random(),cum=cache.get(cacheKey);let outcome=cum.findIndex(x=>u<x);if(outcome<0)outcome=20;
        const scored=outcome%7,status=Math.floor(outcome/7);
        runs+=scored;if(striker){br+=scored;bb++;}if(selectedBowler){wr+=scored;wb++;if(status===1)ww++;}
        if(status){left--;falls.push(ball+1);if(striker)alive=false;striker=0;}
        if(scored%2)[striker,partner]=[partner,striker];
        if(ball%6===5)[striker,partner]=[partner,striker];
        paths[ball+1].push(runs);
      }
      if(runs>=c.required)hits++;if(alive)survives++;
      team.push(runs);bat.push(br);batBalls.push(bb);bowl.push(wr);wkts.push(ww);bowlBalls.push(wb);used.push(c.wickets-left);
    }
    const max=Math.max(...team),step=Math.max(1,Math.ceil((max+1)/10));
    const bins=Array.from({length:Math.max(1,Math.ceil((max+1)/step))},(_,i)=>({from:i*step,to:(i+1)*step-1,count:0}));
    for(const r of team)bins[Math.floor(r/step)].count++;
    const startOver=21-c.overs,ph=phase(startOver),key=ph+'|'+(pressure(startOver,10-c.wickets,c.collapse?2:0,c.knockout)>=55?'H':'L');
    const pair=model.pairs[c.batter+':'+c.bowler]||{},n=sum(pair[key]||[]);
    return {trials,seed:c.seed??20261112,hitRate:hits/trials,hitCount:hits,
      team:describe(team),batter:describe(bat),batterBalls:describe(batBalls),survival:survives/trials,
      bowlerRuns:describe(bowl),bowlerWickets:describe(wkts),bowlerBalls:describe(bowlBalls),wicketsUsed:describe(used),bins,
      trajectory:paths.map((a,i)=>({ball:i,...describe(a)})).filter(x=>x.ball%6===0),
      evidence:{context:key,pairBalls:n,pairAll:sum(pair.All||[]),pairWeight:n/(n+120),
        batterBalls:sum(model.batters[c.batter].contexts[key]||[]),bowlerBalls:sum(model.bowlers[c.bowler].contexts[key]||[])},
      schedule:Array.from({length:c.overs},(_,i)=>({over:startOver+i,selected:i%2===0&&Math.floor(i/2)<c.quota}))};
  }
  return {simulate,distribution,tiltScoring,validate,phase,pressure,describe};
});

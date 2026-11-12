'use strict';
const assert=require('node:assert/strict');
const E=require('../web/scenario-engine.js');
const hist=idx=>Array.from({length:21},(_,i)=>i===idx?100000:0);
function model(idx){const h=hist(idx),contexts={All:h,Powerplay:h,Middle:h,Death:h,'Death|H':h,'Middle|L':h,'Powerplay|L':h};return {league:contexts,batters:{1:{contexts,versus:{},hand:'RHB'}},bowlers:{2:{contexts,versus:{},style:'Right-arm pace'}},pairs:{}};}
const config={batter:1,bowler:2,overs:3,wickets:4,required:100,quota:2,seed:7};
let checks=0;function test(name,fn){fn();checks++;console.log('PASS '+name);}
test('strike rotation, exact balls and alternating spell',()=>{const r=E.simulate(model(1),config,100);assert.equal(r.team.median,18);assert.equal(r.batter.median,9);assert.equal(r.bowlerBalls.median,12);assert.deepEqual(r.schedule.filter(x=>x.selected).map(x=>x.over),[18,20]);});
test('target stops the innings',()=>{const r=E.simulate(model(1),{...config,required:1},100);assert.equal(r.team.median,1);assert.equal(r.batterBalls.median,1);assert.equal(r.hitRate,1);});
test('last wicket stops scoring and striker does not return',()=>{const r=E.simulate(model(7),{...config,wickets:1},100);assert.equal(r.team.median,0);assert.equal(r.bowlerWickets.median,1);assert.equal(r.batterBalls.median,1);assert.equal(r.survival,0);assert.equal(r.bowlerBalls.median,1);});
test('run-out dismissal is not bowler credited',()=>{const r=E.simulate(model(14),{...config,wickets:1},100);assert.equal(r.wicketsUsed.median,1);assert.equal(r.bowlerWickets.median,0);});
test('same seed reproduces all outcomes',()=>assert.deepEqual(E.simulate(model(1),config,200),E.simulate(model(1),config,200)));
test('zero wickets and already met target are safe boundaries',()=>{assert.equal(E.simulate(model(1),{...config,wickets:0},20).team.median,0);assert.equal(E.simulate(model(1),{...config,required:0},20).hitRate,1);});
test('SR override changes scoring but preserves wicket mass',()=>{const p=Array(21).fill(1/21),q=E.tiltScoring(p,240);assert.ok(Math.abs(q.reduce((a,b)=>a+b,0)-1)<1e-9);assert.deepEqual(q.slice(7),p.slice(7));assert.ok(q.every(x=>x>=0));assert.ok(Math.abs(q.reduce((s,x,i)=>s+x*(i%7),0)-2.4)<1e-6);});
test('invalid overs, quotas, players and SR are rejected',()=>{for(const change of [{overs:0},{overs:2.5},{quota:3},{bowler:1},{wickets:11},{sr:Infinity},{required:-1}])assert.throws(()=>E.simulate(model(1),{...config,...change},10));});
test('pressure uses only prior state',()=>{assert.equal(E.pressure(5,3,0),40);assert.equal(E.pressure(5,3,2),60);assert.equal(E.phase(16),'Death');assert.equal(E.pressure(19,0,0),75);});
test('bowler four-over cap and honest missing-pair fallback',()=>{const r=E.simulate(model(1),{...config,overs:20,quota:4,required:500},20);assert.equal(r.bowlerBalls.median,24);assert.equal(r.evidence.pairBalls,0);assert.equal(r.evidence.pairWeight,0);assert.equal(r.trajectory.at(-1).ball,120);});
console.log(checks+' engine checks passed.');

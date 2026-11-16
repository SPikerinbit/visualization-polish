import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/omen/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/_entry.js');
const {chromium}=require('playwright');
const dir='D:/vldb2027/output/algorithm_figures_redesign/revision_v3';
const data=JSON.parse(fs.readFileSync(dir+'/figure_data.json','utf8'));
const C=data.style;let a=[],serial=0;
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
function group(id,fn){a.push(`<g id="${id}" data-edit-group="${id}">`);fn();a.push('</g>');}
const txt=(x,y,s,size=26,color=C.ink,anchor='middle',extra='')=>a.push(`<text id="t${++serial}" x="${x}" y="${y}" text-anchor="${anchor}" font-size="${size}" fill="${color}" ${extra}>${esc(s)}</text>`);
const ln=(x1,y1,x2,y2,color=C.line,w=C.stroke,extra='')=>a.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${w}" ${extra}/>`);
const curve=(d,col=C.line,w=1.8,extra='')=>a.push(`<path d="${d}" fill="none" stroke="${col}" stroke-width="${w}" ${extra}/>`);
function node(x,y,v,type='normal',r=20){
 const st=type==='emitted'?[C.blue,'white',C.blue]:type==='retained'?['white',C.muted,C.muted]:type==='unread'?[C.unread,C.unreadText,'none']:[C.node,'white','none'];
 a.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="${st[0]}" stroke="${st[2]}" stroke-width="1.8"/>`);txt(x,y+8,v,r<19?22:25,st[1]);
}
function row(id,cx,y,values,type='normal',step=48,r=20){group(id,()=>values.forEach((v,i)=>node(cx+(i-(values.length-1)/2)*step,y,v,Array.isArray(type)?type[i]:type,r)));}
function capsule(id,cx,y,values,type='normal',step=43,r=19){group(id,()=>{const w=Math.max(1,values.length)*step+7;a.push(`<rect x="${cx-w/2}" y="${y-25}" width="${w}" height="50" rx="25" fill="white" stroke="#c1c7cd" stroke-width="1.3"/>`);if(!values.length)txt(cx,y+8,'∅',25,C.unreadText);values.forEach((v,i)=>node(cx+(i-(values.length-1)/2)*step,y,v,Array.isArray(type)?type[i]:type,r));});}
function callbox(id,x,y,w,h){group(id,()=>a.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14" fill="none" stroke="${C.red}" stroke-width="2.2" stroke-dasharray="${C.dash}"/>`));}
function mergebox(id,cx,y,w=100,h=40,label=''){group(id,()=>{a.push(`<rect x="${cx-w/2}" y="${y-h/2}" width="${w}" height="${h}" rx="12" fill="white" stroke="${C.line}" stroke-width="1.8"/>`);if(label)txt(cx,y+9,label,26,C.ink);});}
function openArrow(id,x,y,w=50){group(id,()=>a.push(`<path d="M${x},${y-10} h${w-20} v-10 l20,20 -20,20 v-10 h-${w-20} Z" fill="white" stroke="${C.ink}" stroke-width="1.7" stroke-linejoin="round"/>`));}
function smoothLTPointer(id,x1,y1,x2,y2){
 // Same physical dimensions and contour as the single-column Pointer rule figure.
 const scale=(1700/178)/(1000/88),r=(1000/(88/25.4*72)*1.4/2)*scale;
 const length=Math.hypot(x2-x1,y2-y1),angle=Math.atan2(y2-y1,x2-x1)*180/Math.PI;
 const shoulder=length-13.5*scale,neck=length-16*scale;
 const d=`M${r},${-r} H${neck} C${neck+2*scale},${-r} ${shoulder-1.5*scale},${-5.4*scale} ${shoulder+scale},${-5.4*scale} C${shoulder+3.3*scale},${-5.4*scale} ${length-3*scale},${-1.6*scale} ${length-.7*scale},${-.45*scale} Q${length+.1*scale},0 ${length-.7*scale},${.45*scale} C${length-3*scale},${1.6*scale} ${shoulder+3.3*scale},${5.4*scale} ${shoulder+scale},${5.4*scale} C${shoulder-1.5*scale},${5.4*scale} ${neck+2*scale},${r} ${neck},${r} H${r} Q0,${r} 0,0 Q0,${-r} ${r},${-r} Z`;
 group(id,()=>a.push(`<path transform="translate(${x1} ${y1}) rotate(${angle})" d="${d}" fill="#303840"/>`));
}
function bracket(x1,x2,y,label,col=C.muted){curve(`M${x1},${y-5} V${y} H${x2} V${y-5}`,col,1.4);txt((x1+x2)/2,y+28,label,22,col);}
function pathFrame(id,points,w=54){group(id,()=>{const [fx,fy]=points[0],[lx,ly]=points.at(-1);let d=`M${fx+w},${fy}`;for(let i=1;i<points.length;i++){const[p,q]=points[i-1],[x,y]=points[i],c=(y-q)*.63;d+=` C${p+w},${q+c} ${x+w},${y-c} ${x+w},${y}`;}d+=` C${lx+w},${ly+46} ${lx-w},${ly+46} ${lx-w},${ly}`;for(let i=points.length-2;i>=0;i--){const[p,q]=points[i+1],[x,y]=points[i],c=(q-y)*.63;d+=` C${p-w},${q-c} ${x-w},${y+c} ${x-w},${y}`;}d+=` C${fx-w},${fy-46} ${fx+w},${fy-46} ${fx+w},${fy} Z`;curve(d,C.red,2.2,`stroke-dasharray="${C.dash}"`);});}
function begin(name,w,h,description){a=[];serial=0;a.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img"><title>${esc(name)}</title><desc>${esc(description)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1L9 5L1 9Z" fill="${C.ink}"/></marker><marker id="gray-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1L9 5L1 9Z" fill="${C.line}"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="${C.font}">`);}
function end(name){a.push('</g></svg>');const svg=a.join('\n');fs.writeFileSync(`${dir}/${name}.svg`,svg);return svg;}
const figures=[];
// Figure 1: preserve the original 16-item example and two-way merge schedule.
{
 const {width:w,height:h,chunkCenters:xs}=data.layout.overview;begin('Run generation and iterative merging',w,h,'Four disjoint chunks are individually ranked, then their sorted runs are merged in two passes. Red dashed boxes denote single listwise calls; merge junctions can require multiple calls.');
 a.push('<g transform="translate(0 -45)">');
 xs.forEach((x,i)=>{txt(x,83,'C'+['₁','₂','₃','₄'][i],25,C.muted);row(`chunk-${i+1}`,x,127,data.chunks[i],'normal',53);callbox(`rank-call-${i+1}`,x-119,96,238,62);ln(x,168,x,206,C.line,1.8,'marker-end="url(#gray-arrow)"');row(`run-${i+1}`,x,242,data.runs[i],'normal',53);txt(x-130,250,'R'+['₁','₂','₃','₄'][i],26,C.muted,'end');});
 txt(30,337,'Merge pass 1',26,C.ink,'start');
 const qs=[];[0,2].forEach((b,j)=>{const cx=(xs[b]+xs[b+1])/2;ln(xs[b],269,cx-25,317);ln(xs[b+1],269,cx+25,317);mergebox(`merge-pass1-${j+1}`,cx,337,180,40,'MergeGroup');ln(cx,357,cx,385,C.line,1.8,'marker-end="url(#gray-arrow)"');const q=[...data.runs[b],...data.runs[b+1]].sort((a,b)=>a-b);qs.push({cx,q});row(`intermediate-run-${j+1}`,cx,423,q,'normal',43);txt(cx-183,431,'Q'+['₁','₂'][j],26,C.muted,'end');});
 txt(30,520,'Merge pass 2',26,C.ink,'start');const cx=(qs[0].cx+qs[1].cx)/2;qs.forEach((q,i)=>ln(q.cx,451,cx+(i?25:-25),500));mergebox("merge-pass2",cx,520,180,40,'MergeGroup');ln(cx,540,cx,576,C.line,1.8,'marker-end="url(#gray-arrow)"');row('final-order',cx,614,Array.from({length:16},(_,i)=>i+1),'emitted',47);txt(cx-396,623,'Π',31,C.ink);group('overview-legend',()=>{callbox('legend-call',680,666,51,23);txt(744,686,'one listwise call',23,C.muted,'start');});
 a.push('</g>');
 figures.push({name:'algo1_exp',title:'Algorithm 1',width:w,height:h,svg:end('algo1_exp')});
}
// Generate the complete SD trace. Retained candidates keep their identities.
const sdTrace=[],positions=[0,0,0,0];let priorRetained=new Set();
while(positions.some((p,i)=>p<data.runs[i].length)){
 const active=positions.map((p,i)=>p<data.runs[i].length?i:-1).filter(i=>i>=0),quota=Math.floor(data.sd.m/active.length);
 const windows=data.runs.map((r,i)=>r.slice(positions[i],positions[i]+quota));const candidates=windows.flat().sort((a,b)=>a-b);const counts=[0,0,0,0],emit=[];
 for(const v of candidates){const i=data.runs.findIndex(r=>r.includes(v));emit.push(v);counts[i]++;if(counts[i]===windows[i].length&&positions[i]+windows[i].length<data.runs[i].length)break;}
 const retained=candidates.slice(emit.length);sdTrace.push({positions:[...positions],windows,candidates,emit,retained,priorRetained:[...priorRetained],unread:data.runs.map((r,i)=>r.slice(positions[i]+windows[i].length))});positions.forEach((_,i)=>positions[i]+=counts[i]);priorRetained=new Set(retained);
}
if(sdTrace.map(s=>s.emit.length).join(',')!=='5,5,6')throw Error('SD trace differs from original');
if(sdTrace.flatMap(s=>s.emit).join(',')!==Array.from({length:16},(_,i)=>i+1).join(','))throw Error('SD emitted order invalid');
{
 const {width:w,height:h,panelStarts}=data.layout.sd;begin('SD multi-way merge',w,h,'Three rounds of merging four sorted runs. Each merge root connects all run-prefix leaves. Filled blue items are safely emitted, hollow items are retained and re-enter the next call.');
 sdTrace.forEach((s,j)=>{const x=panelStarts[j],cx=x+260,leaf=[x+65,x+195,x+325,x+455];txt(cx,39,`Round ${j+1}`,29,C.ink,'middle','font-weight="600"');
  const types=s.candidates.map((v,i)=>i<s.emit.length?'emitted':'retained');row(`round-${j+1}-ranked`,cx,104,s.candidates,types,52);
  if(s.retained.length){const cut=cx-(s.candidates.length-1)*26+(s.emit.length-.5)*52;ln(cut,75,cut,133,C.ink,1.5,'stroke-dasharray="4 4"');}
  ln(cx,174,cx,137,C.line,1.8,'marker-end="url(#gray-arrow)"');a.push(`<circle cx="${cx}" cy="181" r="6" fill="${C.line}"/>`);leaf.forEach(lx=>ln(cx,181,lx,280));
  s.windows.forEach((win,i)=>{const retained=s.priorRetained;capsule(`round-${j+1}-run-${i+1}`,leaf[i],305,win,win.map(v=>retained.includes(v)?'retained':'normal'));txt(leaf[i],263,'R'+['₁','₂','₃','₄'][i],23,C.muted);if(s.unread[i].length){ln(leaf[i],341,leaf[i],361,'#c5cbd1',1.2);row(`round-${j+1}-unread-${i+1}`,leaf[i],392,s.unread[i],'unread',39,17);}else txt(leaf[i],401,'∅',26,C.unreadText);});
  callbox(`round-${j+1}-call`,x+9,273,502,65);
  if(s.retained.length){const left=cx-(s.candidates.length-1)*26+s.emit.length*52-20,right=cx+(s.candidates.length-1)*26+20,ex=panelStarts[j+1]+13;group(`round-${j+1}-retained-transfer`,()=>curve(`M${left},139 H${right} C${right+72},139 ${x+545},251 ${ex},276`,C.line,1.8,'stroke-linecap="round" marker-end="url(#gray-arrow)"'));}
 });
 
 a.push('<g transform="translate(0 -175)">');group('sd-legend',()=>{callbox('sd-legend-call',405,640,48,23);txt(466,661,'one call',23,C.muted,'start');node(747,652,5,'emitted',17);txt(776,661,'emitted',23,C.muted,'start');node(1052,652,7,'retained',17);txt(1081,661,'retained',23,C.muted,'start');});
 a.push('</g>');
 figures.push({name:'sd_merge',title:'SD merge',width:w,height:h,svg:end('sd_merge')});
}
// Unified LT(k,h): persistent losers and logical-child dependency pointers.
function buildTree(lo,hi){if(hi-lo===1)return{lo,hi,next:2,winner:data.runs[lo].slice(0,2)};const l=buildTree(lo,(lo+hi)/2),r=buildTree((lo+hi)/2,hi),z=[...l.winner,...r.winner].sort((a,b)=>a-b);return{lo,hi,l,r,winner:z.slice(0,2),loser:z.slice(2),pointer:l.winner.at(-1)<r.winner.at(-1)?'l':'r'};}
const lt=buildTree(0,4),ltBefore=structuredClone(lt);const pathBefore=[];let v=lt;while(v.l){pathBefore.push(v);v=v[v.pointer];}pathBefore.push(v);
const input=[...data.runs[v.lo].slice(v.next,v.next+2),...pathBefore.slice(0,-1).flatMap(n=>n.loser)];
function refresh(n){if(!n.l){n.winner=data.runs[n.lo].slice(n.next,n.next+2);n.next+=n.winner.length;return n.winner;}const old=n.loser,through=refresh(n[n.pointer]),z=[...through,...old].sort((a,b)=>a-b);if(through.at(-1)>old.at(-1))n.pointer=n.pointer==='l'?'r':'l';n.winner=z.slice(0,2);n.loser=z.slice(2);return n.winner;}
refresh(lt);
if(input.sort((a,b)=>a-b).join(',')!=='3,4,5,6,7,14'||lt.winner.join(',')!=='3,4'||lt.pointer!=='r'||lt.l.pointer!=='l')throw Error('LT pointer replay mismatch');
{
 const {width:w,height:h,panelStarts}=data.layout.lt;begin('Unified pointer-guided LT',w,h,'An h=2 loser-tree example shows state after initialization, a pointer-guided path refresh, and the new loser and pointer state. The independent node-replay figure explains the pointer rule.');
 function drawTree(state,x,mode){const cx=x+260,leaf=[x+65,x+195,x+325,x+455];const X=n=>n.hi-n.lo===4?cx:n.hi-n.lo===2?(leaf[n.lo]+leaf[n.hi-1])/2:leaf[n.lo];const Y=n=>n.hi-n.lo===4?217:n.hi-n.lo===2?340:477;const active=[];let cur=state;while(cur.l){active.push(cur);cur=cur[cur.pointer];}active.push(cur);
  function edges(n){if(!n.l)return;for(const side of ['l','r'])ln(X(n),Y(n),X(n[side]),Y(n[side]));edges(n.l);edges(n.r);}edges(state);
  function pointers(n){if(!n.l)return;const child=n[n.pointer],px=X(n),py=Y(n),qx=X(child),qy=Y(child),dx=qx-px,dy=qy-py;const start=.25,end=.72;smoothLTPointer(`${mode}-pointer-${n.lo}-${n.hi}`,px+dx*start,py+dy*start,px+dx*end,py+dy*end);pointers(n.l);pointers(n.r);}pointers(state);
  function nodes(n){if(n.l){capsule(`${mode}-loser-${n.lo}-${n.hi}`,X(n),Y(n),n.loser,mode==='refresh'&&!active.includes(n)?'unread':'normal');nodes(n.l);nodes(n.r);}else{const next=data.runs[n.lo].slice(n.next,n.next+2);capsule(`${mode}-run-${n.lo+1}`,X(n),Y(n),next,mode==='refresh'&&active.includes(n)?'normal':'unread');txt(X(n),532,'R'+['₁','₂','₃','₄'][n.lo],23,C.muted);}}nodes(state);
  if(mode==='refresh'){row('lt-rank-map',cx,100,input,'normal',48);txt(cx-178,108,'ρ:',28,C.muted);pathFrame('lt-refresh-call',active.map(n=>[X(n),Y(n)]),54);}else{ln(cx,189,cx,129,C.line,1.8,'marker-end="url(#gray-arrow)"');capsule(`${mode}-winner`,cx,100,state.winner,'emitted');}
 }
 ['(a) Initialized state','(b) One path refresh','(c) Updated state'].forEach((label,i)=>txt(panelStarts[i]+260,39,label,29,C.ink,'middle','font-weight="600"'));
 drawTree(ltBefore,panelStarts[0],'before');drawTree(ltBefore,panelStarts[1],'refresh');drawTree(lt,panelStarts[2],'after');
 openArrow('lt-step-1',535,285,39);openArrow('lt-step-2',1100,285,39);
 group('lt-legend',()=>{callbox('lt-legend-call',390,587,48,23);txt(451,608,'one call',23,C.muted,'start');smoothLTPointer('lt-legend-pointer',700,599,748,599);txt(763,608,'pointer',23,C.muted,'start');node(1052,599,3,'emitted',17);txt(1081,608,'emitted',23,C.muted,'start');});
 figures.push({name:'lt_unified',title:'Unified LT',width:w,height:h,svg:end('lt_unified')});
}
function localReplay(L,R){const z=[...L.map(v=>({v,slot:'L'})),...R.map(v=>({v,slot:'R'}))].sort((a,b)=>a.v-b.v);const count={L:0,R:0};let pointer,index;z.forEach((item,i)=>{count[item.slot]++;if(pointer===undefined&&count[item.slot]===2){pointer=item.slot;index=i;}});return{z,winner:z.slice(0,2).map(x=>x.v),loser:z.slice(2).map(x=>x.v),pointer,index};}
const buildReplay=localReplay(data.pointer.build.left,data.pointer.build.right);
const refreshReplay=localReplay(data.pointer.refresh.parent,data.pointer.refresh.rightNew);
if(buildReplay.pointer!=='R'||buildReplay.loser.join(',')!=='5,7'||refreshReplay.pointer!=='L'||refreshReplay.winner.join(',')!=='5,6'||refreshReplay.loser.join(',')!=='7,14')throw Error('Node replay trace invalid');
figures.push({name:'pointer_rule',title:'Node replay · pointer rule',width:1000,height:710,svg:fs.readFileSync(dir+'/pointer_rule.svg','utf8')});
fs.writeFileSync(dir+'/validated_states.json',JSON.stringify({sd:sdTrace,lt:{before:ltBefore,input,after:lt},pointer:{build:buildReplay,refresh:refreshReplay}},null,2));
// Import the established Intro artwork, retaining its editable vector groups.
figures.unshift({name:'intro_execution',title:'Intro · Pairwise → Listwise',width:1660,height:880,svg:fs.readFileSync(dir+'/intro_execution.svg','utf8')});
// A small offline workbench keeps every SVG text, shape and logical group editable.
const editorScript=`let editing=false,drag=null,undo=[];const btn=document.querySelector('#edit');btn.onclick=()=>{editing=!editing;btn.textContent=editing?'结束编辑':'编辑文字与位置';document.body.classList.toggle('editing',editing)};document.addEventListener('dblclick',e=>{if(!editing||e.target.tagName.toLowerCase()!=='text')return;const v=prompt('修改文字',e.target.textContent);if(v!==null){undo.push([e.target,'text',e.target.textContent]);e.target.textContent=v}});document.addEventListener('pointerdown',e=>{if(!editing||e.button!==0)return;const g=e.target.closest('[data-edit-group]');if(!g)return;const svg=g.ownerSVGElement,p=new DOMPoint(e.clientX,e.clientY).matrixTransform(svg.getScreenCTM().inverse());const old=g.getAttribute('transform')||'';drag={g,svg,p,old};});document.addEventListener('pointermove',e=>{if(!drag)return;const p=new DOMPoint(e.clientX,e.clientY).matrixTransform(drag.svg.getScreenCTM().inverse());drag.g.setAttribute('transform','translate('+(p.x-drag.p.x)+' '+(p.y-drag.p.y)+') '+drag.old)});document.addEventListener('pointerup',()=>{if(drag){if((drag.g.getAttribute('transform')||'')!==drag.old)undo.push([drag.g,'transform',drag.old]);drag=null}});document.querySelector('#undo').onclick=()=>{const u=undo.pop();if(!u)return;if(u[1]==='text')u[0].textContent=u[2];else u[0].setAttribute('transform',u[2])};function save(svg,name){const out=svg.cloneNode(true);out.setAttribute('xmlns','http://www.w3.org/2000/svg');const b=new Blob([new XMLSerializer().serializeToString(out)],{type:'image/svg+xml'}),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download=name+'.svg';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)}document.querySelectorAll('[data-save]').forEach(b=>b.onclick=()=>save(b.closest('section').querySelector('svg'),b.dataset.save));`;
const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Intro 与算法图 · 可编辑工作台</title><style>body{margin:0;background:#f4f5f6;color:#262b30;font:16px/1.6 Arial,'Microsoft YaHei',sans-serif}header{position:sticky;top:0;z-index:2;background:#ffffffed;border-bottom:1px solid #ddd;padding:14px 28px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}main{max-width:1720px;margin:auto;padding:20px}h2{font-size:22px;font-weight:500}section{margin:16px 0 44px}figure{background:white;padding:20px;margin:10px 0}svg{width:100%;height:auto;display:block}button,a{font:inherit;color:#526779;background:white;border:1px solid #c7cfd7;border-radius:3px;padding:6px 13px;text-decoration:none;cursor:pointer}small{color:#7a838b}.editing [data-edit-group]{cursor:move}.editing text{cursor:text}.editing [data-edit-group]:hover{filter:drop-shadow(0 0 2px #b7c9da)}nav{display:flex;gap:12px;margin-bottom:14px}.editing svg{touch-action:none;user-select:none}@media print{header,nav,h2{display:none}body{background:white}figure{padding:0}section{break-after:page}}</style><header><strong>Intro 与算法图</strong><button id="edit">编辑文字与位置</button><button id="undo">撤销</button><small>双击文字修改；拖动元素或分组；下载 SVG 保存。连接线可在矢量编辑器中进一步调整。</small></header><main>${figures.map(f=>`<section><h2>${f.title}</h2><nav><button data-save="${f.name}">保存 SVG</button><a href="${f.name}.pdf">PDF</a><a href="${f.name}.png">PNG</a></nav><figure>${f.svg}</figure></section>`).join('')}</main><script>${editorScript}</script></html>`;
fs.writeFileSync(dir+'/index.html',html);
const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
const page=await browser.newPage({deviceScaleFactor:2});
for(const f of figures.filter(f=>!process.argv.includes('--workbench-only') && (process.argv.includes('--lt-only')?['lt_unified']:['algo1_exp','sd_merge','lt_unified']).includes(f.name))){await page.setViewportSize({width:f.width,height:f.height});await page.setContent(`<style>body{margin:0}svg{display:block}</style>${f.svg}`);await page.screenshot({path:`${dir}/${f.name}.png`});const pw=f.name==='pointer_rule'?88:178;const ht=pw*f.height/f.width;await page.setContent(`<title>${f.title}</title><style>@page{size:${pw}mm ${ht}mm;margin:0}body{margin:0}svg{width:${pw}mm;height:${ht}mm;display:block}</style>${f.svg}`);await page.pdf({path:`${dir}/${f.name}.pdf`,preferCSSPageSize:true,printBackground:true});}
await page.setViewportSize({width:1500,height:1000});await page.goto('file:///'+dir+'/index.html');await page.screenshot({path:dir+'/workbench_preview.png',fullPage:true});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));
await page.locator('#edit').click();if(!await page.locator('body').evaluate(e=>e.classList.contains('editing')))throw Error('Edit toggle failed');
const editGroup=page.locator('#chunk-1');await editGroup.scrollIntoViewIfNeeded();const bb=await editGroup.boundingBox();await page.mouse.move(bb.x+25,bb.y+20);await page.mouse.down();await page.mouse.move(bb.x+45,bb.y+30);await page.mouse.up();if(!(await editGroup.getAttribute('transform'))?.includes('translate'))throw Error('Drag failed');await page.locator('#undo').click();if((await editGroup.getAttribute('transform'))!=='')throw Error('Undo failed');
const download=page.waitForEvent('download');await page.locator('[data-save="algo1_exp"]').click();const saved=await download;if(saved.suggestedFilename()!=='algo1_exp.svg')throw Error('SVG save failed');
if(errors.length)throw Error(errors.join('\n'));await browser.close();console.log('Five figures available. Numeric SD/LT checks and SVG editor drag, undo, save checks passed.');

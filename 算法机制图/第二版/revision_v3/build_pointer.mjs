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
function bracket(x1,x2,y,label,col=C.muted){curve(`M${x1},${y-5} V${y} H${x2} V${y-5}`,col,1.4);txt((x1+x2)/2,y+28,label,22,col);}
function pathFrame(id,points,w=54){group(id,()=>{const [fx,fy]=points[0],[lx,ly]=points.at(-1);let d=`M${fx+w},${fy}`;for(let i=1;i<points.length;i++){const[p,q]=points[i-1],[x,y]=points[i],c=(y-q)*.63;d+=` C${p+w},${q+c} ${x+w},${y-c} ${x+w},${y}`;}d+=` C${lx+w},${ly+46} ${lx-w},${ly+46} ${lx-w},${ly}`;for(let i=points.length-2;i>=0;i--){const[p,q]=points[i+1],[x,y]=points[i],c=(q-y)*.63;d+=` C${p-w},${q-c} ${x-w},${y+c} ${x-w},${y}`;}d+=` C${fx-w},${fy-46} ${fx+w},${fy-46} ${fx+w},${fy} Z`;curve(d,C.red,2.2,`stroke-dasharray="${C.dash}"`);});}
function begin(name,w,h,description){a=[];serial=0;a.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img"><title>${esc(name)}</title><desc>${esc(description)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1L9 5L1 9Z" fill="${C.ink}"/></marker><marker id="gray-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1L9 5L1 9Z" fill="${C.line}"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="${C.font}">`);}
function end(name){a.push('</g></svg>');const svg=a.join('\n');fs.writeFileSync(`${dir}/${name}.svg`,svg);return svg;}
function localReplay(L,R){const z=[...L.map(v=>({v,slot:'L'})),...R.map(v=>({v,slot:'R'}))].sort((a,b)=>a.v-b.v);const count={L:0,R:0};let pointer,index;z.forEach((item,i)=>{count[item.slot]++;if(pointer===undefined&&count[item.slot]===2){pointer=item.slot;index=i;}});return{z,winner:z.slice(0,2).map(x=>x.v),loser:z.slice(2).map(x=>x.v),pointer,index};}
const buildReplay=localReplay(data.pointer.build.left,data.pointer.build.right);
const refreshReplay=localReplay(data.pointer.refresh.parent,data.pointer.refresh.rightNew);
if(buildReplay.pointer!=='R'||buildReplay.loser.join(',')!=='5,7'||refreshReplay.pointer!=='L'||refreshReplay.winner.join(',')!=='5,6'||refreshReplay.loser.join(',')!=='7,14')throw Error('Node replay trace invalid');

const w=1000,h=710;
const treeColor='#AAB1B7',pointerColor='#303840';
// Convert the requested print-point widths to this 1000-unit, 88-mm canvas.
const pt=1000/(88/25.4*72),treeWidth=.8*pt,pointerWidth=1.4*pt;
begin('Node replay and pointer update',w,h,'Build and refresh of the same node. The old right pointer places the incoming right segment in slot R and the retained parent segment in slot L. The first exhausted replay slot determines the updated pointer. Blue is the winner passed upward; pale items are next unread.');
// A single filled contour avoids a shaft protruding through a separate marker.
// Curved shoulders join the shaft to the tapered, subtly rounded arrowhead.
function smoothPointer(id,x1,y1,x2,y2){
 const length=Math.hypot(x2-x1,y2-y1),angle=Math.atan2(y2-y1,x2-x1)*180/Math.PI;
 const r=pointerWidth/2,shoulder=length-13.5,neck=length-16;
 const d=`M${r},${-r} H${neck} C${neck+2},${-r} ${shoulder-1.5},-5.4 ${shoulder+1},-5.4 C${shoulder+3.3},-5.4 ${length-3},-1.6 ${length-.7},-.45 Q${length+.1},0 ${length-.7},.45 C${length-3},1.6 ${shoulder+3.3},5.4 ${shoulder+1},5.4 C${shoulder-1.5},5.4 ${neck+2},${r} ${neck},${r} H${r} Q0,${r} 0,0 Q0,${-r} ${r},${-r} Z`;
 group(id,()=>a.push(`<path transform="translate(${x1} ${y1}) rotate(${angle})" d="${d}" fill="${pointerColor}"/>`));
}
[145,500,855].forEach((x,i)=>txt(x,32,['State','Node replay','Updated state'][i],29,C.ink,'middle','font-weight="600"'));
function boundary(dx,dy,count){
 const core=(Math.max(1,count)*43+7)/2-25;
 let lo=0,hi=1;
 for(let i=0;i<40;i++){const t=(lo+hi)/2;const q=Math.max(Math.abs(dx*t)-core,0);if(q*q+(dy*t)**2<=625)lo=t;else hi=t;}
 return hi;
}
function tree(id,cx,dy,parent,left,right,pointer,winner=null){
 const py=180+dy,cy=277+dy,lx=cx-72,rx=cx+72;
 for(const [side,ex,items] of [['L',lx,left],['R',rx,right]]){
  const dx=ex-cx,ey=cy-py,start=boundary(dx,ey,parent.length),end=1-boundary(-dx,-ey,items.length);
  ln(cx+dx*start,py+ey*start,cx+dx*end,py+ey*end,treeColor,treeWidth);
  if(pointer===side)smoothPointer(id+'-pointer',cx+dx*(start+.035),py+ey*(start+.035),cx+dx*(end-.025),py+ey*(end-.025));
 }
 if(parent.length)capsule(id+'-parent',cx,py,parent);else capsule(id+'-parent',cx,py,[]);
 if(!winner)txt(cx,py-37,'P',24,C.ink);
 capsule(id+'-left',lx,cy,left,id==='build-before'?'normal':'unread');
 capsule(id+'-right',rx,cy,right,id.endsWith('after')?'unread':'normal');
 txt(lx-29,cy-39,'L',23,C.ink);txt(rx+29,cy-39,'R',23,C.ink);
 if(winner){ln(cx,py-28,cx,135+dy,C.line,1.8,'marker-end="url(#gray-arrow)"');capsule(id+'-winner',cx,104+dy,winner,'emitted');}
}
function trace(id,dy,L,R,mapping,result){
 txt(425,105+dy,mapping[0],24,C.ink);txt(575,105+dy,mapping[1],24,C.ink);
 capsule(id+'-slot-L',425,142+dy,L);capsule(id+'-slot-R',575,142+dy,R);
 ln(500,176+dy,500,195+dy,C.line,1.6,'marker-end="url(#gray-arrow)"');
 result.z.forEach((item,i)=>{const x=398+i*68;txt(x,219+dy,item.slot,22,C.muted);node(x,248+dy,item.v,i<2?'emitted':'normal',20);});
 txt(432,301+dy,'winner',22,C.muted);txt(578,301+dy,'loser',22,C.muted);
 const ex=398+result.index*68;
 group(id+'-exhaustion',()=>{ln(ex-17,275+dy,ex+17,275+dy,C.red,1.8);curve(`M${ex},${278+dy} V${310+dy} H500`,C.red,1.1);txt(500,332+dy,result.pointer+' Exhaustion point',21,C.red);});
}
for(const [dy,title,id,L,R,mapping,result] of [
 [0,'(a) Build','build',data.pointer.build.left,data.pointer.build.right,['L','R'],buildReplay],
 [315,'(b) Refresh','refresh',data.pointer.refresh.parent,data.pointer.refresh.rightNew,['P → L','R → R'],refreshReplay]
]){
 txt(24,70+dy,title,23,C.muted,'start');
 if(id==='build'){
  tree('build-before',145,dy,[],L,R,null);
  tree('build-after',855,dy,result.loser,data.pointer.refresh.leftUnread,data.pointer.refresh.rightNew,result.pointer,result.winner);
 }else{
  tree('refresh-before',145,dy,L,data.pointer.refresh.leftUnread,R,'R');
  tree('refresh-after',855,dy,result.loser,data.pointer.refresh.leftUnread,[],result.pointer,result.winner);
 }
 trace(id+'-replay',dy,L,R,mapping,result);
 group(id+'-transition',()=>{ln(280,204+dy,326,204+dy,C.line,1.8,'marker-end="url(#gray-arrow)"');ln(674,204+dy,720,204+dy,C.line,1.8,'marker-end="url(#gray-arrow)"');});
}
group('pointer-rule-legend',()=>{smoothPointer('legend-pointer',95,686,142,686);txt(155,694,'pointer',23,C.muted,'start');node(397,686,1,'emitted',16);txt(424,694,'winner',23,C.muted,'start');node(667,686,12,'unread',16);txt(694,694,'next unread',23,C.muted,'start');});
const svg=end('pointer_rule');
let html=fs.readFileSync(dir+'/index.html','utf8');
let matched=0;
html=html.replace(/<section><h2>Node replay · pointer rule<\/h2>[\s\S]*?<\/section>/,section=>{matched++;return section.replace(/<figure>[\s\S]*?<\/figure>/,`<figure>${svg}</figure>`);});
if(matched!==1)throw Error('Pointer section not found');
fs.writeFileSync(dir+'/index.html',html);
const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
try{
 const page=await browser.newPage({viewport:{width:w,height:h},deviceScaleFactor:2});
 await page.setContent(`<style>body{margin:0}svg{display:block}</style>${svg}`);
 await page.screenshot({path:dir+'/pointer_rule.png'});
 const ht=88*h/w;
 await page.setContent(`<style>@page{size:88mm ${ht}mm;margin:0}body{margin:0}svg{width:88mm;height:${ht}mm;display:block}</style>${svg}`);
 await page.pdf({path:dir+'/pointer_rule.pdf',preferCSSPageSize:true,printBackground:true});
}finally{await browser.close();}
console.log('Pointer rule refined; standalone SVG, PDF, PNG and workbench updated.');

import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/omen/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/_entry.js');
const {chromium}=require('playwright');
const dir='D:/vldb2027/output/algorithm_figures_redesign/revision_v3';
let svg=fs.readFileSync(dir+'/intro_execution.svg','utf8');
for(const [from,to] of [
 ['(a) k = 2, h = 1','(a) fan-in k = 2, head h = 1'],
 ['(b) SD · k = 4, h = 2','(b) Sliding Window · fan-in k = 4, head h = 2'],
 ['(c) LT · k = 8, h = 2','(c) Loser Tree · fan-in k = 8, head h = 2']
])svg=svg.replace(from,to);
fs.writeFileSync(dir+'/intro_execution.svg',svg);
let html=fs.readFileSync(dir+'/index.html','utf8');
let count=0;
html=html.replace(/<section><h2>Intro · Pairwise → Listwise<\/h2>[\s\S]*?<\/section>/,section=>{count++;return section.replace(/<figure>[\s\S]*?<\/figure>/,`<figure>${svg}</figure>`);});
if(count!==1)throw Error('Intro section not found');
fs.writeFileSync(dir+'/index.html',html);
const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
try{
 const page=await browser.newPage({viewport:{width:1660,height:880},deviceScaleFactor:2});
 await page.setContent(`<style>body{margin:0}svg{display:block}</style>${svg}`);
 const labels=await page.locator('text').evaluateAll(items=>items.filter(e=>/^\([abc]\)/.test(e.textContent)).map(e=>{const b=e.getBBox();return {text:e.textContent,x:b.x,right:b.x+b.width};}));
 if(labels.length!==3||labels[0].x<0||labels[0].right>398||labels.slice(1).some(l=>l.x<424||l.right>1660))throw Error('Intro caption overflow '+JSON.stringify(labels));
 await page.screenshot({path:dir+'/intro_execution.png'});
 const ht=178*880/1660;
 await page.setContent(`<style>@page{size:178mm ${ht}mm;margin:0}body{margin:0}svg{width:178mm;height:${ht}mm;display:block}</style>${svg}`);
 await page.pdf({path:dir+'/intro_execution.pdf',preferCSSPageSize:true,printBackground:true});
 console.log('Intro labels updated and checked within panel bounds.');
}finally{await browser.close();}

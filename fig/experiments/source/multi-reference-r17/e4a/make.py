from pathlib import Path
import re, subprocess, xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[5]
out=root/'fig/experiments/figures/e4a-r17'
out.mkdir(exist_ok=True,parents=True)
src=root/'fig/e4a-bold/6x10/full-sw.svg'
g=ET.parse(src).getroot().find('{*}g')
colors={}
for e in g.findall('{*}rect'):
 if e.get('width')=='9.46' and e.get('fill','').startswith('#'):
  x,y=float(e.get('x')),float(e.get('y'))
  r=int(y>72); c=int(x>=115)
  k=round((x-(116 if c else 13))/9.8)
  h=round((y-(82.95 if r else 19.65))/7.4)
  assert 0<=h<6 and 0<=k<10 and (r,c,k,h) not in colors
  colors[r,c,k,h]=e.get('fill')
assert len(colors)==166, len(colors)
ink='#26343D'
pat='<pattern id="invalid" width="3.2" height="3.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3.2" height="3.2" fill="#EFF1F3"/><path d="M0 0v3.2" stroke="#929EA8" stroke-width=".62"/></pattern>'
stops=''.join(f'<stop offset="{i/6}" stop-color="{c}"/>' for i,c in enumerate(['#8F302B','#D5785F','#F2C4AA','#F7F7F4','#ACC7DD','#557EB5','#233C73']))
def write(name,w,h,els):
 s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}"><defs>{pat}<linearGradient id="scale" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient></defs><g font-family="Liberation Serif,serif" fill="{ink}">'+''.join(els)+'</g></svg>'
 p=out/(name+'.svg');p.write_text(s)
 subprocess.run(['inkscape',str(p),'--export-filename='+str(p.with_suffix('.pdf'))],check=True)
def t(x,y,s,sz=7.0,anc='start',weight='normal',style='normal'):
 return f'<text x="{x}" y="{y}" font-size="{sz}" text-anchor="{anc}" font-weight="{weight}" font-style="{style}">{s}</text>'
def rect(x,y,w,h,f,s='none'):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{f}" stroke="{s}" stroke-width=".38"/>'
def line(x,y,x2,y2):
 return f'<path d="M{x} {y}L{x2} {y2}" stroke="#6D7B85" stroke-width=".44" fill="none"/>'
W0,W1,WK=111,98,31
for r in range(2):
 for c,fam in enumerate(['sw','lt']):
  x0=14 if c==0 else 1
  y0=1
  dx,dy=9.55,7.4
  es=[]
  if not c: es.append(t(1,y0+4.7,'h',7.,style='italic'))
  for h in range(6):
   if not c: es.append(t(11,y0+(h+.5)*dy+2.25,6-h,7.0,'end'))
   for k in range(10):
    es.append(rect(x0+dx*k+.12,y0+dy*h+.12,dx-.24,dy-.24,colors.get((r,c,k,h),'url(#invalid)')))
  bot=y0+6*dy
  es.append(rect(x0,y0,10*dx,6*dy,'none','#73808B'))
  if r:
   for k in range(10):
    x=x0+dx*(k+.5)
    es.extend([line(x,bot,x,bot+1.6),t(x,bot+8.0,k+2,7.0,'middle')])
   if not c: es.append(t(9,bot+8.0,'k',7.,style='italic',anc='end'))
  write(('limit' if r else 'full')+'-'+fam,W0 if c==0 else W1,55 if r else 47,es)
els=[t(15.5,8.0,'Savings',7.0,'middle','bold'),t(15.5,15.8,'(%)',6.6,'middle'),rect(2,22,7,78,'url(#scale)','#73808B')]
for y,v in [(22,'≥+30'),(41.5,'+15'),(61,'0'),(80.5,'−15'),(100,'≤−30')]:
 els.extend([line(9,y,11,y),t(12,y+2.2,v,6.75,weight='bold' if v=='0' else 'normal')])
els.extend([rect(2,109,7,7,'url(#invalid)','#73808B'),t(2,124,'Infeasible',6.8)])
write('key',WK,128,els)

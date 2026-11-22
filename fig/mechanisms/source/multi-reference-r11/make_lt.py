from pathlib import Path
from lxml import etree as E
import sys
src=Path(sys.argv[1]);dst=Path(sys.argv[2]); compact='--compact' in sys.argv
t=E.parse(str(src)); N='{http://www.w3.org/2000/svg}'
def fix(e,**kw):
 for k,v in kw.items():e.set(k.replace('_','-'),str(v))
def ad(p,tag,content=None,**kw):
 e=E.SubElement(p,N+tag)
 fix(e,**kw)
 e.text=content
 return e
ink='#28343C'; warm='#965A08'; ash='#4F5E63'
def tx(p,x,y,text,size=5.5,color=ink,bold=False):
 kw=dict(x=x,y=y,font_size=size,fill=color,text_anchor='middle')
 if bold:kw['font_weight']='bold'
 return ad(p,'text',text,**kw)
def line(p,x,y,x2,y2,color=ash,w=.55):
 return ad(p,'path', d=f'M {x} {y} L {x2} {y2}', fill='none',stroke=color,stroke_width=w)
def arrow(p,x,y,x2,y2,color=ash):
 line(p,x,y,x2,y2,color)
 if x==x2:s=f'M{x-1.10} {y2+1.6} L{x} {y2} L{x+1.10} {y2+1.6}' if y2<y else f'M{x-1.1} {y2-1.6} L{x} {y2} L{x+1.1} {y2-1.6}'
 else:s=f'M{x2-2} {y2-1.2} L{x2} {y2} L{x2-2} {y2+1.2}'
 ad(p,'path',d=s,fill='none',stroke=color,stroke_width='.6',stroke_linecap='round')
p=t.getroot().find(N+'g'); L=p.find(N+'g[@id="read-path"]'); R=p.find(N+'g[@id="after"]'); legend=p.find(N+'g[@id="legend"]')
for e in list(p):
 if e not in [L,R,legend]:p.remove(e)
L.find(N+'text').text='(a) Find the refresh path'
R.find(N+'text').text='(b) Replay the path'
legend.findall(N+'text')[-1].text='Follow pointer'
for node in L.findall(N+'circle'):
 if float(node.get('cy')) in {33,46.9} and node.get('stroke')=='#AC6D0B':
  node.set('stroke',ink)
for gg in [L,R]:
 for e in gg.findall(N+'text'):
  if e.text in {'8','9'} and e.get('fill')=='#8C989E':e.set('fill','#606E74')
# Keep the legend at the exact trim-safe position.
g=ad(p,'g',id='one-listwise-call')
ad(g,'rect',x=100.0,y=19.8,width=40.25,height=25.6,rx=1.35,fill='white',stroke='#B57F36',stroke_width='.63')
tx(g,120.1233,15.8,'Rank once',6.85,ink,True)
tx(g,120.1233,27.1,'Stored on path',5.55,ash)
tx(g,120.1233,33.8,'[3, 4]  +  [5, 7]',5.8,ink)
tx(g,120.1233,41.5,'New R₂  [6, 14]',5.8,warm,True)
# A local solid rectangular enclosure visually matches Fig3's one-call grammar.
arrow(g,120.1233,46.4,120.1233,50.7)
tx(g,120.1233,57.0,'3 ≺ 4 ≺ 5 ≺ 6 ≺ 7 ≺ 14',5.55,ink)
tone='#425E4D'
h=ad(p,'g',id='bottom-up-order')
arrow(h,98.7,69.0,98.7,63.7,tone)
tx(h,122.1,68.9,'Replay bottom-up',5.5,tone,True)
# The numbers label actual updated matches, bottom node first, root second.
tx(R,149.8,48.85,'(1)',5.5,tone,True)
tx(R,171.7,34.85,'(2)',5.5,tone,True)
# Before and after snapshots still retain all run positions and filled outputs.
E.indent(t,space='  ');t.write(dst,encoding='UTF-8',xml_declaration=True)

#!/usr/bin/env python3
from pathlib import Path
from lxml import etree as E
import json,os,subprocess
S=Path(__file__).resolve().parent
D=S.parent
P=D/'patch/fig/mechanisms'
N="http://www.w3.org/2000/svg"
def tag(s): return f'{{{N}}}{s}'
def el(p,s,**a): return E.SubElement(p,tag(s),{k.replace('_','-'):str(v) for k,v in a.items() if v is not None})
def tx(p,x,y,msg,size=5.7,fill='#252B2E',anchor='middle',weight=None,italic=False):
 e=el(p,'text',x=x,y=y,font_size=size,fill=fill,text_anchor=anchor,font_weight=weight,font_style='italic' if italic else None);e.text=msg;return e
def line(p,x,y,xx,yy,col='#69757C',sw=.55):return el(p,'path',d=f'M{x} {y} L{xx} {yy}',stroke=col,stroke_width=sw,fill='none')
def rect(p,x,y,w,h,rx,fill,stroke,sw,da=None):return el(p,'rect',x=x,y=y,width=w,height=h,rx=rx,fill=fill,stroke=stroke,stroke_width=sw,stroke_dasharray=da)
def arrow(p,x,y,yy):
 line(p,x,y,x,yy-1.1);el(p,'path',d=f'M{x-1.05} {yy-1.9}L{x} {yy}L{x+1.05} {yy-1.9}Z',fill='#69757C')
def branch(p,x1,x2,y,yy,dest):
 # Open fan-in, not a compartment.
 el(p,'path',d=f'M{x1} {y}V{yy}H{x2}V{y}',stroke='#9CA6AB',stroke_width='.48',fill='none')
 arrow(p,(x1+x2)/2,yy,dest)
def circle(p,x,y,num,final):
 e=el(p,'g',data_value=num);el(e,'circle',cx=x,cy=y,r=4.46,fill='#DDEBDD' if final else '#fff',stroke='#4F6B56' if final else '#485157',stroke_width=.5)
 tx(e,x,y+1.97,str(num),5.7)
def coins(p,x,y,rows,final=False,pitch=12):
 for i,n in enumerate(rows):circle(p,x+pitch*(i-(len(rows)-1)/2),y,n,final)
def call(p,x,y,name,merger=False):
 w=48.5 if merger else 44.4
 rect(p,x-w/2,y-5.25,w,10.5,1.25,'#fff' if merger else '#FFE3AE','#AC6D0B',.56,'1.8 1.2' if merger else None);tx(p,x,y+2,name,5.8)
def sym(p,x,y,letter,n):
 e=tx(p,x,y,letter,6.0,italic=True)
 sub=el(e,'tspan',dy=1.2,font_size=4.8,font_style='normal');sub.text=str(n)
def out(tree,dst):E.indent(tree,space="  ");tree.write(str(dst),xml_declaration=True,encoding="utf-8")
def pdf(svg,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 env={**os.environ,'XDG_CONFIG_HOME':str(D/'.build/config'),'XDG_CACHE_HOME':str(D/'.build/cache'),'SOURCE_DATE_EPOCH':'0'}
 subprocess.run(['inkscape',str(svg),'--export-type=pdf',f'--export-filename={dst}'],env=env,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def fig2():
 a=json.loads((S/'fig2/states.json').read_text())
 assert a['R']==[sorted(c) for c in a['C']] and a['Q']==[sorted(a['R'][0]+a['R'][1]),sorted(a['R'][2]+a['R'][3])] and a['Pi']==list(range(1,17))
 w,h=240.24655,135.723
 r=E.Element(tag('svg'),nsmap={None:N},width=f'{w}pt',height=f'{h}pt',viewBox=f'0 0 {w} {h}')
 el(r,'title').text='Four chunks, four initial runs, and two merge passes'
 el(r,'desc').text='ListwiseRank processes each input chunk in one call. Open fan-in lines pair the runs for each merge. The final output is the green sequence at the bottom.'
 g=el(r,'g',font_family='Nimbus Roman, Liberation Serif, serif')
 cs=[31.5,90.5,149.5,208.5];qs=[61,179]
 for i,x in enumerate(cs):
  cols=el(g,'g',id=f'chunk-{i+1}')
  sym(cols,x,5.9,'C',i+1);coins(cols,x,13.5,a['C'][i]);arrow(cols,x,18.45,22.8);call(cols,x,28.1,'ListwiseRank');arrow(cols,x,33.5,37.2)
  sym(cols,x,42.6,'R',i+1);coins(cols,x,49.4,a['R'][i])
 for i,x in enumerate(qs):
  branch(g,cs[2*i],cs[2*i+1],54.5,56.8,59.3)
  call(g,x,64.7,'MergeGroup',True);arrow(g,x,70,73.4);sym(g,x,78.95,'Q',i+1);coins(g,x,85.7,a['Q'][i],pitch=12)
 branch(g,*qs,90.8,93.1,96.1);call(g,120,101.5,'MergeGroup',True)
 for y,n,nn in [(64.8,1,'4 → 2 runs'),(101.6,2,'2 → 1 run')]:
  tx(g,1.4,y-.75,'Pass '+str(n),6.45,anchor='start',weight='bold');tx(g,1.4,y+6.15,nn,5.6,fill='#596168',anchor='start')
 arrow(g,120,106.8,110.75)
 # A single overbar connects the last merger to a whole sequence, not one item.
 el(g,'path',d='M29.2 112.65V110.85H232.7V112.65',stroke='#809086',stroke_width='.48',fill='none')
 tx(g,13.3,119.6,'Π =',6.55);coins(g,131,117.6,a['Pi'],True,pitch=12.95)
 for x,name,merger in [(50,'one LLM call',False),(129,'group merger',True)]:
  rect(g,x,128.1,10.8,5.9,1.05,'#fff' if merger else '#FFE3AE','#AC6D0B',.54,'1.6 1' if merger else None);tx(g,x+14,132.95,name,5.75,anchor='start')
 svg=S/'fig2/alg1-trace.svg';out(E.ElementTree(r),svg);pdf(svg,P/'alg1-trace/alg1-trace.pdf')
def fig4():
 f=S/'fig4';r=E.parse(str(f/'lt-path.svg')); t=r.xpath('//*[local-name()="text" and text()="Rank once"]')[0];t.set('y','29.8')
 arr=json.loads((f/'states.json').read_text())['refresh']['rank_map_order']
 note=tx(t.getparent(),120.1233,37.15,'['+', '.join(map(str,arr))+']',5.55,fill='#50595E')
 # Keep the new sequence secondary to the gold route, without a frame or new tokens.
 t.addnext(note)
 # Shift just the central arrow and existing replay caption; node coordinates are fixed.
 for e in note.getparent():
  if e.tag==tag('line') and e.get('y1')=='39.7': e.set('transform','translate(0 3)')
  if e.tag==tag('polygon') and e.get('points','').startswith('134.8233,39.7000'): e.set('transform','translate(0 3)')
  if e.tag==tag('text') and e.text=='Replay bottom-up':e.set('y','50.6')
 r.xpath('//*[@id="legend"]')[0].set('transform','translate(0 -1.15)') # retain descenders inside the fixed page
 svg=f/'lt.svg';out(r,svg);pdf(svg,P/'lt.pdf')
def fig5():
 f=S/'fig5';r=E.parse(str(f/'r4.svg'));L=r.xpath('//*[@id="legend-physical-bp"]')[0]
 for e in r.xpath('//*[contains(@id,"ranked-excerpt")]'):e.getparent().remove(e)
 for e in r.xpath('//*[local-name()="text" and text()="Ranked slots"]'):
  e.text='Replay order';e.set('font-style','normal');e.set('fill','#373F43');e.set('font-weight','bold');e.set('font-size','6.92')
 L.remove(L[-1])
 for e,x in zip(L,[15.0,67.4,118.2,192.3]):e.set('transform',f'translate({x} 0) scale(0.84)')
 svg=f/'pointer.svg';out(r,svg);pdf(svg,P/'pointer.pdf')
if __name__=='__main__':fig2();fig4();fig5()

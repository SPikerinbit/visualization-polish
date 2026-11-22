from lxml import etree as E
from pathlib import Path
import re
o=Path(__file__).resolve().parent
src=o.parents[1]/'multi-reference-r10/sw.svg'
tr=E.parse(src)
root=tr.getroot()
ns={'s':root.nsmap[None]}
def find(q):return root.xpath(q,namespaces=ns)
g=find('s:g')[0]
def add(tag, **attrs):return E.SubElement(g,'{'+ns['s']+'}'+tag,**{k.replace('_','-'):str(v) for k,v in attrs.items()})
def tx(x,y,s,anchor='start',size=5.8,col='#4D565B'):
 a=add('text',x=x,y=y,text_anchor=anchor,font_size=size,fill=col)
 a.text=s
def path(d,**kw):return add('path',d=d,**kw)
ink='#313C43'
for c in find('s:g/s:circle'):
 v=c.getnext()
 if v is not None and (c.get('cx'),c.get('cy')) in [('34.5750','40.0000'),('41.9500','59.0000'),('151.5750','40.0000'),('122.0500','59.0000')]:
  c.set('stroke',ink);c.set('stroke-width','.85');v.set('font-weight','bold')
for node in list(g):
 if node.tag.endswith('path'):
  d=node.get('d','')
  if any(d.startswith(pr) for pr in ['M39.200 45.1','M119.300 45.1','M104.150 45.8','M221.150 45.8','M44.5250 53','M124.6250 53','M46.2750 63','M126.3750 63']):
   g.remove(node)
 if node.tag.endswith('text'):
  if node.get('x') in ['110.3500','227.3500'] and node.get('y')=='17.7500':
   node.set('font-weight','normal');node.set('fill','#626A70')
  if node.text in ['Refill R2','Refill R4']:
   node.text={'Refill R2':'R2 next: 6','Refill R4':'R4 next: 13'}[node.text];node.set('fill',ink)
  elif node.text=='Emit all six':
   node.text='Emit 11–16'
defs=find('s:defs')[0]
mk=E.SubElement(defs,'{'+ns['s']+'}marker',id='tail',viewBox='0 0 5 5',refX='4.8',refY='2.5',markerWidth='3.3',markerHeight='3.3',orient='auto')
E.SubElement(mk,'{'+ns['s']+'}path',d='M0 .2L5 2.5L0 4.8Z',fill=ink)
for x,xt in [(34.575,41.95),(151.575,122.05)]:
 path(f'M{x} 44.25 L{x} 46.7 L{xt} 51.7 L{xt} 54.42',fill='none',stroke=ink,stroke_width='.69',stroke_linejoin='round',marker_end='url(#tail)')
tx(34.3,51.6,'R2 buffer tail','end',5.65,ink)
tx(120.5,51.6,'R4 buffer tail','end',5.65,ink)
# Third round has no causal cutoff; leave the regular all-window arrow alone.
tx(235,71.55,'No unread rows','end',5.65,ink)
# Break marks border the two groups, without falsely pointing at the first retained row.
for x in [46.275,126.375]:
 for y in [53.35,63.1]:
  path(f'M{x} {y} v1.8',fill='none',stroke='#748077',stroke_width='.55')
find('s:desc')[0].text='Rounds 1 and 2 trace the last buffered row (5 in R2; 10 in R4) from its run through the ranked call output. The next unread rows in those runs are 6 and 13. In round 3 no run has unread input; all six buffered rows are emitted.'
tr.write(str(o/'sw.svg'),encoding='UTF-8',xml_declaration=True)

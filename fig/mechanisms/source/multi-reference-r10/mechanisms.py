"""A shared semantic grammar: solid call boundary, dashed composite/unread,
short unboxed action labels, and the stronger accent only where state changes."""
from pathlib import Path
from lxml import etree as E
import sys
root=Path(sys.argv[1]);out=Path(sys.argv[2])
out.mkdir(parents=True,exist_ok=True)
base=root/'fig/mechanisms/source'
ns='http://www.w3.org/2000/svg'
def svg(path):return E.parse(str(base/path))
def save(tree,name):tree.write(str(out/name),encoding='UTF-8',xml_declaration=True)
def remake(e,**a):
 for k,v in a.items():e.set(k.replace('_','-'),str(v))
sw=svg('multi-reference-r8/sw.svg')
boxes=sw.xpath('//*[local-name()="rect" and @stroke-dasharray="1.6 1.15"]')
assert len(boxes)==4
for e in boxes:
 del e.attrib['stroke-dasharray']
 remake(e,stroke='#B57F36',stroke_width='.58',rx='.85')
 # Keep the windows unfilled in this view: some row chips are drawn first.
for r, e in enumerate(boxes[:3]):
 for x in [21.025,39.475,57.925]:
  x=x+80.10*r
  e.addnext(E.Element(f'{{{ns}}}path',d=f'M{x:.3f} 36.65v6.7',stroke='#9C8B71',**{'stroke-width':'.37'}))
# Empty run outlines and next-refill pills now become the typographic marker,
# while the separate amber refill ticks on the specific window remain.
for e in sw.xpath('//*[local-name()="rect" and @y="11.7000"]'):
 e.getparent().remove(e)
for e in sw.xpath('//*[local-name()="path" and contains(@d,"l1.75 1.35")]'):
 remake(e,stroke_width='.84')
save(sw,'sw.svg')

alg=svg('multi-reference-r6/fig2/alg1-trace.svg')
for e in alg.xpath('//*[local-name()="rect" and @fill="#FFE3AE"]'):
 remake(e,fill='#FFF0D1')
for e in alg.xpath('//*[local-name()="path" and @stroke="#9CA6AB"]'):
 remake(e,stroke='#879298',stroke_width='.59')
for t in alg.xpath('//*[local-name()="text" and text()="MergeGroup"]'):
 remake(t,fill='#2E383D',font_weight='bold')
save(alg,'alg1-trace.svg')

lt=svg('multi-reference-r8/lt.svg')
for e in lt.xpath('//*[local-name()="line" and @stroke="#AC6D0B" and @stroke-width="1.2"]'):
 remake(e,stroke_width='1.32')
q=lt.xpath('//*[local-name()="text" and text()="Rank once"]')[0]
remake(q,fill='#3B3022')
q.addprevious(E.Element(f'{{{ns}}}path',d='M112 21.7h16.25',stroke='#C18A31',**{'stroke-width':'.67'}))
save(lt,'lt.svg')

pt=svg('multi-reference-r8/pointer.svg')
for t in pt.xpath('//*[local-name()="text" and contains(text(),"2/2")]'):
 remake(t,fill='#915807')
save(pt,'pointer.svg')

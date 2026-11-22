from lxml import etree as E
from pathlib import Path
p=Path(__file__).resolve().parent
doc=E.parse(str(p.parents[1]/'multi-reference-r12/pointer.svg'));ns={'s':'http://www.w3.org/2000/svg'}; H='{'+ns['s']+'}'
def get(el,q):return el.xpath(q,namespaces=ns)
def add(parent,tag,attrs):return E.SubElement(parent,H+tag,{k:str(v) for k,v in attrs.items()})
for side in ['build','refresh']:
 g=get(doc,f'//s:g[@id="{side}"]')[0]
 lab=get(g,'./s:text[contains(text(), "Slot L")]')[0]
 lab.text= ('Left child → L   ·   Right child → R' if side=='build' else 'Retained P → L   ·   Refill from R → R')
 if side=='refresh':
  lab.set('font-weight','bold');lab.set('fill','#284C60')
 for row4 in get(g,'./*[@transform="translate(17.8 6.02900) scale(0.84)"]'):
  row4.set('transform','translate(17.8 4.62900) scale(0.84)')
 for t in get(g,'./s:text[@x="94"]')[:2]:
  t.text=t.text+': 1/2'
# Preserve saturation coding on rows themselves; identify the stored pair by a common outline.
for id in ['build-after','refresh-before']:
 g=get(doc,'//s:g[@id="'+id+'"]')[0]
 re=get(g,'./s:rect[@x="25.8"]')[0]
 re.set('stroke','#4C7081');re.set('stroke-width','.82');re.set('fill','#ECF3F5')
# A source connector rooted in P joins precisely the two L entries. Orthogonal, no arrowheads; gold arrows remain exclusively tree pointers.
g=get(doc,'//s:g[@id="refresh"]')[0]
lead=add(g,'g',{'fill':'none','stroke':'#4C7081','stroke-width':'.60','stroke-linejoin':'round'})
add(lead,'path',{'d':'M51.0 32.1 H70.1 V65.0 M70.1 33.18 H84.4 M70.1 65.0 H83.4'})

doc.write(str(p/'pointer.svg'),encoding='utf-8',xml_declaration=True,pretty_print=True)

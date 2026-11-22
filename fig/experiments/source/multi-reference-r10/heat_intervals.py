"""Render disconnected invalid regions as single continuous hatched masks."""
import sys
from pathlib import Path
from lxml import etree as E
ns='http://www.w3.org/2000/svg'
root=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
for p in sorted(root.glob('*.svg')):
 if p.name=='key.svg': continue
 doc=E.parse(str(p))
 elems=doc.xpath('//*[local-name()="rect" and @fill="url(#invalid)" and not(@y="113")]')
 # Every crop retains the full backing SVG. The union uses exactly the same
 # invalid grid slots on every crop; changing the crop alters no alignment.
 assert len(elems)==74
 parts=[]
 for e in elems:
  x=float(e.get('x'))-.17; y=float(e.get('y'))-.17
  w=9.8; h=7.4
  assert (x+.17>=13 and y+.17>=19)
  parts.append(f'M{x:.4f} {y:.4f}h{w}v{h}h-{w}Z')
 elems[0].addprevious(E.Element(f'{{{ns}}}path',d=' '.join(parts),fill='url(#invalid)'))
 for e in elems:e.getparent().remove(e)
 doc.write(str(out/p.name),encoding='UTF-8')

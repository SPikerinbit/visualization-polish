"""Improve the shared texture key; all 240 cells and placements are kept."""
from pathlib import Path
import sys
from lxml import etree as E
src=Path(sys.argv[1])
dst=Path(sys.argv[2])
dst.mkdir(parents=True,exist_ok=True)
for p in sorted(src.glob('*.svg')):
    tree=E.parse(str(p))
    hatch=tree.xpath('//*[@id="invalid"]/*[@stroke="#C7CED6"]')
    assert len(hatch)==1
    hatch[0].set('stroke','#AAB3BD')
    if p.name=='key.svg':
        swatch=tree.xpath('//*[@x="218.3" and @y="113"]')
        assert len(swatch)==1
        swatch[0].set('width','9.46')
        swatch[0].set('height','7.06')
        for t in tree.xpath('//*[@x="224.65" and @font-size="5.35"]'):
            t.set('font-size','6.05')
        note=tree.xpath('//*[text()="Infeasible"]')[0]
        note.set('y','128.0')
    tree.write(str(dst/p.name),encoding='UTF-8')

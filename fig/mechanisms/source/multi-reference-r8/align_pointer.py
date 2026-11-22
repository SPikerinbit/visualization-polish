"""Align the two replay orders while keeping all nodes and replay states fixed."""
from pathlib import Path
import sys
from lxml import etree as ET
src = Path(__file__).resolve().parents[1]/'multi-reference-r6/fig5/pointer.svg'
tree = ET.parse(str(src))
for panel in ['build','refresh']:
    group = tree.xpath(f'//*[@id="{panel}"]')[0]
    replay = group.xpath('./*[@data-role and @transform] | ./*[contains(@transform,"17.800") and local-name()="text"]')
    assert len(replay) == 9
    for e in replay[1:]:
        e.set('transform','translate(17.8 0) scale(0.84)')
        if e.tag.endswith('}g'):
            row = (float(e[0].get('cy'))-39.5)/16.5
        else:
            row = (float(e.get('y'))-41.65)/16.5
        # In the left tree, the lower leaf container ends at 100.85.
        # Bottom replay ring (including stroke) ends at 96.17738+4.67262.
        new_y = 39.5 + (96.17738-39.5)*row/3
        e.set('transform',f'translate(17.8 {(new_y-(39.5+16.5*row))*.84:.5f}) scale(0.84)')
    # Labels are annotations; the ordered numeric spine anchors the title.
    replay[0].set('x', '84.4' if '--spine' in sys.argv else '95.5')
    divider = ET.Element('{http://www.w3.org/2000/svg}line', {
        'x1':'84.8', 'x2':'111.8', 'y1':'55.05', 'y2':'55.05',
        'stroke':'#AEB6BC', 'stroke-width':'0.45',
    })
    replay[0].addnext(divider)
tree.write(sys.argv[1],xml_declaration=True,encoding='UTF-8')

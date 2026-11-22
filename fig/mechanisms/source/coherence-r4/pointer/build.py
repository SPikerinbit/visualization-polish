#!/usr/bin/env python3
"""Polish canonical Fig. 5 without changing its two tree/strip panels."""
from pathlib import Path
import argparse, os, subprocess, xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
import fitz

HERE=Path(__file__).resolve().parent
W,H=240.24655,94.164
S=.84
N='http://www.w3.org/2000/svg'
ET.register_namespace('',N)
def q(s):return '{'+N+'}'+s
INK='#252B2E'
DARK='#4D4D4D'
UNREAD='#6C6C6C'
SOFT='#BEBEBE'
BRANCH='#969696'
GOLD='#AC6D0B'
GOLD_FILL='#FFE3AE'
GOLD_FRAME='#C5A36F'
WINNER='#4F6B56'
WINNER_FILL='#DDEBDD'
def export(svg,pdf,fontdir):
    fontconf=HERE/'fonts.conf'
    fontconf.write_text(f'''<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
 <include>/etc/fonts/fonts.conf</include>
 <dir>{escape(str(fontdir))}</dir>
 <cachedir>{escape(str(HERE/'fontcache'))}</cachedir>
</fontconfig>
''')
    env={**os.environ,'FONTCONFIG_FILE':str(fontconf),'XDG_CONFIG_HOME':str(HERE/'config'),'XDG_CACHE_HOME':str(HERE/'cache'),'SOURCE_DATE_EPOCH':'0'}
    subprocess.run(['inkscape',str(svg),'--export-type=pdf',f'--export-filename={pdf}'],env=env,check=True)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--font-dir',type=Path,default=HERE.parent/'pvldb2027/tl26/fonts/opentype/public/tex-gyre')
    arg=ap.parse_args()
    font_dir=arg.font_dir.resolve()
    if not (font_dir/'texgyretermes-regular.otf').is_file():raise SystemExit("Supply --font-dir with TeX Gyre Termes OTF files")
    tree=ET.parse(HERE/'canonical.svg')
    root=tree.getroot()
    all_elements={el.get('id'):el for el in root.iter() if 'id' in el.attrib}
    root.find(q('desc')).text=('Construction and refresh at the same local replay node, before and after. '
         'Each ordered strip is read top to bottom. Green marks the two local winners. '
         'The gold double ring and 2/2 identify the first exhausted slot and determine the new gold pointer. '
         'White dashed rings are unread rows. Before refresh the old pointer is R; the new pointer is L.')
    base=root.find(q('g'))
    base.set('fill',INK)
    base.set('font-family','Nimbus Roman, Liberation Serif, serif')
    divider=base.find(q('path'))
    divider.set('stroke','#DADADA')
    legend=all_elements['legend-physical-bp']
    for panel_id in ('build','refresh'):
        p=all_elements[panel_id]
        first=p.find(q('text'))
        first.set('font-size',f'{7.05/S:.8f}')
        first.set('y','9.35')
        redundant=[el for el in p.findall(q('path')) if el.get('d','').startswith('M4 23.4')]
        assert len(redundant)==1
        p.remove(redundant[0])
        fr=all_elements[panel_id+'-ranked-excerpt']
        fr.set('stroke',GOLD_FRAME);fr.set('stroke-width',f'{.40/S:.8f}');fr.set('stroke-dasharray','1.65 1.35')
        for el in p.findall(q('text')):
            if el.text.startswith('Slot L:'):
                el.set('fill',DARK)
            if el.text in ('Before','After','Ranked slots'):
                el.set('fill',DARK);el.set('font-size',f'{5.75/S:.8f}')
            if ': 2/2' in el.text:
                el.set('fill',GOLD);el.set('font-size',f'{5.9/S:.8f}')
        for state in ('before','after'):
            node=all_elements[f'{panel_id}-{state}']
            for r in node.findall(q('rect')):
                r.set('stroke',SOFT);r.set('stroke-width',f'{.34/S:.8f}')
            for e in node.findall(q('path')):
                e.set('stroke',BRANCH);e.set('stroke-width',f'{.43/S:.8f}')
            for g in node.findall(q('g')):
                if 'data-pointer' in g.attrib:
                    for e in g.findall(q('path')):
                        if e.get('fill')=='none':
                            e.set('stroke',GOLD);e.set('stroke-width',f'{.66/S:.8f}')
                        else: e.set('fill',GOLD)
        for g in p.iter(q('g')):
            if 'data-value' not in g.attrib: continue
            rr=g.findall(q('circle'))
            circ=rr[-1]
            circ.set('r',f'{3.70/S:.8f}');circ.set('stroke-width',f'{.45/S:.8f}')
            # Activity before replay and trigger rows receive gold. The trailing
            # non-trigger loser is charcoal, not highlighted as an action.
            role=g.get('data-role')
            rank_group=g in p.findall(q('g'))
            if role=='winner': fill,stroke=WINNER_FILL,WINNER
            elif len(rr)>1 or (role=='active' and not rank_group): fill,stroke=GOLD_FILL,GOLD
            elif role=='unread':fill,stroke='white',UNREAD
            else:fill,stroke='white',DARK
            circ.set('fill',fill);circ.set('stroke',stroke)
            if role=='unread':circ.set('stroke-dasharray',f'{1.15/S:.8f} {.75/S:.8f}')
            if len(rr)>1:
                rr[0].set('r',f'{4.75/S:.8f}')
                rr[0].set('stroke',GOLD);rr[0].set('stroke-width',f'{.48/S:.8f}')
    entries=legend.findall(q('g'))
    entries[0].find(q('circle')).attrib.update(fill=WINNER_FILL,stroke=WINNER)
    entries[1].find(q('circle')).attrib.update(stroke=UNREAD)
    for e in entries[2].findall(q('circle')):e.set('stroke',GOLD)
    for e in entries[3].findall(q('path')):
        for att in ('fill','stroke'):
            if e.get(att)=='#E07B00':e.set(att,GOLD)
    entries[4].find(q('rect')).attrib.update(stroke=GOLD_FRAME,**{'stroke-width':f'{.4/S:.8f}','stroke-dasharray':'1.65 1.35'})
    out=HERE/'pointer.svg'
    ET.indent(tree,space='  ')
    tree.write(out,encoding='UTF-8',xml_declaration=True)
    export(out,HERE/'pointer.pdf',font_dir)
    with fitz.open(HERE/'canonical.pdf') as a, fitz.open(HERE/'pointer.pdf') as b:
        d=fitz.open()
        for file,label in [(a,'Original c4e1049'),(b,'Pointer refinement')]:
            pg=d.new_page(width=W+14,height=H+19)
            pg.insert_text((7,8),label,fontsize=6,fontname='tiro')
            pg.show_pdf_page(fitz.Rect(7,13,7+file[0].rect.width,13+file[0].rect.height),file,0)
        d.save(HERE/'native-compare.pdf',garbage=4,deflate=True)
        for n,pg in [('canonical',a[0]),('pointer',b[0])]:
            pg.get_pixmap(matrix=fitz.Matrix(3,3),alpha=False).save(HERE/(n+'.png'))
        b[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False,colorspace=fitz.csGRAY).save(HERE/'pointer-gray-108dpi.png')
if __name__=='__main__':main()

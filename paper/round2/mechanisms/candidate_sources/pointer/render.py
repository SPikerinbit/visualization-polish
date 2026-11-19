#!/usr/bin/env python3
"""Generate the active single-column Pointer figure. Physical units: PDF big points.

From any cwd: python3 <this-file>. Requires Inkscape, PyMuPDF and Poppler pdftoppm.
Numbers are taken from the verified local replay plus the shared LT run data.
Only diagram arrows are pointers; gray tapered-free paths are structural edges.
"""
from pathlib import Path
import json, os, subprocess, xml.etree.ElementTree as ET
from math import hypot
import fitz
HERE=Path(__file__).resolve().parent
MECH=HERE.parent.parent
DATA=json.loads((HERE/'verified-trace.json').read_text())
RUN=json.loads((HERE.parent/'lt/source-data.json').read_text())['runs'][:2]
W,H=240.24655,112.1
HALF=W/2
R=4.05
F=6.8
ORANGE='#E07B00'; WARM='#FDE7CE'; GRAY='#D6D6D6'
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
def el(p,tag,**a):
    return ET.SubElement(p,'{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
def txt(p,x,y,s,size=7,**a):
    e=el(p,'text',x=x,y=y,font_size=size,text_anchor=a.pop('anchor','middle'),**a);e.text=str(s);return e
def circ(p,x,y,r,fill,stroke,width=.45,**a):
    return el(p,'circle',cx=x,cy=y,r=r,fill=fill,stroke=stroke,stroke_width=width,**a)
def path(p,d,color,width,**a):
    return el(p,'path',d=d,fill='none',stroke=color,stroke_width=width,**a)
def group(p,**a): return el(p,'g',**a)
def element(p,x,y,v,style,ring=False):
    fill,stroke={'active':(WARM,ORANGE),'winner':(GRAY,'#888888'),'stored':('white','#555555'),'unread':('white','#666666')}[style]
    g=group(p,data_value=v,data_role=style)
    if ring: circ(g,x,y,R+1.45,'none',ORANGE,.65)
    circ(g,x,y,R,fill,stroke,**({'stroke_dasharray':'1.15 .75'} if style=='unread' else {}))
    # Two-digit labels retain one font height, tightening only the width to
    # keep diagonally extreme glyph ink clear of the 8.1 bp circle.
    a={'transform':f'translate({x} 0) scale(.86 1) translate({-x} 0)'} if len(str(v))==2 else {}
    txt(g,x,y+2.19,v,F,**a)
def cap(p,x,y,seq,style):
    w=22.4 if seq else 12.3
    el(p,'rect',x=x-w/2,y=y-5.75,width=w,height=11.5,rx=5.75,fill='white',stroke='#B5B5B5',stroke_width='.36')
    if not seq: txt(p,x,y+2.15,'∅',7,fill='#555555');return
    assert len(seq)==2
    for ofs,v in zip((-5.15,5.15),seq):element(p,x+ofs,y,v,style)
def branch(p,x1,y1,x2,y2,active):
    # Start at the parent bottom center. End 1.4 bp short of the child so its
    # capsule remains visible; all three true pointer assignments are gold.
    dx,dy=x2-x1,y2-y1; L=hypot(dx,dy); ux,uy=dx/L,dy/L
    if not active:
        path(p,f'M{x1} {y1} L{x2} {y2}','#A9A9A9',.52); return
    tx,ty=x2-1.4*ux,y2-1.4*uy; bx,by=tx-3.15*ux,ty-3.15*uy
    g=group(p,data_pointer='L' if x2<x1 else 'R')
    path(g,f'M{x1} {y1} L{bx+.4*ux} {by+.4*uy}',ORANGE,.83)
    el(g,'path',d=f'M{tx} {ty} L{bx-1.22*uy} {by+1.22*ux} L{bx+1.22*uy} {by-1.22*ux} Z',fill=ORANGE)
def tree(p,name,y,parent,children,styles,pointer):
    g=group(p,id=name); xp,xl,xr=37.0,18.9,55.1; yc=y+20.5
    for side,xc in [('L',xl),('R',xr)]:
        branch(g,xp,y+5.75,xc,yc-5.75,pointer==side)
    cap(g,xp,y,parent,'stored'); txt(g,xp+(8.6 if not parent else 13.7),y+2.2,'P',6.9,anchor='start')
    for side,x,seq,style in zip(('L','R'),(xl,xr),children,styles):
        cap(g,x,yc,seq,style)
        txt(g,x+(-7.8 if side=='L' else 7.8),yc-7.8,side,6.75,fill='#414141')
def validate():
    for d in DATA:
        L,Rr=d['L'],d['R']; ranks=d['z'];h=2
        assert sorted(v for v,_ in ranks)==sorted(L+Rr)
        counts={'L':0,'R':0}
        for i,(v,s) in enumerate(ranks):
            assert v in d[s];counts[s]+=1
            if counts[s]==h:break
        assert [v,s]==d['first_exhausted'] and i==d['index'] and s==d['pointer']
        assert d['winner']==[v for v,_ in ranks[:h]] and d['loser']==[v for v,_ in ranks[h:]]
    a,b=DATA
    assert [r[:2] for r in RUN]==[a['L'],a['R']] and a['pointer']=='R' and b['pointer']=='L'
    assert b['L']==a['loser'] and b['R']==RUN[1][2:4] and len(RUN[1])==4
def draw():
    validate()
    root=ET.Element('{'+NS+'}svg',width=f'{W}pt',height=f'{H}pt',viewBox=f'0 0 {W} {H}')
    el(root,'title').text='First-exhausted replay slot determines the child pointer'
    el(root,'desc').text=('Each panel shows the same node before and after replay, with the ranked slots read from top to bottom at right. '
       'Gray marks the two winners; a double ring marks the first exhausted slot. Construction assigns the right child. '
       'Refresh replays the stored parent as slot L and the incoming right child as slot R, then points left. Gray lines are tree edges. Each dashed orange frame encloses a ranked excerpt of the call output.')
    el(root,'rect',width=W,height=H,fill='white')
    body=group(root,font_family='Liberation Serif, Times New Roman, serif',fill='#222222')
    path(body,f'M{HALF} 3 V95.1','#D4D4D4',.41)
    for i,d in enumerate(DATA):
        b=bool(i); kind='refresh' if b else 'build';p=group(body,id=kind,transform=f'translate({HALF*i} 0)')
        txt(p,HALF/2,8.25,'(b) Path refresh' if b else '(a) Tree construction',8,font_weight='bold')
        txt(p,HALF/2,19.5,'Slot L: parent P · Slot R: child R' if b else 'Slot L: child L · Slot R: child R',7)
        # Break only the pale separator over the excerpt so that two borders
        # cannot coincide. The rounded outline includes its header and all four rows.
        path(p,'M4 23.4 H68.4','#DFDFDF',.37)
        # Align geometric ink edges, not path centers: capsule stroke is
        # .36 bp, versus .55 bp on the orange outline. Bottom ink y=101.03.
        tree_bottom=74.6+20.5+5.75+.36/2
        frame_height=tree_bottom-23.05-.55/2
        el(p,'rect',id=kind+'-ranked-excerpt',x=71.75,y=23.05,width=44.45,height=frame_height,rx=2.6,fill='none',
           stroke=ORANGE,stroke_width=.55,stroke_dasharray='1.5 1.15')
        txt(p,21.8,40.2,'Before',7,font_style='italic',anchor='end')
        txt(p,92.5,30.6,'Ranked slots',7,font_style='italic')
        if b:
            tree(p,kind+'-before',38.,DATA[0]['loser'],[RUN[0][2:],d['R']],['unread','active'],DATA[0]['pointer'])
            kids=[RUN[0][2:],[]]
        else:
            tree(p,kind+'-before',38.,[],[d['L'],d['R']],['active','active'],None)
            kids=[RUN[0][2:],RUN[1][2:]]
        txt(p,21.8,76.8,'After',7,font_style='italic',anchor='end')
        tree(p,kind+'-after',74.6,d['loser'],kids,['unread','unread'],d['pointer'])
        for j,(v,s) in enumerate(d['z']):
            y=39.5+j*16.5; isend=j==d['index']
            element(p,84.4,y,v,'winner' if j<2 else 'stored' if b and s=='L' else 'active',ring=isend)
            txt(p,94,y+2.15,s+(': 2/2' if isend else ''),6.95,anchor='start',fill='#925000' if isend else '#333333',**({'font_weight':'bold'} if isend else {}))
    # Five physical-width legend items. Advances below are Liberation Serif
    # 7 bp as embedded; Winner includes its Wi kerning. Equal inter-item gaps
    # are computed after each icon-plus-text group, not between group centers.
    specs=[('Winner',9.95,20.713),('Unread',9.95,20.601),('First exhausted',9.95,42.581),
           ('Pointer',13,20.223),('Call output (excerpt)',11.7,58.314)]
    widths=[a+b for _,a,b in specs]
    gap=(W-6.-sum(widths))/(len(specs)-1)
    assert gap>3
    leg=group(body,id='legend-physical-bp',transform=f'translate(0 {H-10})')
    x=3.
    for i,(t,start,_) in enumerate(specs):
        g=group(leg,transform=f'translate({x} 0)')
        if i<3:
            circ(g,3.475,5,3.25,[GRAY,'white','none'][i],['#888888','#666666',ORANGE][i],**({'stroke_dasharray':'1.15 .75'} if i==1 else {}))
            if i==2:circ(g,3.475,5,1.9,'none',ORANGE)
        elif i==3:
            path(g,'M0 5H7.2',ORANGE,.6);el(g,'path',d='M6.8 3.5L10 5L6.8 6.5Z',fill=ORANGE)
        else:
            el(g,'rect',x=.275,y=1.75,width=8.15,height=6.5,rx=1.4,fill='none',stroke=ORANGE,stroke_width=.55,stroke_dasharray='1.5 1.15')
        txt(g,start,7.3,t,anchor='start')
        x+=widths[i]+gap
    return root
if __name__=='__main__':
    out=MECH/'candidate_sources/pointer.svg'
    svg=draw();ET.indent(svg,space='  ');ET.ElementTree(svg).write(out,encoding='utf-8',xml_declaration=True)
    subprocess.run(['inkscape','--export-type=pdf','--export-filename='+str(MECH/'pointer.pdf'),str(out)],check=True,env={**os.environ,'SOURCE_DATE_EPOCH':'0'})
    # Cairo records wall-clock CreationDate even with SOURCE_DATE_EPOCH.
    # Strip only that metadata and suppress creation of a random document ID.
    pdf=MECH/'pointer.pdf'
    with fitz.open(pdf) as doc:
        info=int(doc.xref_get_key(-1,'Info')[1].split()[0])
        doc.xref_set_key(info,'CreationDate','null')
        stable=doc.tobytes(garbage=3,deflate=True,no_new_id=True)
    pdf.write_bytes(stable)
    subprocess.run(['pdftoppm','-png','-singlefile','-r','300',str(MECH/'pointer.pdf'),str(MECH/'pointer')],check=True)

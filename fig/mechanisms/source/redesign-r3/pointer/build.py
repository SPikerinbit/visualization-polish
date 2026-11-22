#!/usr/bin/env python3
"""Render two editable, text-preserving Fig. 5 contenders at 240.247 bp."""
from pathlib import Path
from html import escape
import json, subprocess
import fitz

ROOT=Path(__file__).resolve().parent
W=240.2465515
INK='#252421'; SUB='#625c54'; LINE='#c6bfb6'; METAL='#ece9e5'; WIN='#ded8d0'
ORANGE='#b3540b'; ORANGE_BG='#fff0dc'; DARK='#773701'
TRACE=[
  dict(title="(a) Tree construction", src={"L":("Left child",[3,7]),"R":("Right child",[1,5])},
       before_parent=[], old_pointer=None, before_unread={"L":[],"R":[]},
       order=[(1,"R"),(3,"L"),(5,"R"),(7,"L")], emit=[1,3], retain=[5,7],
       stop=(5,"R"), pointer="R", after_unread={"L":[12,16],"R":[6,14]}),
  dict(title="(b) Path refresh", src={"L":("Old parent",[5,7]),"R":("Right refill",[6,14])},
       before_parent=[5,7], old_pointer="R", before_unread={"L":[12,16],"R":[]},
       order=[(5,"L"),(6,"R"),(7,"L"),(14,"R")], emit=[5,6], retain=[7,14],
       stop=(7,"L"), pointer="L", after_unread={"L":[12,16],"R":[]}),
]
def check():
    for t in TRACE:
        assert sorted((v,s) for s,(_,xs) in t['src'].items() for v in xs)==sorted(t['order'])
        assert sorted(v for v,s in t['order'])==[v for v,s in t['order']]
        assert [v for v,s in t['order'][:2]]==t['emit']
        assert [v for v,s in t['order'][2:]]==t['retain']
        seen={"L":0,"R":0}
        for v,s in t['order']:
            seen[s]+=1
            if seen[s]==2:
                assert (v,s)==t['stop'] and s==t['pointer']
                break
    assert TRACE[0]['retain']==TRACE[1]['src']['L'][1]
    assert TRACE[0]['pointer']==TRACE[1]['old_pointer']
    assert TRACE[0]['after_unread']['R']==TRACE[1]['src']['R'][1]
    assert TRACE[0]['after_unread']['L']==TRACE[1]['before_unread']['L']==TRACE[1]['after_unread']['L']
class Svg:
    def __init__(self,h,title,desc):
        self.h=h
        self.items=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{h}pt" viewBox="0 0 {W} {h}">',
                    f'<title>{escape(title)}</title><desc>{escape(desc)}</desc>']
        self.rect(0,0,W,h,fill='white',stroke='none')
    def group(self,name): self.items.append(f'<g id="{name}">')
    def end(self): self.items.append('</g>')
    def text(self,x,y,s,size=6.6,bold=False,italic=False,anchor='start',fill=INK):
        att=' font-weight="700"' if bold else ''
        att+=' font-style="italic"' if italic else ''
        self.items.append(f'<text x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}" font-family="Liberation Serif" font-size="{size}"{att} fill="{fill}">{escape(str(s))}</text>')
    def rect(self,x,y,w,h,r=0,fill='none',stroke=LINE,sw=.45,dash=''):
        d=f' stroke-dasharray="{dash}"' if dash else ''
        self.items.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
    def line(self,x,y,a,b,color=LINE,sw=.45,dash=''):
        d=f' stroke-dasharray="{dash}"' if dash else ''
        self.items.append(f'<path d="M {x:.3f} {y:.3f} L {a:.3f} {b:.3f}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{d}/>')
    def pointer(self,x,y,a,b):
        from math import hypot
        u,v=a-x,b-y
        length=hypot(u,v);u/=length;v/=length
        self.line(x,y,a-.25*u,b-.25*v,ORANGE,.8)
        p=[(a,b),(a-2.7*u-1.22*v,b-2.7*v+1.22*u),(a-2.7*u+1.22*v,b-2.7*v-1.22*u)]
        self.items.append(f'<polygon points="{" ".join(f"{q:.3f},{r:.3f}" for q,r in p)}" fill="{ORANGE}"/>')
    def circle(self,x,y,r=4.3,fill='white',stroke=SUB,sw=.45):
        self.items.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def token(self,x,y,val,winner=False,trigger=False,r=4.3,size=6.65):
        self.circle(x,y,r,WIN if winner else ('#fff8ef' if trigger else 'white'),ORANGE if trigger else SUB,.55 if trigger else .45)
        if trigger: self.circle(x,y,r+1.36,'none',ORANGE,.49)
        self.text(x,y+size*.325,val,size,trigger,anchor='middle',fill=DARK if trigger else INK)
    def tag(self,x,y,s,trigger=False):
        self.text(x,y,s,6.5,True,anchor='middle',fill=DARK if trigger else SUB)
    def vals(self,vals,none="∅"): return ", ".join(map(str,vals)) if vals else none
    def capsule(self,x,y,w,txt,dash=False,bg='white',size=6.6):
        self.rect(x-w/2,y-5.7,w,11.4,2.5,bg,SUB if dash else LINE,.45,"1.3 .9" if dash else "")
        self.text(x,y+size*.325,txt,size,anchor='middle')
    def save(self,stem):
        s=ROOT/f'{stem}.svg';s.write_text('\n'.join(self.items+['</svg>'])+'\n',encoding="utf-8")
        subprocess.run(['inkscape',str(s),'--export-type=pdf',f'--export-filename={ROOT/stem}.pdf'],check=True)
def top(s,title,y,x):
    s.text(x,y,title,8.15,True)
def update_tree(s,t,bx,y):
    # Node state: bottom-center arrow is the *new* refill pointer.
    pos={"L":bx-23,"R":bx+23}
    s.capsule(bx,y,45,"Stored P: "+s.vals(t["retain"]),bg=METAL)
    yy=y+16.6
    for slot,x in pos.items():
        if slot==t["pointer"]:s.pointer(bx,y+5.8,x,yy-6.6)
        else:s.line(bx,y+5.8,x,yy-5.7,LINE)
        unread=t["after_unread"][slot]
        s.capsule(x,yy,40,slot+": "+s.vals(unread),bool(unread))
def rank_strip(s,t,xs,y):
    for i,(v,slot) in enumerate(t["order"]):
        s.token(xs[i],y,v,i<2,(v,slot)==t["stop"])
        s.tag(xs[i],y+11.2,slot+(" · 2/2" if (v,slot)==t["stop"] else ""),(v,slot)==t["stop"])
def version_a():
    # Two parallel local replays: inputs and next state remain directly above/below their rank order.
    s=Svg(94.164,"Which child is next? Two local replays (h=2)",
          "Construction slots are child L [3,7] and child R [1,5]. On refresh, old pointer R puts the replacement [6,14] in R and retained parent [5,7] in L. The rank strip separates emitted winner and retained loser; the first second slot entry sets the next pointer. Unread child state and canonical rows are preserved.")
    s.line(120.123,2.3,120.123,91.5)
    for i,t in enumerate(TRACE):
        x=[1.7,123.35][i]; w=115.2; mid=x+w/2
        s.group(["tree-construction","path-refresh"][i])
        top(s,t['title'],8.6,x+2)
        s.text(x+2,17.7,"P starts empty" if not t["old_pointer"] else "Old pointer: R · L unread: 12, 16",6.45,fill=SUB)
        s.rect(x+1.8,21.5,54.5,14.1,2,fill='#f8f7f4',stroke='none')
        s.rect(x+59,21.5,54.5,14.1,2,fill='#f8f7f4',stroke='none')
        for j,slot in enumerate("LR"):
            src,vals=t["src"][slot]
            s.text(x+4.2+57.2*j,27.3,slot,6.25,True,fill=DARK)
            s.text(x+52.5+57.2*j,27.3,src,6.15,fill=SUB,anchor="end")
            s.text(x+52.5+57.2*j,33.8,s.vals(vals),7,True,anchor='end')
        s.line(x+2,45.1,x+53.7,45.1,SUB,.42)
        s.line(x+61.5,45.1,x+113.2,45.1,SUB,.42)
        s.text(x+27.8,42.1,"Winner",6.25,True,anchor="middle")
        s.text(x+87.4,42.1,"Loser",6.25,True,anchor="middle")
        rank_strip(s,t,[x+14.8,x+39.5,x+73.5,x+97.5],50.9)
        s.line(x+2,64.15,x+113.2,64.15)
        s.text(x+2,71.25,"Updated node",6.4,True,fill=SUB)
        update_tree(s,t,mid+7.5,70.95)
        s.end()
    s.save("pointer-A")
def version_b():
    # Row comparison, with logs rather than duplicated before/after tree silhouettes.
    s=Svg(108.6,"Which child is next? Two rank ledgers (h=2)",
          "Read left to right. In each of two local replays, the first two ranked rows are the winner, the last two remain in P, and the first slot to hit entry 2/2 determines the next pointer. On refresh the old right pointer admits replacement [6,14] into R while stored loser [5,7] occupies L.")
    s.text(2,8.3,"In rank order, the first slot to supply two rows sets the pointer.",8.35,True)
    s.text(3,18.6,"Replay inputs",6.65,True,fill=SUB)
    s.text(73,18.6,"Ranked rows",6.65,True,fill=SUB)
    s.text(177,18.6,"Updated node",6.65,True,fill=SUB)
    for i,t in enumerate(TRACE):
        y=22+39.5*i
        s.group(["tree-construction","path-refresh"][i])
        s.rect(0.6,y,239.05,38.5,3,'#faf8f5','#ded7ce',.45)
        s.rect(68.5,y+.8,102.8,36.9,0,'white','none')
        s.line(68.6,y+3,68.6,y+35.3)
        s.line(171.3,y+3,171.3,y+35.3)
        s.text(3.35,y+7.9,t['title'],6.9,True)
        s.text(3.35,y+15,"No stored parent" if i==0 else "Old pointer: R · L unread",6.1,fill=SUB)
        for j,slot in enumerate("LR"):
            src,vals=t["src"][slot]
            yy=y+24+9.4*j
            s.text(3.35,yy,slot,6.6,True,fill=DARK)
            s.text(11,yy,src,6.5)
            s.text(65.5,yy,s.vals(vals),6.8,True,anchor="end")
        s.text(91,y+8.0,"Winner",6.5,True,anchor="middle")
        s.text(148.5,y+8.0,"Loser",6.5,True,anchor="middle")
        s.line(73.2,y+10.7,113.8,y+10.7,SUB,.44)
        s.line(127.6,y+10.7,168.2,y+10.7,SUB,.44)
        rank_strip(s,t,[79.6,102.3,136.8,159.5],y+20.05)
        cx=205.4
        s.capsule(cx,y+10.9,31,"P: "+s.vals(t["retain"]),bg=METAL)
        for j,slot in enumerate("LR"):
            xx=188.8+j*33.2; yy=y+28.7
            if slot==t["pointer"]:s.pointer(cx,y+16.7,xx,yy-6.6)
            else:s.line(cx,y+16.7,xx,yy-5.7)
            unread=t["after_unread"][slot]
            s.capsule(xx,yy,28.4,""+slot+": "+s.vals(unread),bool(unread),size=6.05)
        s.end()
    s.text(W/2,105.8,"P: stored parent segment     ·     Dashed box: unread rows",6.2,anchor='middle',fill=SUB)
    s.save("pointer-B")
def preview():
    files=['baseline','pointer-A','pointer-B']
    d=fitz.open()
    for f in files:
        with fitz.open(ROOT/f'{f}.pdf') as z:
            a=d.new_page(width=W+20,height=129.5)
            a.insert_text((10,9),f if f!='baseline' else 'Baseline (canonical Fig. 5)',fontname="tiro",fontsize=6.3,color=(.35,.35,.35))
            a.show_pdf_page(fitz.Rect(10,14,10+z[0].rect.width,14+z[0].rect.height),z,0)
            z[0].get_pixmap(matrix=fitz.Matrix(3,3),alpha=False).save(ROOT/f'{f}.png')
    d.save(ROOT/'native-compare.pdf',garbage=4,deflate=True)
def main():
    check()
    ROOT.joinpath('trace.json').write_text(json.dumps(TRACE,indent=2)+'\n')
    version_a();version_b();preview()
if __name__=='__main__':main()

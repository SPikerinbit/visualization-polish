from pathlib import Path
from html import escape
from math import hypot
D=Path(__file__).resolve().parent
s=['<svg xmlns="http://www.w3.org/2000/svg" width="240.247pt" height="93.906pt" viewBox="0 0 241 94.2"><title>Pointer assignment across construction and refresh</title><desc>With h=2 the first slot to contribute twice decides the next pointer. Read the four values left to right in each replay. At construction the third value, 5, exhausts R; the loser [5,7] stays at the parent and enters L together at the next replay. Then the third value, 7, exhausts L. Dashed rings mark unread child rows.</desc><rect width="241" height="94.2" fill="white"/><g font-family="Liberation Serif,serif">']
ink='#282B2B'; gray='#565958'; light='#CCD0CB'; gold='#915807'; goldf='#FFE3AE'; blue='#3F6675'; bluef='#E3EFF1'; win='#DCEFEB'; wh='white'
def add(z):s.append(z)
def txt(x,y,t,size=7.1,col=ink,b=False,align='middle',it=False):
 add(f'<text x="{x}" y="{y}" text-anchor="{align}" font-size="{size}" fill="{col}" font-weight="{"bold" if b else "normal"}" font-style="{"italic" if it else "normal"}">{escape(t)}</text>')
def path(d,c=gray,w=.55,fill='none',dash=''):
 add(f'<path d="{d}" stroke="{c}" stroke-width="{w}" fill="{fill}" stroke-linecap="round" stroke-linejoin="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def rect(x,y,w,h,r,fill=wh,c='none',sw=.6):
 add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')
def circ(x,y,r,fill=wh,c=gray,w=.5,dash=''):
 add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{c}" stroke-width="{w}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def ah(x,y,dx,dy,col,sz=2.1):
 n=hypot(dx,dy); dx,dy=dx/n,dy/n
 a=x-dx*sz; b=y-dy*sz
 path(f'M{x} {y} L{a-dy*sz*.46} {b+dx*sz*.46} L{a+dy*sz*.46} {b-dx*sz*.46} Z',col,.25,col)
def pair(x,y,vs,mode='plain'):
 # Same pair silhouette whether the segment occupies a child slot or the parent.
 if mode=='unread':
  for xx,v in zip([x-5.8,x+5.8],vs):
   circ(xx,y,5.25,wh,'#747876',.55,'1.5 1')
   txt(xx,y+2.1,str(v),6.8,gray)
 else:
  if mode=='tracked': fill,stroke,wt=bluef,blue,1.0
  else: fill,stroke,wt=wh,'#8A908B',.60
  rect(x-12.2,y-5.65,24.4,11.3,5.65,fill,stroke,wt)
  path(f'M{x} {y-4.1} v8.2',stroke,.38)
  for j,v in enumerate(vs): txt(x+(-5.9,5.9)[j],y+2.5,str(v),7.5,ink,mode=='tracked')
def ringnum(x,y,v,kind):
 if kind=='first':
  circ(x,y,6.45,'white',gold,.83); circ(x,y,4.98,goldf,gold,.55)
 else: circ(x,y,5.35,win if kind=='winner' else wh,'#176A64',.60)
 txt(x,y+2.48,str(v),7.5,ink,kind=='first')
# A continuous visible state-equality connector, behind the tokens. It names no source row.
path('M70.5 64.9 H113.5 Q117.6 64.9 117.6 60.8 V27.1 Q117.6 23.1 121.7 23.1 H136.4',blue,.77)
ah(137.2,23.1,1,0,blue,2.3)
for i,x in enumerate([0,126.5]):
 build=i==0; cx=x+57.25
 txt(x+56.75,6.85, '(a) Tree construction' if build else '(b) Path refresh',8.65,ink,True)
 # Inputs form explicit local slots, independent of source runs.
 u,v=x+30,x+85
 for k,(sx,cap,dat) in enumerate(zip([u,v],['Left child','Right child'] if build else ['Old parent','Refill from R'],[(3,7),(1,5)] if build else [(5,7),(6,14)])):
  txt(sx,15.9,cap,6.85,blue if (not build and k==0) else gray,not build and k==0)
  txt(sx-17.2,25.6,'LR'[k],7.,ink,True)
  pair(sx,23.1,dat,'tracked' if (not build and k==0) else 'plain')
 # One central read direction; under the values the slot labels are on their own baseline.
 path(f'M{x+35.9} 33.1 H{x+7.6} Q{x+6.7} 33.1 {x+6.7} 34 V56.7 Q{x+6.7} 57.6 {x+7.6} 57.6 H{x+106.8} Q{x+107.7} 57.6 {x+107.7} 56.7 V34 Q{x+107.7} 33.1 {x+106.8} 33.1 H{x+78.6}', '#C9955D',.54,dash='2.15 1.5')
 txt(cx,35.1,'Replay order',6.9,gray,True)
 coords=[x+20,x+45,x+70,x+95]
 vals=(1,3,5,7) if build else (5,6,7,14)
 slots='RLRL' if build else 'LRLR'
 for j,(tx,num,slot) in enumerate(zip(coords,vals,slots)):
  ringnum(tx,43.45,num,'winner' if j<2 else 'first' if j==2 else 'other')
  txt(tx,55.0,slot+(' · 2/2' if j==2 else ''),6.7,gold if j==2 else gray,j==2)
 # The local tree is the only output depiction. 
 y=64.9; L=(cx-31,79.1); R=(cx+31,79.1)
 for k,(xx,yy) in enumerate([L,R]):
  hot=(build and k==1) or (not build and k==0); sx=cx+(-7.5,7.5)[k]; sy=y+4.65; ex=xx+(5,-5)[k]; ey=yy-5.25
  path(f'M{sx} {sy} L{ex} {ey}',gold if hot else '#929994',1.13 if hot else .52)
  if hot: ah(ex,ey,ex-sx,ey-sy,gold,3)
 txt(cx-15,67.15,'P',7,gray,False,'end')
 pair(cx,y,(5,7) if build else (7,14),'tracked' if build else 'plain')
 txt(L[0]-14.4,81.3,'L',6.8,gray,False,'end')
 txt(R[0]+14.4,81.3,'R',6.8,gray,False,'start')
 pair(*L,(12,16),'unread')
 if build:pair(*R,(6,14),'unread')
 else: 
  circ(*R,5.05,wh,'#ABB0AD',.5);txt(R[0],R[1]+2.05,'∅',6.85,gray)
# Single line, distinct marks. These are encodings actually used in the figure.
y=91.0
circ(9,y-1.5,2.4,win,'#176A64',.55); txt(13.1,y+.55,'Winner',6.65,ink,False,'start')
circ(45,y-1.5,2.45,wh,gray,.6,'1.3 .8');txt(49.5,y+.55,'Unread',6.65,ink,False,'start')
circ(82,y-1.5,3.1,wh,gold,.68);circ(82,y-1.5,1.86,goldf,gold,.5);txt(87,y+.55,'First exhausted',6.65,ink,False,'start')
path(f'M133 {y-4.1} h8 v5.1 h-8 z','#C9955D',.54,dash='2.15 1.5');txt(143.4,y+.55,'Call-result excerpt',6.65,ink,False,'start')
path(f'M199 {y-1.5} h7',gold,1);ah(206.4,y-1.5,1,0,gold,2.6);txt(209,y+.55,'Pointer',6.65,ink,False,'start')
s+=['</g></svg>']
svg=''.join(s).encode()
(D/'pointer.svg').write_bytes(svg)
if __name__ == '__main__':
 from subprocess import run
 from tempfile import TemporaryDirectory
 import os
 with TemporaryDirectory() as td:
  env=dict(os.environ,XDG_CACHE_HOME=td,XDG_CONFIG_HOME=td)
  run(['inkscape',str(D/'pointer.svg'),'-o',str(D/'pointer.pdf')],env=env,check=True)
 run(['pdftoppm','-scale-to','950','-png','-singlefile',str(D/'pointer.pdf'),str(D/'proof')],check=True)

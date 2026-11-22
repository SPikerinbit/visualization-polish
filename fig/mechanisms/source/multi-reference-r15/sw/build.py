"""R15 Fig. 3. Experimental vector master; 1 pt = 1 manuscript pt."""
from pathlib import Path
import math,xml.etree.ElementTree as E
from xml.sax.saxutils import escape
import subprocess,fitz
out=Path(__file__).resolve().parent
W,H=240.24655,83.4
S=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}"><title>Sliding-window merge: why the safe prefix stops</title><desc>Four sorted runs. In rounds 1 and 2 the first emptied buffer with unread input sets the cutoff. The same amber tail is traced from the by-run window to the end of the ranked emitted prefix. With no unread input all six remaining rows are safe.</desc><rect width="100%" height="100%" fill="white"/><g font-family="Liberation Serif,serif">']
def draw(s): S.append(s)
ink='#1A2425'; muted='#4E5A5C'; rail='#B7C1C0';lite='#EEF1F0'; amber='#915807'; amberlight='#FFE3AE'; green='#176A64'; sage='#DCEFEB'; pale='#F5F7F6'; white='#FFFFFF'
def tx(x,y,t,fs=6.2,bold=False,clr=ink,anchor='start',style=''):
 draw(f'<text x="{x}" y="{y}" fill="{clr}" font-size="{fs}" font-weight="{("bold" if bold else "normal")}" text-anchor="{anchor}" {style}>{escape(str(t))}</text>')
def rect(x,y,w,h,col,edge='none',lw=.45,ext=''):
 draw(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{col}" stroke="{edge}" stroke-width="{lw}" {ext}/>')
def path(d,stroke=muted,lw=.6,fill='none',ext=''):
 draw(f'<path d="{d}" stroke="{stroke}" stroke-width="{lw}" fill="{fill}" stroke-linejoin="round" {ext}/>')
def line(x,y,x2,y2,col=rail,lw=.42):path(f'M{x:.2f} {y:.2f}L{x2:.2f} {y2:.2f}',col,lw)
def token(cx,cy,v,role,wit=False):
 if role=='new': rect(cx-3.58,cy-4.05,7.16,8.05,lite)
 if wit:
  rect(cx-3.68,cy-4.15,7.36,8.35,amberlight)
  line(cx-3.68,cy+4.03,cx+3.68,cy+4.03,amber,.87)
 tx(cx,cy+2.35,v,6.7,bold=wit,clr=amber if wit else (muted if role=='unread' else ink),anchor='middle')
rounds=[
 ([[12,16],[6,14],[11,15],[10,13]],[[3,7],[1,5],[2,8],[4,9]],[],[1,2,3,4,5,7,8,9],5,5,1),
 ([[16],[],[15],[13]],[[7,12],[6,14],[8,11],[9,10]],[7,8,9],[6,7,8,9,10,11,12,14],5,10,3),
 ([[],[],[],[]],[[12,16],[14],[11,15],[13]],[11,12,14],[11,12,13,14,15,16],6,None,None)
]
width=68;pitch=72;left=27
for y,t in [(26.8,'Unread'),(40.0,'Window'),(60.9,'Ranked')]:tx(.55,y,t,6.6,True)
for i,(us,win,keep,result,n,witness,run_id) in enumerate(rounds):
 x=left+pitch*i
 tx(x+width/2,6.8,'Round '+str(i+1),7.25,True,anchor='middle')
 line(x,9.1,x+width,9.1)
 dx=width/4
 for k,values in enumerate(us):
  hot=k==run_id;cx=x+(k+.5)*dx
  tx(cx,17.2,'R'+str(k+1),6.35,hot,amber if hot else muted,anchor='middle')
  if k:line(x+k*dx,11.4,x+k*dx,29.3,'#D9DFDE',.36)
  for j,v in enumerate(values): token(cx+(j-(len(values)-1)/2)*7.9,24.55,v,'unread')
  if not values:tx(cx,26.8,'–',6.4,clr=rail,anchor='middle')
 # light frame, by-run separators. Row shading differentiates new from retained in grayscale.
 rect(x,32.3,width,10.45,white,rail)
 for k,values in enumerate(win):
  cx=x+(k+.5)*dx
  if k:line(x+k*dx,32.3,x+k*dx,42.75)
  for j,v in enumerate(values):
   xx=cx+(j-(len(values)-1)/2)*7.9
   token(xx,37.48,v,'retained' if v in keep else 'new',v==witness)
 # Ranked list is split precisely after last legal row. Light fill and bracket span ALL emitted rows.
 slot=8.0;gap=2.2 if n!=len(result) else 0
 xl=x+(width-(len(result)*slot+gap))/2
 rect(xl,53.4,n*slot,10.65,sage)
 if n!=len(result):rect(xl+n*slot+gap,53.4,(len(result)-n)*slot,10.65,white,rail)
 for j,v in enumerate(result):
  xx=xl+(j+.5)*slot+(gap if j>=n else 0)
  token(xx,58.65,v,'result',v==witness)
 line(xl,64.08,xl+n*slot,64.08,green,.74)
 if witness:
  if i==0:tx(x+.3,50.1,'Stop after 5',5.65,True,amber)
  else:tx(x+.3,50.1,'Stop after 10',5.65,True,amber)
 else:
  tx(x+width*.5,49.8,'All buffered',5.85,clr=muted,anchor='middle')
 tx(xl+n*slot/2,71.1,'Emit '+str(result[0])+'–'+str(result[n-1]),6.55,True,green,anchor='middle')
 if n!=len(result):tx(xl+gap+(n+(len(result)-n)/2)*slot,71.1,'Retain',5.95,clr=muted,anchor='middle')
line(0.55,73.9,W-1.6,73.9)
rect(4,77,7.1,5.7,lite,rail,.23);tx(13,82.3,'New',5.9,clr=muted)
rect(36,77,7.1,5.7,white,rail);tx(45,82.3,'Retained',5.9,clr=muted)
rect(82,77,7.1,5.7,amberlight);line(82,82.4,89.1,82.4,amber,.83);tx(91,82.3,'Tail of first buffer to refill',5.9,clr=muted)
rect(170,77,7.1,5.7,sage);line(170,82.4,177.1,82.4,green,.74);tx(179,82.3,'Emitted prefix',5.9,clr=muted)
draw('</g></svg>');src=out/'sw.svg';src.write_text('\n'.join(S),encoding='utf8')
subprocess.run(["inkscape",str(src),"--export-filename="+str(out/"sw.pdf")],check=True)
doc=fitz.open(out/'sw.pdf');print(doc[0].rect)
for scale,name in [(3,'print'),(1.5,'small')]:
 doc[0].get_pixmap(matrix=fitz.Matrix(scale,scale)).save(out/(name+'.png'))

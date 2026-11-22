from html import escape
from math import hypot
from pathlib import Path
import subprocess
D=Path(__file__).resolve().parent
s=['<svg xmlns="http://www.w3.org/2000/svg" width="240.24655pt" height="94.164pt" viewBox="0 0 240.24655 94.164"><title>Pointer creation and update at a replay node</title><desc>Construction starts with no pointer, then points to its right child. Refresh starts with that right pointer, and then redirects it to the left child. The retained [5,7] at P is the source of refresh slot L. The shallow inset gives replay order; the third token reaches 2/2 and triggers the new pointer.</desc><rect width="240.24655" height="94.164" fill="white"/><g font-family="Nimbus Roman,Liberation Serif,serif">']
ink="#292D30"; gray="#54585A"; edge="#929995"; soft="#D8DBD7"; gold="#915807"; goldf="#FFE3AE"; blue="#436B7D"; bluef="#E8F1F3"; win="#DCEFEB"
def add(t): s.append(t)
def tx(x,y,t,z=6.1,c=ink,b=False,a="middle",i=False):
 add(f'<text x="{x}" y="{y}" text-anchor="{a}" font-size="{z}" fill="{c}" font-weight="{"bold" if b else "normal"}" font-style="{"italic" if i else "normal"}">{escape(t)}</text>')
def path(d,c=edge,w=.52,f="none",da=""):
 add(f'<path d="{d}" fill="{f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"'+(f' stroke-dasharray="{da}"' if da else '')+'/>')
def rect(x,y,w,h,r,f,c,sw=.53):
 add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{f}" stroke="{c}" stroke-width="{sw}"/>')
def circle(x,y,r,f,c,sw=.53,da=""):
 add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{f}" stroke="{c}" stroke-width="{sw}"'+(f' stroke-dasharray="{da}"' if da else '')+'/>')
def head(x,y,dx,dy,c,sz=2.6):
 n=hypot(dx,dy);dx,dy=dx/n,dy/n;k=.43
 ax,ay=x-sz*dx,y-sz*dy
 path(f'M{x:.3f} {y:.3f} L{ax-sz*k*dy:.3f} {ay+sz*k*dx:.3f} L{ax+sz*k*dy:.3f} {ay-sz*k*dx:.3f} Z',c,.23,c)
def pair(x,y,vals,role):
 if not vals:
  circle(x,y,4.55,"white","#A2A8A4")
  tx(x,y+2,"∅",6.2,gray)
  return
 if role in ("stored","tracked","active"):
  rect(x-10.1,y-4.6,20.2,9.2,4.55,bluef if role=="tracked" else "white",blue if role=="tracked" else edge,.78 if role=="tracked" else .52)
  path(f'M{x} {y-3.25} v6.5',blue if role=="tracked" else edge,.38)
 for j,v in enumerate(vals):
  xx=x+(-5.1,5.1)[j]
  if role=="unread": circle(xx,y,4.72,"white",gray,.54,'1.24 .87')
  tx(xx,y+2.1,str(v),6.45,ink,role=="tracked")
def state(x,y,label,ptr,p,l,r):
 add(f'<g data-state="{label.lower()}" data-pointer="{ptr}">')
 xc=x+69; xl=x+44; xr=x+94; cy=y+14.1
 tx(x+5,y+1,label,6.9,ink,True,a="start")
 tx(x+5,y+9.25,"No pointer" if ptr=="∅" else "Pointer: "+ptr,6.3,gray if ptr=="∅" else gold,False,a="start")
 for slot,xx in [('L',xl),('R',xr)]:
  sx=xc+(-4.6 if slot=='L' else 4.6); sy=y+3.55
  ex=xx+(5.1 if slot=='L' else -5.1); ey=cy-4.75
  active=(slot==ptr)
  path(f'M{sx} {sy} L{ex} {ey}',gold if active else edge,1.08 if active else .51)
  if active:head(ex,ey,ex-sx,ey-sy,gold)
 for tag,xx,yy in [('P',xc+13.4,y),('L',xl-12.8,cy),('R',xr+12.8,cy)]:
  tx(xx,yy+1.96,tag,6.4,gray if tag!=ptr else gold,tag==ptr,"start" if tag in 'PR' else "end")
 pair(xc,y,*p);pair(xl,cy,*l);pair(xr,cy,*r)
 add('</g>')
def replay(x,vals,slots):
 y=74.48
 path(f'M{x+44.1} 66.95 H{x+4.0} V85.1 H{x+111.6} V66.95 H{x+82.9}','#AC8050',.56,da='1.85 1.2')
 tx(x+63.5,68.55,"Replay order",6.35,gray,True)
 for j,(v,slot) in enumerate(zip(vals,slots)):
  cx=x+19+26*j
  if j==2:
   circle(cx,y,4.86,"white",gold,.68);circle(cx,y,3.79,goldf,gold,.47)
  else:
   circle(cx,y,3.98,win if j<2 else "white","#176A64",.52)
  tx(cx,y+2.04,str(v),6.33,ink,j==2)
  tx(cx,83.1,slot+(' 2/2' if j==2 else ' 1/2' if j<2 else ''),6.12,gold if j==2 else gray,j==2)
def leg():
 y=90.65
 circle(6,y,2.58,win,"#176A64")
 tx(10.3,92.66,'Winner',6.35,a="start")
 circle(46,y,2.58,"white",gray,.54,'1.24 .87')
 tx(50.2,92.66,'Unread',6.35,a="start")
 circle(88,y,2.98,"white",gold,.65);circle(88,y,1.93,goldf,gold,.42)
 tx(93.2,92.66,'First exhausted',6.35,a="start")
 path('M145 90.65 H153',gold,.91);head(153,90.65,8,0,gold,2.1)
 tx(156,92.66,'Pointer',6.35,a="start")
 path('M182 88.2 H190 V93.1 H182 Z','#AC8050',.52,da='1.85 1.2')
 tx(193,92.66,'Call-result excerpt',6.05,a="start")
path('M120.12 1.3 V85.1',soft,.52)
for i,x in enumerate([0,122.3]):
 t=not i; cx=x+57.8
 add('<g id="'+('construction' if t else 'refresh')+'">')
 tx(cx,7.7,'(a) Tree construction' if t else '(b) Path refresh',8.7,b=True)
 tx(cx,15.15,'Slot L: left child  ·  Slot R: right child' if t else 'L: old P [5,7]  ·  R: refill from R',5.95,gray)
 state(x,21.55,'Before','∅' if t else 'R',(None,'blank') if t else ((5,7),'tracked'),((3,7),'active') if t else ((12,16),'unread'),((1,5),'active') if t else ((6,14),'active'))
 state(x,43.50,'After','R' if t else 'L',((5,7),'tracked') if t else ((7,14),'stored'),((12,16),'unread'),((6,14),'unread') if t else (None,'blank'))
 replay(x,(1,3,5,7) if t else (5,6,7,14),'RLRL' if t else 'LRLR')
 add('</g>')
leg();add('</g></svg>')
(D/'pointer.svg').write_text('\n'.join(s))
subprocess.run(['inkscape',str(D/'pointer.svg'),'--export-type=pdf','--export-filename='+str(D/'pointer.pdf')],check=True)
subprocess.run(['pdftoppm','-png','-singlefile','-r','300',str(D/'pointer.pdf'),str(D/'proof')],check=True)

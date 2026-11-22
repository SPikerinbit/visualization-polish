from html import escape
from math import hypot
from pathlib import Path
import subprocess
D=Path(__file__).resolve().parent
s=['<svg xmlns="http://www.w3.org/2000/svg" width="240.24655pt" height="91.9pt" viewBox="0 0 240.24655 91.9"><title>Pointer creation and update at a replay node</title><desc>Construction starts with no pointer, then points to its right child. Refresh starts with that right pointer, and then redirects it to the left child. The retained [5,7] at P is the source of refresh slot L. The shallow inset gives replay order; the third token reaches 2/2 and triggers the new pointer.</desc><rect width="240.24655" height="91.9" fill="white"/><g font-family="Nimbus Roman,Liberation Serif,serif">']
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
  circle(x,y,4.75,"white","#A2A8A4")
  tx(x,y+2.2,"∅",6.7,gray)
  return
 if role in ("stored","tracked","active"):
  rect(x-10.1,y-4.6,20.2,9.2,4.55,bluef if role=="tracked" else "white",blue if role=="tracked" else edge,.78 if role=="tracked" else .52)
  path(f'M{x} {y-3.25} v6.5',blue if role=="tracked" else edge,.38)
 for j,v in enumerate(vals):
  xx=x+(-5.1,5.1)[j]
  if role=="unread": circle(xx,y,4.72,"white",gray,.54,'1.24 .87')
  tx(xx,y+2.25,str(v),6.8,ink,role=="tracked")
def state(x,y,label,ptr,p,l,r,l_slot=False):
 add(f'<g data-state="{label.lower()}" data-pointer="{ptr}">')
 xc=x+68; xl=x+42.5; xr=x+93.5; cy=y+14.6
 tx(x+5,y+2.2,label,7.1,ink,True,a="start")
 for slot,xx in [('L',xl),('R',xr)]:
  sx=xc+(-4.6 if slot=='L' else 4.6); sy=y+3.55
  ex=xx+(5.1 if slot=='L' else -5.1); ey=cy-4.75
  active=(slot==ptr)
  path(f'M{sx} {sy} L{ex} {ey}',gold if active else edge,1.08 if active else .51)
  if active:head(ex,ey,ex-sx,ey-sy,gold,3.2)
 for tag,xx,yy in [('P',xc+13.4,y),('L',xl-12.8,cy),('R',xr+12.8,cy)]:
  tx(xx,yy+2.2,'P (slot L)' if tag=='P' and l_slot else tag,6.65,blue if tag=='P' and l_slot else (gray if tag!=ptr else gold),tag==ptr or (tag=='P' and l_slot),"start" if tag in 'PR' else "end")
 pair(xc,y,*p);pair(xl,cy,*l);pair(xr,cy,*r)
 add('</g>')
def replay(x,vals,slots):
 y=72.25
 path(f'M{x+44.1} 64.65 H{x+4.0} V82.45 H{x+111.6} V64.65 H{x+82.9}','#AC8050',.56,da='1.85 1.2')
 tx(x+63.5,66.25,"Replay order",6.35,gray,True)
 for j,(v,slot) in enumerate(zip(vals,slots)):
  cx=x+19+26*j
  if j==2:
   circle(cx,y,5.05,"white",gold,.68);circle(cx,y,3.79,goldf,gold,.47)
  else:
   circle(cx,y,4.2,win if j<2 else "white","#176A64",.52)
  tx(cx,y+2.2,str(v),6.75,ink,j==2)
  tx(cx,80.6,slot+(' 2/2' if j==2 else ''),6.65,gold if j==2 else gray,j==2)
def leg():
 y=87.6
 circle(23,y,2.8,win,"#176A64")
 tx(28,89.7,'Winner',6.35,a="start")
 circle(75,y,2.8,"white",gray,.54,'1.24 .87')
 tx(80,89.7,'Unread',6.35,a="start")
 circle(126,y,2.98,"white",gold,.65);circle(126,y,1.93,goldf,gold,.42)
 tx(131,89.7,'First exhausted',6.35,a="start")
 path('M187 87.6 H197',gold,.91);head(197,87.6,8,0,gold,2.1)
 tx(201,89.7,'Pointer',6.35,a="start")
path('M120.12 1.3 V82.45',soft,.52)
for i,x in enumerate([0,122.3]):
 t=not i; cx=x+57.8
 add('<g id="'+('construction' if t else 'refresh')+'">')
 tx(cx,7.7,'(a) Tree construction' if t else '(b) Path refresh',8.7,b=True)
 state(x,19.2,'Before','∅' if t else 'R',(None,'blank') if t else ((5,7),'tracked'),((3,7),'active') if t else ((12,16),'unread'),((1,5),'active') if t else ((6,14),'active'),l_slot=not t)
 state(x,41.9,'After','R' if t else 'L',((5,7),'tracked') if t else ((7,14),'stored'),((12,16),'unread'),((6,14),'unread') if t else (None,'blank'))
 replay(x,(1,3,5,7) if t else (5,6,7,14),'RLRL' if t else 'LRLR')
 add('</g>')
leg();add('</g></svg>')
(D/'pointer.svg').write_text('\n'.join(s))
subprocess.run(['inkscape',str(D/'pointer.svg'),'--export-type=pdf','--export-filename='+str(D/'pointer.pdf')],check=True)
subprocess.run(['pdftoppm','-png','-singlefile','-r','300',str(D/'pointer.pdf'),str(D/'proof')],check=True)

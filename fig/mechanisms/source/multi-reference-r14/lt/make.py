"""One-path segmented loser-tree refresh; SVG and PDF at native journal width."""
from pathlib import Path
from math import hypot
import html,subprocess,os
D=Path(__file__).resolve().parent
W,H=250,98
o=[]
def p(x):o.append(x)
ink='#1A2425'; gray='#4E5A5C';dim='#748482';edge='#A0ADAF'; pale='#B7C1C0'
gold='#915807'; amber='#FFE3AE'; teal='#176A64'; sea='#DCEFEB'; white='#FFFFFF'
def line(x,y,X,Y,e=edge,w=.65,d=''):
 p(f'<path d="M{x} {y} L{X} {Y}" fill="none" stroke="{e}" stroke-width="{w}" stroke-linecap="round" {d}/>')
def arrow(x,y,X,Y,e,w=.9,size=2.8):
 l=hypot(X-x,Y-y);u=(X-x)/l;v=(Y-y)/l
 line(x,y,X-u*size*.5,Y-v*size*.5,e,w)
 p(f'<path d="M{X} {Y} l{-u*size-v*size*.52} {-v*size+u*size*.52} l{v*size*1.04} {-u*size*1.04} z" fill="{e}"/>')
def text(x,y,t,s=6.2,c=ink,a='middle',b=False,it=False):
 p(f'<text x="{x}" y="{y}" text-anchor="{a}" font-size="{s}" fill="{c}" font-weight="{"bold" if b else "normal"}" font-style="{"italic" if it else "normal"}">{html.escape(t)}</text>')
def rect(x,y,w,h,f,e,sw=.6,da=''):
 p(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx=".7" fill="{f}" stroke="{e}" stroke-width="{sw}" {da}/>')
def pair(x,y,vals,kind='stored',w=18.7,h=8.6):
 ec=dim if kind in ('unchanged','unread') else teal if kind in ('output','carry') else gold if kind=='read' else gray
 rect(x-w/2,y-h/2,w,h,sea if kind in ('output','carry') else white,ec, .8 if kind=='output' else .55,'stroke-dasharray="1.7 1.2"' if kind=='unread' else '')
 for j,v in enumerate(vals):
  X=x+(j-.5)*w/2
  if v in (6,14) and kind!='unread':
   rect(X-w/4+.6,y-h/2+.7,w/2-1.2,h-1.45,amber,'none',0)
   line(X-w*.16,y+h/2-1,X+w*.16,y+h/2-1,gold,.52)
  text(X,y+2.15,str(v),6.45,gold if v in (6,14) and kind!='unread' else teal if kind in ('output','carry') else gray if kind in ('unchanged','unread') else ink,b=kind in ('output','carry') or v in (6,14) and kind!='unread')
def header(x,y,n,t):
 text(x,y,n,7.2,gray,'start',True);text(x+9,y,t,7.8,ink,'start',True)
def label(x,y,t):text(x,y,t,6.4,gray)
# Left tree; globally read top down, with only R2 and its two opponents active.
header(1,7.6,'1','Follow the pointer path')
anchor=53.5
pair(anchor,18.65,[1,2],'output');text(37.6,20.65,'Emitted',5.9,gray,'end')
arrow(anchor,26.65,anchor,23.9,gray,.62,2.15)
pair(anchor,31.65,[3,4])
for (x,y,X,Y,c,width,head) in [(49,36.95,34,43.8,gold,1.35,1),(58,36.75,77.1,43.8,pale,.65,0),(26.5,54.1,15.7,62.1,edge,.62,0),(34.5,54.1,40.4,62.1,gold,1.35,1),(77.0,54.1,70.4,62.1,dim,.67,1),(85.1,54.1,95.0,62.1,edge,.62,0)]:
 if head:arrow(x,y,X,Y,c,width,3.0)
 else:line(x,y,X,Y,c,width)
for x,vals,kind in [(30,[5,7],'stored'),(81,[8,9],'unchanged')]:pair(x,49.1,vals,kind)
for i,(x,vals) in enumerate([(13,[12,16]),(41,[6,14]),(69,[11,15]),(96.5,[10,13])]):
 pair(x,67.3,vals,'read' if i==1 else 'unread',21)
 text(x,79.0,['R₁','R₂','R₃','R₄'][i],6.8,gold if i==1 else gray,b=i==1)
# Right, one ordered register and a genuine dataflow replay.
header(113,7.6,'2','Rank the six path rows once')
rx=151; ww=71; yy=17.5;hh=9.4
rect(rx-ww/2,yy-hh/2,ww,hh,white,gray)
for j,v in enumerate([3,4,5,6,7,14]):
 x=rx-ww/2+ww/6*(j+.5)
 if j:line(x-ww/12,yy-hh/2+.6,x-ww/12,yy+hh/2-.6,pale,.45)
 if v in (6,14):
  rect(x-ww/12+.7,yy-hh/2+.7,ww/6-1.4,hh-1.4,amber,'none',0)
  line(x-3.3,yy+hh/2-1.05,x+3.3,yy+hh/2-1.05,gold,.55)
 text(x,yy+2.25,str(v),7.2,gold if v in (6,14) else ink,b=v in (6,14))
text(190,19.7,'one rank map',6.25,gray,'start',it=True)
header(113,30.95,'3','Replay two local matches')
# Two replay junctions, vertical flow. A stored opponent enters each junction from the left.
xc=182.4; xt=213.7; xo=148.4
for y in (47.35,69.1):
 arrow(xo+10.25,y,xc-2.35,y,dim,.64,2.5)
 arrow(xc+2.6,y,xt-10.4,y,dim,.64,2.5)
 p(f'<circle cx="{xc}" cy="{y}" r="1.65" fill="{teal}"/>')
for y,vals in [(47.35,[3,4]),(69.1,[5,7])]:
 pair(xo,y,vals)
text(135.4,49.35,'Root',6.45,gray,'end')
text(135.4,71.1,'Lower',6.45,gray,'end')
text(213.7,39.7,'Keep',6.05,gray)
pair(xt,47.35,[5,6]); pair(xt,69.1,[7,14]); text(235.5,39.7,'Next child',6.05,gray); text(235.5,49.5,'Right',6.2,gray); text(235.5,71.25,'Left',6.2,gray)
pair(xc,37.35,[3,4],'output')
text(xc-12,39.4,'New root',6.15,teal,'end',True)
arrow(xc,45.25,xc,42.45,teal,.95,2.45)
pair(xc,58.2,[5,6],'carry')
text(xc-12,60.35,'Carry',6.15,teal,'end',True)
arrow(xc,67.0,xc,63.1,teal,.95,2.45)
arrow(xc,53.2,xc,49.65,teal,.95,2.45)
pair(xc,80.6,[6,14],'read')
text(xc-12,82.7,'R₂ refill',6.1,gold,'end',True)
arrow(xc,75.5,xc,71.35,teal,.95,2.45)
text(221.6,81.4,'R₂ now empty',5.95,gray)
# Compact print legend; retain semantic classes without a paragraph of prose.
line(1,87.5,249,87.5,pale,.42)
rect(1.1,90.5,6.2,4.8,amber,gold,.5);line(2.1,94.4,6.3,94.4,gold,.5)
text(9.2,95.3,'New from R₂',6.05,ink,'start')
rect(49.8,90.5,6.2,4.8,white,gray,.55);text(58,95.3,'Stored',6.05,ink,'start')
rect(85.4,90.5,6.2,4.8,white,dim,.55,'stroke-dasharray="1.4 .85"');text(93.8,95.3,'Unread',6.05,ink,'start')
rect(119.5,90.5,6.2,4.8,sea,teal,.55);text(127.6,95.3,'Winner',6.05,ink,'start')
arrow(158.3,90.7,158.3,95.9,gold,1.0,2.3);text(163,95.3,'Follow pointer',6.05,ink,'start')
arrow(212,95.9,212,90.7,teal,1.,2.3);text(216.7,95.3,'Replay',6.05,ink,'start')
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}"><title>One path, one ranking, two local replays</title><desc>Following the root pointer reaches R2. Rank the two stored pairs and the refill together, then carry [5,6] up to the root and emit [3,4].</desc><rect width="{W}" height="{H}" fill="white"/><g font-family="Liberation Serif, serif">'+'\n'.join(o)+'</g></svg>'
(D/'lt.svg').write_text(svg)
env=dict(os.environ,XDG_CACHE_HOME=str(D/'cache'),XDG_CONFIG_HOME=str(D/'config'))
subprocess.run(['inkscape',str(D/'lt.svg'),'--export-filename='+str(D/'lt.pdf')],check=True,env=env,stdout=subprocess.DEVNULL)
import fitz
d=fitz.open(D/'lt.pdf')
for sc,n in [(2.8,'zoom'),(1.45,'print')]:d[0].get_pixmap(matrix=fitz.Matrix(sc,sc)).save(D/(n+'.png'))

from pathlib import Path
import sys
import matplotlib as m
m.use('Agg'); m.rcParams.update({'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'SemOrderR18Fig1Type','axes.linewidth':0,'savefig.pad_inches':0})
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Rectangle,Circle,Polygon,PathPatch
from matplotlib.path import Path as MPath
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
W,H=504,148
base=Path(__file__).resolve().parent
fonts=next(iter(Path.cwd().glob('old-zip-preview/tl26-extras/fonts/opentype/public/libertine')),None)
if len(sys.argv)>1: fonts=Path(sys.argv[1]).expanduser()
if not fonts:
 from subprocess import check_output
 import shutil
 if shutil.which('kpsewhich'):
  loc=check_output(['kpsewhich','LinLibertine_R.otf'],text=True).strip()
  if loc: fonts=Path(loc).parent
 if not fonts and shutil.which('fc-match'):
  loc=Path(check_output(['fc-match','-f','%{file}','Linux Libertine O'],text=True))
  if loc.name=='LinLibertine_R.otf': fonts=loc.parent
if not fonts or not (fonts/'LinLibertine_R.otf').is_file():
 raise SystemExit('Run: python build.py /path/to/libertine/opentype (must contain LinLibertine_R, RB, RI .otf).')
ft={k:FontProperties(family="Linux Libertine O",weight="bold" if k=="b" else "normal",style="italic" if k=="i" else "normal",fname=fonts/v) for k,v in {'r':'LinLibertine_R.otf','b':'LinLibertine_RB.otf','i':'LinLibertine_RI.otf'}.items()}
fig=plt.figure(figsize=(W/72,H/72)); ax=fig.add_axes([0,0,1,1],xlim=(0,W),ylim=(H,0));ax.set_axis_off()
black='#202832'; gray='#505c67'; pale='#d7dfe2'; blue='#285d82'; blue2='#dcebf3'; gold='#8a5a16'; gold2='#f9e9c4'; green='#406949'; green2='#deecdc'
def t(x,y,txt,s=7.4,k='r',c=black,align='left'):
 ax.text(x,y,txt,ha=align,va='center',fontproperties=ft[k],fontsize=s,color=c,zorder=8)
def mixed(x,y,parts,s=7.5,c=gray,align='left'):
 # Preserve the original optical centers and one common baseline.
 # Measure each run in its actual embedded font before moving the pen.
 renderer=fig.canvas.get_renderer()
 widths=[renderer.get_text_width_height_descent(txt,FontProperties(fname=ft[k].get_file(),size=s),False)[0]*72/fig.dpi for txt,k in parts]
 dx=sum(widths)*({'left':0,'center':.5,'right':1}[align])
 pen=x-dx
 for (txt,k),w in zip(parts,widths):
  ax.text(pen,y+1.9,txt,ha='left',va='baseline',fontproperties=ft[k],fontsize=s,color=c,zorder=8)
  pen+=w
def ln(p,c=gray,w=.65,d=None):
 xs,ys=zip(*p);o=ax.plot(xs,ys,color=c,lw=w,solid_capstyle='round')[0]
 if d:o.set_dashes(d)
def rect(x,y,w,h,fc='none',ec='none',sw=.6,r=0):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',fc=fc,ec=ec,lw=sw) if r else Rectangle((x,y),w,h,fc=fc,ec=ec,lw=sw))
def poly(pts,c):ax.add_patch(Polygon(pts,closed=True,ec='none',fc=c,zorder=4))
def ar(x1,y1,x2,y2,c=gray,w=.8,hs=2.8,d=None):
 # One filled, slightly inset swept head for every kind of flow. hs is in print points.
 # Shaft stops at the notch instead of protruding behind the head.
 import math
 dx=x2-x1;dy=y2-y1;L=math.hypot(dx,dy);dx/=L;dy/=L
 ln([(x1,y1),(x2-dx*hs*.79,y2-dy*hs*.79)],c,w,d)
 xx,yy=x2-dx*hs,y2-dy*hs
 poly([(x2,y2),(xx-dy*hs*.43,yy+dx*hs*.43),(x2-dx*hs*.79,y2-dy*hs*.79),(xx+dy*hs*.43,yy-dx*hs*.43)],c)
def dot(x,y,s,c):ax.add_patch(Circle((x,y),s,fc=c,ec='none',zorder=5))
def doc(x,y,c):
 rect(x-1.6,y+1.6,8,10,'white',c,.5);rect(x,y,8,10,'white',c,.65)
 for i,l in enumerate([4.8,4.8,3.4]):ln([(x+1.4,y+2.8+i*2.1),(x+1.4+l,y+2.8+i*2.1)],c,.4)
def stage(x,x2,no,txt,c):
 ln([(x,15.8),(x2,15.8)],pale,.56);ln([(x,15.8),(x+13,15.8)],c,1.25)
 t(x,7.5,no,8,'b',c);t(x+15,7.5,txt,10,'b')
stage(1,109,'01','Planning inputs',green);stage(119,283,'02','Merge plan selection',gold);stage(294,503,'03','Execute the selected plan',blue)
# Documents and the query determine run lengths; capacity, demand and token profile enter the planning collector separately.
doc(4,23,green);t(15,28,'Documents',7.65,'b');doc(65,23,blue);t(76,28,'NL query',7.65,'b')
ln([(8,35.5),(8,39),(69,39),(69,35.5)],green,.64)
ar(19,39,19,48.5,green,.68,2.8)
# Meaningful profile marks; no numbered or invented data.
for j,n in enumerate([3,3,2]):
 for i in range(n):rect(15+i*3,50+j*2.5,2.2,1.9,green if i==0 else '#aac7ab')
t(29,52,'Initial run lengths',8,'b');t(15,63,'Items per sorted run',7)
# Compact capacity gauge: slots are unnumbered.
for i in range(4):rect(15+2.6*i,76,2,5,green2 if i<3 else 'white',green,.43)
t(29,79,'Call capacity m',8,'b');t(15,89,'Max items per listwise call',7)
# Ordered result list: vertically arranged lines and downward order cue,
# distinct from the horizontal capacity slots above.
for i,length in enumerate([5.8,4.7,3.5]):
 y=101.2+i*2.5
 dot(15.6,y,.51,green)
 ln([(17.1,y),(17.1+length,y)],green,.58)
ar(25,100.3,25,107.3,green,.56,1.65)
t(29,104,'Requested output',8,'b');t(15,114,'Full Ranking or LIMIT K',7)
rect(15,129,3.2,4.1,blue);rect(19.7,129,7.5,4.1,green2,green,.44)
t(29,131,'Token profile',8,'b');t(15,141,'H: overhead; L: tokens/item',7)
# Collect the four inputs before pointing to the feasible-plan set, not one example.
for yy in [52,79,104,131]: ln([(107.5,yy),(110.8,yy)],green,.5)
ln([(110.8,131),(110.8,27.3)],green,.54); ar(110.8,27.3,117.2,27.3,green,.65,2.65)
# Stage 2: the three candidates are the argument of the estimator, not detached clip art.
t(120,27,'Feasible merge plans',8.3,'b');mixed(282,27,[('b','i'),('(','r'),('k','i'),(') ','r'),('h','i'),(' ≤ ','r'),('m','i')],align='right')
# Local section comparison: one wider window and two genuinely binary trees. All four LT leaves and all retained lengths are explicit.
centers=[142,195,248]
for x,lab,sub in zip(centers,['A   SW','B   LT','C   LT'],['k=5, h=2','k=4, h=2','k=4, h=4']):
 t(x,43,lab,8.5,'b',black,'center');t(x,54,sub,7.4,'i',gray,'center')
for j in range(5):
 for idx in range(3):
  rect(123+j*8,63+idx*4.9,5.7,3.6,blue2 if idx<2 else 'white',blue if idx<2 else '#9ba8af',.45,.55)
rect(121.5,61.5,41,10.8,'none',blue,.75,1.4)
def lt(x,h):
 lx=[x+v for v in [-17,-6,6,17]]
 nx=[x-11.5,x+11.5]
 heights=(62,69.7,77.4)
 # One example refresh path: root → right parent → its left leaf.
 active={(0,0),(1,1),(2,2)}
 muted_border='#7e8a92'; muted_fill='#f1f4f5'; warm='#ae650c'; warm_fill='#ffd99a'
 levels=[[x],nx,lx]
 for lev in (1,2):
  for i,u in enumerate(levels[lev]):
   parent=levels[lev-1][i//2]
   on=(lev,i) in active
   ln([(parent,heights[lev-1]+1.8),(u,heights[lev]-1.8)],warm if on else muted_border,1.08 if on else .53)
 for lev, row in enumerate(levels):
  for i,u in enumerate(row):
   on=(lev,i) in active
   yy=heights[lev]-1.8
   cell=2.18
   ww=cell*h
   rect(u-ww/2,yy,ww,3.6,warm_fill if on else muted_fill,warm if on else muted_border,.61 if on else .49,.34)
   for j in range(1,h):
    ln([(u-ww/2+j*cell,yy+.2),(u-ww/2+j*cell,yy+3.4)],warm if on else muted_border,.4)
lt(195,2);lt(248,4);t(278,77,'…',9,'b',gray,'center')
ln([(123,85),(123,88),(276,88),(276,85)],gray,.56);ar(199.5,88,199.5,94,gray,.65,2.4)
rect(120,95.8,162,42,'#fbf6e9','none',0,2)
t(201,104,'Estimated merge input tokens',8.2,'b',gold,'center')
t(201,117,'H × calls  +  L × item appearances',9,'b',black,'center')
t(201,130,'Select the plan with the lowest estimate.',7.5,'r',gray,'center')
# Stage 3: both modes are tested against aligned layers and a common baseline.
F,K=359,456
t(F,29,'Full Ranking',9.8,'b',blue,'center');t(K,29,'LIMIT K',9.8,'b',gold,'center')
t(F,40,'Plan for all rows',7.5,'r',gray,'center');mixed(K,40,[('Plan for the first ','r'),('K','i'),(' rows','r')],align='center')
ln([(408,23),(408,139)],pale,.5)
def g(x,y,role):
 c={'F':blue,'K':gold,'n':'#aab5b9'}[role];fill={'F':blue2,'K':gold2,'n':'white'}[role]
 rect(x-10.5,y,21,9,fill,c,.64 if role!='n' else .48,1)
 for j in range(3):rect(x-7.0+j*5.3,y+2.6,3.6,3.8,c if role!='n' else '#d6dee0')
# No implied equal cardinality of complete merge layers: these are groups shown in each layer, not complete merge trees.
mixed(294,56.5,[('Layer ','r'),('i','i')])
mixed(294,101,[('Layer ','r'),('i','i'),('+1','r')])
for x in [335,359,383]:
 g(x,52,'F');g(x,96.5,'F')
 ln([(x,61),(x,64.5)],blue,.6);ln([(x,93),(x,96.5)],blue,.6)
ln([(335,64.5),(383,64.5)],blue,.7);ln([(335,93),(383,93)],blue,.7)
ar(340.5,64.5,340.5,91.9,blue,1.0,4.0)
t(349,75,'Materialize',7.5,'b',blue);t(349,84.5,'the full layer',7.5,'b',blue)
for j,x in enumerate([431,455,479]):
 g(x,52,'K' if j==1 else 'n');g(x,96.5,'K' if j==1 else 'n')
ar(451.7,62.2,451.7,95.0,blue,.86,3.6);ar(458.3,95.0,458.3,62.2,gold,.84,3.6,[2.2,1.8])
t(447.5,78.5,'Push rows',7.55,'b',blue,'right');t(462.5,78.5,'Pull',7.55,'b',gold)
for x in [335,359,383]:ln([(x,106),(x,109.5)],blue,.55)
ln([(335,109.5),(383,109.5)],blue,.7)
ar(359,109.5,359,116,blue,.7,2.65);ar(455,106,455,116,gold,.7,2.65)
t(F,123,'All rows',8.6,'b',blue,'center');t(K,123,'First K rows',8.6,'b',gold,'center')
t(F,134,'Drain every group',7.15,'r',gray,'center');t(K,134,'Stop at K or exhaustion',7.15,'r',gray,'center')
fig.savefig(base/'framework.pdf',metadata={'Creator':'Figure source in build.py'});fig.savefig(base/'framework.svg');fig.savefig(base/'framework.png',dpi=220)

# Matplotlib's PDF backend wraps OpenType/CFF as Type 2; normalize the wrapper
# using Cairo. The final result has embedded, selectable Type 1C glyphs.
from subprocess import run
normalized=base/'framework.cairo.pdf'
run(['pdftocairo','-pdf',str(base/'framework.pdf'),str(normalized)],check=True)
normalized.replace(base/'framework.pdf')

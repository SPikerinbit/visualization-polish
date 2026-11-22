import glob,json
from pathlib import Path
base = Path(__file__).resolve().parent
import fitz
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
for key,fn in [('Reg','LiberationSerif-Regular'),('Bold','LiberationSerif-Bold'),('It','LiberationSerif-Italic')]:
 pdfmetrics.registerFont(TTFont(key,glob.glob('/usr/share/fonts/truetype/liberation/'+fn+'.ttf')[0]))
data=json.load(open(base / 'states.json'))
W,H=250,133
p=str(base / 'fig2-run-strips.pdf');c=Canvas(p,pagesize=(W,H))
ink='#33383B'; muted='#50565A'; rail='#80888C'; accent='#915807'; tint='#FFE3AE'; rim='#C7CCCF'; paper='#F8F9F9'; active_ink='#392B1D'
def line(x,y,x2,y2,col=rail,w=.55):
 c.setStrokeColor(HexColor(col));c.setLineWidth(w);c.line(x,H-y,x2,H-y2)
def txt(x,y,t,fs=7,f='Reg',col=ink,center=False):
 c.setFillColor(HexColor(col));c.setFont(f,fs);(c.drawCentredString if center else c.drawString)(x,H-y,t)
def rect(x,y,w,h,fill,edge=None):
 c.setFillColor(HexColor(fill));c.setLineWidth(.42);c.setStrokeColor(HexColor(edge or fill));c.rect(x,H-y-h,w,h,stroke=int(bool(edge)),fill=1)
x0=50;step=12.4;rowh=17.9; gutter=2.6
tops=[2,35,68,101]
def cen(i,n): return x0+(i+.5)*(16/n)*step
def arrow(x,y):
 line(x,y,x-1.1,y-1.7);line(x,y,x+1.1,y-1.7)
def links(src,dst):
 a=tops[src]+rowh;b=tops[dst]-.5;ns=[4,4,2,1][src];nd=[4,4,2,1][dst]
 for i in range(nd):
  x=cen(i,nd)
  xs=[cen(k,ns) for k in range(i*ns//nd,(i+1)*ns//nd)];m=(a+b)/2
  for h in xs:line(h,a,h,m)
  if len(xs)>1:line(xs[0],m,xs[-1],m)
  line(x,m,x,b);arrow(x,b)
for j in range(3):links(j,j+1)
source=set(data['C'][1])
for j,(name,groups,text1,text2) in enumerate([('C',data['C'],'Input','4 chunks'),('R',data['R'],'ListwiseRank','4 calls'),('Q',data['Q'],'Merge pass 1','4 → 2 runs'),('Π',[data['Pi']],'Merge pass 2','2 → 1 run')]):
 t=tops[j];txt(1,t+7.5,text1,7.9,'Bold');txt(1,t+15.2,text2,6.6,col=muted)
 for i,g in enumerate(groups):
  x=x0+len(g)*i*step+.5*gutter;w=len(g)*step-gutter;rect(x,t,w,rowh,paper,rim)
  txt(x+2,t+6.4,name,6.7,'It')
  if name!='Π':txt(x+6.6,t+7.5,str(i+1),4.9)
  for k,v in enumerate(g):
   xp=x+w*(k+.5)/len(g)
   if v in source:
    rect(xp-4.6,t+8.3,9.2,8.7,tint);line(xp-3.8,t+16.8,xp+3.8,t+16.8,col=accent,w=.7)
   txt(xp,t+15.55,str(v),7.8,'Bold' if v in source else 'Reg',active_ink if v in source else ink,True)
rect(x0+1.3,125.1,7.6,5.7,tint)
line(x0+1.3,130.7,x0+8.9,130.7,accent,.75)
txt(x0+12,130.7,'rows from C₂',6.65,col=muted)
c.showPage();c.save()
d=fitz.open(p)
for scale,nam in [(3,'print'),(1.4,'small')]:
 pix=d[0].get_pixmap(matrix=fitz.Matrix(scale,scale));pix.save(str(base / (nam + '.png')))

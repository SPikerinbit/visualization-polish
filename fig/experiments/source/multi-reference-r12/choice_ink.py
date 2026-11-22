"""Change focus ink only; do not move points/labels or regenerate synthetic data."""
from pathlib import Path
import re,sys,json
import fitz
root=Path(sys.argv[1]); out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
for f in sorted(root.glob('p??.pdf')):
 with fitz.open(f) as d:
  pg=d[0]; ids=pg.get_contents()
  assert len(ids)==1
  stream=d.xref_stream(ids[0]).decode('ascii')
  pat=r'0\.48 w (0\.8549019608 0\.5098039216\s+0\.1176470588) RG /DeviceRGB cs\s+(\d[^\n]* m(?:\s+[^\n]* l){4}\s+h)\s+S'
  m=list(re.finditer(pat,stream));assert len(m)==1,(f,len(m))
  col,path=m[0].groups()
  # Stroke the diamond's exact path twice: a narrow knockout, then the
  # saturated hairline. Both are stroke only, so hollow center survives.
  s,n=re.subn(pat,lambda m:f'1.80 w 1 G\n{path}\nS\n0.84 w {col} RG\n{path}\nS',stream)
  assert n==1 and len(path.splitlines())>=6
  # Same star anchor: matplotlib's built-in five-point marker has outer
  # radius sqrt(30)/2 here. Expand the symbol, never the sampled location.
  import math
  star=r'0\.3 w 1 G (0\.031372549 0\.4980392157\s+0\.6078431373) rg\s+(\d[^\n]* m(?:\s+[^\n]* l){9}\s+h)\s+B'
  def boost(m):
   col,path=m.groups()
   pts=re.findall(r'([0-9.]+) ([0-9.]+) ([ml])',path)
   assert len(pts)==10
   x=float(pts[0][0]); y=float(pts[0][1])-math.sqrt(30)/2
   scale=1.31
   p='\n'.join(f'{x+(float(a)-x)*scale:.6f} {y+(float(b)-y)*scale:.6f} {op}' for a,b,op in pts)+'\nh'
   return f'0.88 w 1 G {col} rg\n{p}\nS\n{p}\nf'
  s,n=re.subn(star,boost,s);assert n==1,(f,n)
  d.update_stream(ids[0],s.encode('ascii'))
  d.save(out/f.name,garbage=3,deflate=True)

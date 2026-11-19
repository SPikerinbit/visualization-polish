"""Eight independent logical panels. Each contains LIMIT and separate Full axes."""
from pathlib import Path
import json
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import e5

def build(out):
 out.mkdir(parents=True,exist_ok=True);e5._font_setup();rows,meta=e5.load()
 manifest=[]
 width=e5.W_MM/4
 groupw=6.6+28.6+1.55+6.15
 left=(e5.W_MM-(4*groupw+3*1.15))/2
 for col,(dataset,state) in enumerate([('dl20','off'),('dl20','on'),('covid','off'),('covid','on')]):
  for row,metric in enumerate(['cost','quality']):
   fig=e5.draw(rows,meta);keep=fig.axes[col*4+row*2:col*4+row*2+2]
   for ax in list(fig.axes):
    if ax not in keep:ax.remove()
   for leg in list(fig.legends):leg.remove()
   # Keep only this panel's column title / x description.
   for i,t in enumerate(list(fig.texts)):
    if i != 2*col+row:t.remove()
   lo,hi=(49.75,86.25) if row==0 else (8.5,50.5)
   x0=left+col*(groupw+1.15)-1.1
   for a in list(fig.artists):
    xx=sum(a.get_xdata())/2*e5.W_MM; yy=sum(a.get_ydata())/2*e5.H_MM
    if not(x0<xx<x0+width and lo<yy<hi):a.remove()
   bounds=Bbox.from_extents(x0/25.4,lo/25.4,(x0+width)/25.4,hi/25.4)
   name=f'e5-{dataset}-{state}-{metric}'
   points=[]
   fig.canvas.draw()
   for axis in keep:
    for line in axis.lines:
     for xy in line.get_xydata():
      px,py=axis.transData.transform(xy)/fig.dpi*72
      x=px-bounds.x0*72;y=bounds.y1*72-py
      assert 0<x<bounds.width*72 and 0<y<bounds.height*72
      points.append(dict(xy=xy.tolist(),pdf_xy=[x,y],full=len(line.get_xdata())==1))
   assert len(points)==20 and sum(p['full'] for p in points)==2
   manifest.append(dict(file=name+'.pdf',axes=2,points=points,dataset=dataset,state=state,metric=metric))
   for ext in ['pdf','svg','png']:fig.savefig(out/f'{name}.{ext}',bbox_inches=bounds,pad_inches=0,dpi=300)
   plt.close(fig)
 (out/'e5-panel-manifest.json').write_text(json.dumps(manifest,indent=2))
 fig=plt.figure(figsize=(e5.pt_to_in(e5.TEXT_PT),6/25.4))
 fig.legend(**e5.legend_keys(),loc='center',ncol=3,frameon=False,fontsize=7,handlelength=2.2)
 for ext in ['pdf','svg','png']:fig.savefig(out/f'e5-legend.{ext}',dpi=300)
 plt.close(fig)
if __name__=='__main__':build(Path(__file__).parent/'figures/e5')

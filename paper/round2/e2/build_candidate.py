"""Style-only twelve-panel E2 candidate. Frozen synthetic values, no interpolation."""
from pathlib import Path
import json,csv,hashlib
import plot_surfaces as b
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import proj3d
HERE=Path(__file__).resolve().parent
ROOT=HERE/"out"
(ROOT/"panels").mkdir(parents=True,exist_ok=True)
b._apply_font();original_sizes=b._sizes
# Points more visible than original 1.7 pt² without using a large opaque point wall.
def sizes(layout):
 d=original_sizes(layout);d.update(tick=10.5,label=10.5,diamond=40,star=30,face_b=.13,face_o=.045,edge_ca=.28,edge_co=.48,edge_b=.22,edge_o=.27,pt_s=5.,pt_lw_b=.18,pt_lw_o=.24,pt_a=1.,grid_lw=.23);return d
b._sizes=sizes
reports=[];rows=[]
for spec in b.SPECS_12:
 s=b.build_series(spec);frozen=[(r.k,r.h,r.u,r.p) for r in s.rows];tri=s.tri.copy()
 fig=plt.figure(figsize=(b.PANEL_IN,b.PANEL_IN),facecolor='white');ax=fig.add_axes([.06,.11,.74,.85],projection='3d',computed_zorder=False)
 b.draw_series(ax,s,'panel',b._frames([s])[0],dict(x_ticks=True,x_label=True,y_ticks=True,y_label=True,z_ticks=True,z_label=False));fig.canvas.draw()
 # Axis-attached unit name; cost values remain in thousands, as the caption states.
 # Place just above the actual top z-tick ink with a fixed 4.5bp gap in native panel.
 renderer=fig.canvas.get_renderer()
 boxes=[t.get_window_extent(renderer) for t in ax.get_zticklabels() if t.get_visible() and t.get_text()]
 right=min(max(bb.x1 for bb in boxes),fig.bbox.width-1.5*fig.dpi/72)
 top=max(max(bb.y1 for bb in boxes),ax.zaxis.line.get_window_extent(renderer).y1)+4.5*fig.dpi/72
 fig.text(right/fig.bbox.width,top/fig.bbox.height,'Tokens',ha='right',va='bottom',fontsize=8.5,color=b.INK)
 points=np.array([(r.k,r.h,z) for r in s.rows for z in [r.u,r.p]])
 x,y,z=proj3d.proj_transform(*points.T,ax.get_proj());xy=ax.transData.transform(np.column_stack([x,y]))*72/fig.dpi*(79.28136488/133.2)
 dist=np.linalg.norm(xy[:,None,:]-xy[None,:,:],axis=2);np.fill_diagonal(dist,np.inf);diameter=(5**.5+.24)*79.28136488/133.2
 for ext in ['pdf','svg','png']:fig.savefig(ROOT/'panels'/f'{spec["id"]}.{ext}',dpi=240)
 plt.close(fig)
 assert frozen==[(r.k,r.h,r.u,r.p) for r in s.rows] and (tri==s.tri).all()
 # Independently rebuild baseline rows rather than only comparing rendered Series to itself.
 baseline=b.build_series(dict(spec));assert frozen==[(r.k,r.h,r.u,r.p) for r in baseline.rows]
 reports.append(dict(id=spec['id'],configurations=len(frozen),all_values_equal=True,topology_equal=True,camera=b.CAMERA,projected_potential_overlap=int((dist.min(axis=1)<diameter).sum()),ordinary_markers=len(points),pred_selected=[s.selected.k,s.selected.h,s.selected.u],actual_min=[s.best.k,s.best.h,s.best.u]))
 rows += [[spec['id'],*r] for r in frozen]
with (ROOT/'unchanged-points.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['panel','k','h','synthetic_actual','synthetic_predicted']);w.writerows(rows)
(ROOT/'validation.json').write_text(json.dumps(dict(synthetic=True,panels=reports,all_data_unchanged=True,marker_diameter_print_pt=diameter,baseline_source_sha256=hashlib.sha256((HERE/'plot_surfaces.py').read_bytes()).hexdigest()),indent=2))
# --panels-only preserves the already-reviewed independent legend byte-for-byte.
import sys
if "--panels-only" in sys.argv: raise SystemExit(0)
# One row, shared legend. Synthetic disclosure belongs to manuscript opening.
from matplotlib.lines import Line2D
fig=plt.figure(figsize=(5.6,.23),facecolor='white')
h=[Line2D([],[],marker='o',color=b.BLUE,lw=.5,ms=3,label='Observed cost'),Line2D([],[],marker='o',color=b.ORANGE,lw=.5,mfc='white',ms=3,label='Predicted cost'),Line2D([],[],marker='*',color=b.BLUE,lw=0,ms=5,label='Minimum'),Line2D([],[],marker='D',color=b.ORANGE,lw=0,mfc='none',ms=4,label='Model-selected')]
fig.legend(handles=h,loc='center',ncol=4,fontsize=8.5,frameon=False,handletextpad=.45,columnspacing=1.4)
for ext in ['pdf','svg','png']:fig.savefig(ROOT/f'e2-legend.{ext}',dpi=240)
plt.close(fig)

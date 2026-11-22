#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
from collections import Counter
from decimal import Decimal
from itertools import combinations
import numpy as np
from scipy.spatial import Delaunay
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection,Line3DCollection

D=Path(__file__).resolve().parent
P=D/'patch/fig/experiments/figures/e4b-e2-style'
P.mkdir(parents=True,exist_ok=True)
SRC=D/'existing-e4b-fixture.json'
W,H=240.24655,181.
BETAS=[('0','#0E648D'),('0.25','#287F66'),('0.5','#775BA2'),('0.75','#B7660D'),('1','#9C3E63')]
KEYS=[(2,1),(2,2),(4,1),(4,2),(4,3),(8,1),(8,2)]
CAMERA={'elev':26,'azim':-54}
ASPECT=(1.68,1.,.78)
ZOOM=1.42
INK='#20303D'; TICK='#516370'
mpl.rcParams.update({'font.family':'Liberation Serif','pdf.fonttype':42,'ps.fonttype':42,
                     'font.size':6.25,'path.simplify':False,'savefig.facecolor':'white'})
def frame(ax):
    ax.set_xlim(1.70,8.32);ax.set_ylim(.83,3.17);ax.set_zlim(50,180)
    ax.set_xticks((2,4,6,8));ax.set_yticks((1,2,3));ax.set_zticks((60,80,100,120,140,160,180))
    ax.view_init(**CAMERA)
    ax.set_proj_type('ortho');ax.set_box_aspect(ASPECT,zoom=ZOOM)
    for axis in (ax.xaxis,ax.yaxis,ax.zaxis):
        axis.pane.fill=False
        axis.pane.set_edgecolor('#E8EDF0')
        axis._axinfo['grid']['color']='#E6EAED'
        axis._axinfo['grid']['linewidth']=.22
        axis.line.set_color('#A8B4BC')
        axis.line.set_linewidth(.52)
        axis._axinfo['tick']['inward_factor']=.10
        axis._axinfo['tick']['outward_factor']=.14
        axis._axinfo['tick']['linewidth']={True:.38,False:.28}
    ax.tick_params(axis='x',labelsize=6.1,pad=-.1,colors=TICK)
    ax.tick_params(axis='y',labelsize=6.1,pad=-.1,colors=TICK)
    ax.tick_params(axis='z',labelsize=6.1,pad=.45,colors=TICK)
def labels(fig,ax):
    # Manual offsets in physical bp avoid mplot3d's unstable 2D text extents.
    fig.text(93/W,6.2/H,'k',ha='center',va='bottom',color=INK,fontsize=6.7,fontstyle='italic')
    fig.text(199/W,11/H,'h',ha='center',va='bottom',color=INK,fontsize=6.7,fontstyle='italic')
    fig.text(236/W,139/H,'Equivalent input tokens',ha='right',va='bottom',color=INK,fontsize=7.0)
def legend():
    f=plt.figure(figsize=(W/72,15.4/72),facecolor='white')
    a=f.add_axes([0,0,1,1]);a.set_axis_off()
    # Two independent channels in one line. Whitespace, not boxes, separates
    # parameter colors from the two decision markers. Manual bp positions
    # lock the complete legend inside its original MediaBox.
    def label(x,t,weight='normal'):
        f.text(x/W,.50,t,ha='left',va='center',fontsize=6.6,color=INK,fontweight=weight)
    label(1.8,'β:','bold')
    for x,(b,c) in zip((14,33,59.4,82.4,109),BETAS):
        f.add_artist(Line2D([(x-3.6)/W,(x+3.6)/W],[.5,.5],transform=f.transFigure,lw=.8,color=c))
        f.add_artist(Line2D([x/W],[.5],transform=f.transFigure,linestyle='none',marker='o',markersize=2.85,color=c))
        label(x+5.3,b)
    for x,mark,txt in [(137,'*','Reference min.'),(195,'D','Model pick')]:
        f.add_artist(Line2D([x/W],[.5],transform=f.transFigure,linestyle='none',marker=mark,markersize=5.3 if mark=='*' else 4.2,markeredgewidth=.67,markeredgecolor=INK,markerfacecolor=INK if mark=='*' else 'none'))
        label(x+5,txt)
    f.savefig(P/'e4b-legend.pdf');plt.close(f)
def main():
    raw=SRC.read_bytes();src=json.loads(raw)
    assert src['status']=='synthetic_layout_sample'
    rows=src['configs'];assert [(p['k'],p['h']) for p in rows]==KEYS
    xy=np.array(KEYS,float); tri=Delaunay((xy-xy.min(0))/np.ptp(xy,axis=0)).simplices
    hits=Counter(tuple(sorted((int(a),int(b)))) for t in tri for a,b in combinations(t,2))
    hull=[e for e,n in hits.items() if n==1]; interior=[e for e,n in hits.items() if n==2]
    assert len(set(tri.flatten()))==7
    f=plt.figure(figsize=(W/72,H/72),facecolor='white')
    ax=f.add_axes([-.055,20/H,1,148.24/H],projection='3d',computed_zorder=False)
    frame(ax)
    layers=[];faces=[];fills=[];optima=[]
    for beta,c in BETAS:
        b=Decimal(beta)
        vals=[float(Decimal(p['U'])-(1-b)*Decimal(p['Q'])) for p in rows]
        check=src['expected_measured'][str(b.normalize())]
        assert (check['k'],check['h']) in [KEYS[i] for i,v in enumerate(vals) if v==min(vals)]
        opts=[KEYS[i] for i,v in enumerate(vals) if v==min(vals)]
        assert len(opts)==1
        prediction=src['predicted'][beta]
        pick=(prediction['k'],prediction['h'])
        assert pick in KEYS
        optima.append({'beta':beta,'color':c,'kh':opts[0],'cost':min(vals),'model_choice_kh':pick,'cost_at_model_choice':vals[KEYS.index(pick)]})
        xyz=np.column_stack((xy,vals));layers.append((beta,c,xyz))
        for t in tri:
            faces.append(xyz[t]); fills.append(to_rgba(c,.026))
    ax.add_collection3d(Poly3DCollection(faces,facecolors=fills,edgecolors='none',zsort='average',shade=False,zorder=2))
    for _,c,x in layers:
        ax.add_collection3d(Line3DCollection([x[list(e)] for e in hull],colors=[to_rgba(c,.89)],linewidths=.66,zorder=3))
        ax.add_collection3d(Line3DCollection([x[list(e)] for e in interior],colors=[to_rgba(c,.25)],linewidths=.24,zorder=3))
    for artist in ax.collections:
        artist.set_clip_on(False)  # data stays inside figure, but extends beyond square axes patch
    labels(f,ax)
    f.canvas.draw()
    # Both roles are evaluated on the same repriced surface.
    for (_,c,xyz),row in zip(layers,optima):
        i=KEYS.index(tuple(row['kh'])); j=KEYS.index(tuple(row['model_choice_kh']))
        assert xyz[i,2]==row['cost'] and xyz[j,2]==row['cost_at_model_choice']
        others=np.delete(xyz,sorted({i,j}),axis=0)
        ax.scatter(*others.T,marker='o',s=5.4,c=c,edgecolors='white',linewidths=.25,depthshade=False,zorder=5,clip_on=False)
        xx,yy,_=proj3d.proj_transform(*xyz.T,ax.get_proj())
        xy_fig=f.transFigure.inverted().transform(ax.transData.transform(np.column_stack((xx,yy))))
        for idx, form, size, role in [(j,'D',6.2 if i==j else 5.4,'pick'),(i,'*',5.15,'min')]:
            px,py=xy_fig[idx]
            if role=='pick':
                f.add_artist(Line2D([px],[py],marker=form,linestyle='none',transform=f.transFigure,
                     markersize=size,markerfacecolor='none',markeredgecolor='white',markeredgewidth=1.7,zorder=10))
            f.add_artist(Line2D([px],[py],marker=form,linestyle='none',transform=f.transFigure,
                 markersize=size,markerfacecolor=c if role=='min' else 'none',
                 markeredgecolor='white' if role=='min' else c,markeredgewidth=.67 if role=='min' else .83,zorder=12 if role=='min' else 11))
    if not __import__('os').environ.get('E4B_NO_ANNOTATIONS'):
        # One beta / decision key; no colored labels repeated above the plot.
        for x, txt in [(158,'β'),(179,'Min.'),(209,'Pick')]:
            f.text(x/W,(H-48.5)/H,txt,fontsize=6.9,ha='center',va='center',color=INK,fontweight='semibold',zorder=14)
        for x,mark in [(169,"*"),(198,"D")]:
            f.add_artist(Line2D([x/W],[(H-48.5)/H],transform=f.transFigure,marker=mark,linestyle="none",markersize=4.1,markeredgewidth=.57,markeredgecolor=INK,markerfacecolor=INK if mark=="*" else "none",zorder=14))
        for i,row in enumerate(optima):
            y=(H-57.5-i*7.7)/H
            c=row['color']; q=row['kh']; m=row['model_choice_kh']
            f.add_artist(Line2D([140/W,146/W],[y,y],transform=f.transFigure,lw=1.1,color=c,zorder=13))
            f.text(164/W,y,row['beta'],fontsize=6.65,ha='right',va='center',color=INK,zorder=14)
            for x,key in [(178,q),(207,m)]:
                f.text(x/W,y,f"({key[0]},{key[1]})",fontsize=6.7,ha='center',va='center',color=INK,zorder=14)
    qa=[];f.canvas.draw()
    for beta,_,xyz in layers:
        xx,yy,_=proj3d.proj_transform(*xyz.T,ax.get_proj())
        coords=ax.transData.transform(np.column_stack((xx,yy)))*72/f.dpi
        assert np.all((coords[:,0]>0)&(coords[:,0]<W)&(coords[:,1]>0)&(coords[:,1]<H))
        i=KEYS.index(tuple(next(r['kh'] for r in optima if r['beta']==beta)))
        row=next(r for r in optima if r['beta']==beta)
        row['projection_xy_bp']=coords[i].tolist()
        row['model_choice_projection_xy_bp']=coords[KEYS.index(tuple(row['model_choice_kh']))].tolist()
        qa.append({'beta':beta,'vertex_rows':xyz.tolist(),'projection_xy_bp':coords.tolist()})
    assert sum(len(x['vertex_rows']) for x in qa)==35
    f.savefig(P/'e4b-panel.pdf')
    f.savefig(D/'E4b-panel.png',dpi=300)
    plt.close(f)
    audit={'status':src['status'],'formula':'U-(1-beta)*Q','source_sha256':hashlib.sha256(raw).hexdigest(),
           'projection':'orthographic','camera':CAMERA,'box_aspect':ASPECT,'grid':'#E6EAED',
           'optima_of_seven_sampled_fixture_keys':optima,'new_sorts':0,'sampled_keys':KEYS,'triangles':tri.tolist(),'vertices_total':35,'surface_layers':qa}
    (D/'e4b-3d-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
if __name__=='__main__': main()

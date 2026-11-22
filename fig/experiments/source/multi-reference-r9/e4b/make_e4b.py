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
    fig.text(236/W,137/H,'Tokens',ha='right',va='bottom',color=INK,fontsize=6.65)
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
            faces.append(xyz[t]); fills.append(to_rgba(c,.064))
    ax.add_collection3d(Poly3DCollection(faces,facecolors=fills,edgecolors='none',zsort='average',shade=False,zorder=2))
    for _,c,x in layers:
        ax.add_collection3d(Line3DCollection([x[list(e)] for e in hull],colors=[to_rgba(c,.89)],linewidths=.66,zorder=3))
        ax.add_collection3d(Line3DCollection([x[list(e)] for e in interior],colors=[to_rgba(c,.25)],linewidths=.24,zorder=3))
    for artist in ax.collections:
        artist.set_clip_on(False)  # data stays inside figure, but extends beyond square axes patch
    labels(f,ax)
    # Both roles are evaluated on the same repriced surface.
    for (_,c,xyz),row in zip(layers,optima):
        i=KEYS.index(tuple(row['kh'])); j=KEYS.index(tuple(row['model_choice_kh']))
        assert xyz[i,2]==row['cost'] and xyz[j,2]==row['cost_at_model_choice']
        others=np.delete(xyz,sorted({i,j}),axis=0)
        ax.scatter(*others.T,marker='o',s=8.2,c=c,edgecolors='white',linewidths=.25,depthshade=False,zorder=5,clip_on=False)
        ax.scatter(*xyz[j],marker='D',s=50 if i==j else 19,facecolors='none',edgecolors=c,
                   linewidths=.78,depthshade=False,zorder=8,clip_on=False)
        ax.scatter(*xyz[i],marker='*',s=31,c=c,edgecolors='white',linewidths=.4,depthshade=False,zorder=9,clip_on=False)
    if not __import__('os').environ.get('E4B_NO_ANNOTATIONS'):
        for i,row in enumerate(optima):
            y=(H-57.3-i*7.1)/H
            c=row['color']; q=row['kh']; m=row['model_choice_kh']
            f.text(162/W,y,row['beta'],fontsize=6.15,ha='right',va='center',color=INK,zorder=11)
            def mark(x,form):
                f.add_artist(Line2D([(x-2)/W],[y],transform=f.transFigure,marker=form,markersize=4.4 if form=='*' else 3.6,
                    linestyle='none',markeredgewidth=.66,markerfacecolor=c if form=='*' else 'none',markeredgecolor=c,zorder=11))
            def coords(x,k):
                f.text((x-2)/W,y,f"({k[0]},{k[1]})",fontsize=6.15,ha='left',va='center',color=INK,zorder=11)
            mark(169,'*')
            if q==m:
                mark(174,'D'); coords(177.5,q)
            else:
                coords(172.5,q); mark(188,'D'); coords(191.5,m)
        f.text(162/W,(H-50.0)/H,'β',fontsize=6.15,ha='right',va='center',color=INK,zorder=11)
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
    plt.close(f);legend()
    audit={'status':src['status'],'formula':'U-(1-beta)*Q','source_sha256':hashlib.sha256(raw).hexdigest(),
           'projection':'orthographic','camera':CAMERA,'box_aspect':ASPECT,'grid':'#E6EAED',
           'optima_of_seven_sampled_fixture_keys':optima,'new_sorts':0,'sampled_keys':KEYS,'triangles':tri.tolist(),'vertices_total':35,'surface_layers':qa}
    (D/'e4b-3d-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
if __name__=='__main__': main()

#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
from itertools import combinations
import hashlib,json
import numpy as np
from scipy.spatial import Delaunay
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection,Line3DCollection

HERE=Path(__file__).resolve().parent
DEST=HERE/'patch/fig/experiments/figures/e3-liu-palette'
SRC=HERE/'existing-layout-fixture.json'
REF='2cfdb2883f65c0b35ad6e04c21787111c600be4ba80d6ef51390adce499d8e3d'
REFSRC='fa11b8dc3b79743c9c912eae30c31630af4e0d166fccec743343bc2cbe33bcf6'
WIDTH,HEIGHT,PAGE=122.8,98,504.4
CAMERA=dict(elev=25,azim=-62); ASPECT=(1.45,.92,1.08); ZOOM=1.26
KEY_ORIGIN={'SW':(49.25,66.25),'LT':(57.75,63.75)}
COLORS={1000:'#326FA3',5000:'#AC710D',10000:'#8057A6'}
INK='#20303D';TICK='#516370';CHOICE='#263C48'
DIAMOND_X,DIAMOND_Y,DIAMOND_LW=2.72,1.36,.48
STAR_R,STAR_LW=1.40,.14
def _motif_star(cx,cy,r):
    ang=np.linspace(np.pi/2,np.pi/2+2*np.pi,10,endpoint=False)
    rad=np.asarray([r,r*.40]*5)
    return np.column_stack((cx+rad*np.cos(ang),cy+rad*np.sin(ang)))
def _motif_diamond(cx,cy,rx,ry):
    return np.array([(cx-rx,cy),(cx,cy+ry),(cx+rx,cy),(cx,cy-ry)])
FROZEN={'SW':[(4,5),(5,4),(10,2),(8,1),(10,1)],
        'LT':[(50,2),(16,4),(32,3),(50,1),(20,1)]}
RANGES={'SW':(4,10),'LT':(16,50)}
TICKS={'SW':(4,6,8,10),'LT':(16,24,32,40,50)}
LIMZ=(10,65)
mpl.rcParams.update({'font.family':'Liberation Serif','pdf.fonttype':42,
    'ps.fonttype':42,'font.size':6.1,'axes.unicode_minus':False,'savefig.facecolor':'white',
    'path.simplify':False})
def _frame(ax,fam):
    x0,x1=RANGES[fam];span=x1-x0
    ax.set_xlim(x0-.045*span,x1+.057*span)
    ax.set_ylim(.82,5.20)
    ax.set_zlim(*LIMZ)
    ax.set_xticks(TICKS[fam])
    ax.set_yticks((1,2,3,4,5))
    ax.set_zticks((20,35,50,65))
    ax.view_init(**CAMERA)
    ax.set_proj_type('ortho')
    ax.set_box_aspect(ASPECT,zoom=ZOOM)
    for axis in (ax.xaxis,ax.yaxis,ax.zaxis):
        axis.pane.fill=False
        axis.pane.set_edgecolor('#E8EDF0')
        axis._axinfo['grid']['color']='#DFE6EA'
        axis._axinfo['grid']['linewidth']=.25
        axis.line.set_color('#A8B4BC')
        axis.line.set_linewidth(.52)
        axis._axinfo['tick']['inward_factor']=.10
        axis._axinfo['tick']['outward_factor']=.14
        axis._axinfo['tick']['linewidth']={True:.38,False:.28}
    ax.tick_params(axis='x',labelsize=5.75,pad=-1.8,colors=TICK)
    ax.tick_params(axis='y',labelsize=5.75,pad=-1.8,colors=TICK)
    ax.tick_params(axis='z',labelsize=5.75,pad=-2.2,colors=TICK)
    ax.set_xlabel('',labelpad=0,color=INK,fontsize=6.35)
    ax.set_ylabel('',labelpad=0,color=INK,fontsize=6.35)
def _labels(fig,ax):
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer(); px=fig.dpi/72
    boxes=[t.get_window_extent(renderer) for t in ax.get_zticklabels() if t.get_visible() and t.get_text()]
    rail=ax.zaxis.line.get_window_extent(renderer)
    tokens=fig.text((rail.x0/px-1.3)/WIDTH,0,'Tokens',ha='left',va='bottom',
        color=INK,fontsize=6.2)
    width=tokens.get_window_extent(renderer).width/px
    xb=min(rail.x0/px-1.3, WIDTH-width-1.9)
    # Real rail top and highest tick set the anchor, not an outboard proxy axis.
    yb=min(max(max(b.y1 for b in boxes),rail.y1)/px+2.0,HEIGHT-8.1)
    tokens.set_position((xb/WIDTH,yb/HEIGHT))
    fig.text(.265,.012,'k',ha='center',va='bottom',color=INK,fontsize=6.35)
    fig.text(.88,.018,'h',ha='center',va='bottom',color=INK,fontsize=6.35)
    return {
      'z_title_box_bp':[v/px for v in tokens.get_window_extent(renderer).extents],
      'z_rail_box_bp':[v/px for v in rail.extents],
      'highest_z_tick_top_bp':max(b.y1 for b in boxes)/px,
    }
def _coordinate_key(fig,markers,family):
    # Separate diagnostic view: one row per n and a single LINEAR token scale.
    # No centering trick, jitter or replacement of the true 3D minima.
    keys = {tuple(int(v) for v in m[q][:2]) for m in markers for q in ('reference_min_xyz','predicted_min_xyz')}
    assert len(keys) == 1
    k,h=next(iter(keys))
    xlo, xhi = (31.25,61.25) if family=='SW' else (64.25,94.25)
    rowtop=(82.25 if family=='SW' else 79.0)
    first=xlo-2.3
    def txt(x,y,v,sz=5.8,hal='center',color=INK):
        return fig.text(x/WIDTH,y/HEIGHT,v,ha=hal,va='center',color=color,fontsize=sz,zorder=16)
    def line(x,y,xx,yy,ink,thick):
        l=Line2D([x/WIDTH,xx/WIDTH],[y/HEIGHT,yy/HEIGHT],transform=fig.transFigure,lw=thick,color=ink,solid_capstyle='butt',zorder=13)
        fig.add_artist(l)
        return l
    header=txt(26.75 if family=='SW' else 39,87.90 if family=='SW' else 84.75,f'Tokens at ({k},{h})',5.95,'left')
    from matplotlib.transforms import Bbox
    xpos=lambda z: xlo+(z-14)/13*(xhi-xlo)
    out=[]
    for j,m in enumerate(markers):
        y=rowtop-j*5.40
        n=m['input_size']; c=COLORS[n]
        z1,z2=[m[key][2] for key in ['reference_min_xyz','predicted_min_xyz']]
        x1,x2=xpos(z1),xpos(z2)
        lab=txt(first,y,f'{n//1000}k',5.8,'right',c)
        ln=line(x1,y,x2,y,c,.44)
        star=Polygon(_motif_star(x1,y,2.0)/[WIDTH,HEIGHT],closed=True,transform=fig.transFigure,facecolor=c,edgecolor='white',linewidth=.17,zorder=15)
        diam=Polygon(_motif_diamond(x2,y,1.78,1.68)/[WIDTH,HEIGHT],closed=True,transform=fig.transFigure,facecolor='white',edgecolor=c,linewidth=.48,zorder=15)
        fig.add_artist(star);fig.add_artist(diam)
        fig.canvas.draw();renderer=fig.canvas.get_renderer();px=fig.dpi/72
        bb=Bbox.union([a.get_window_extent(renderer) for a in [lab,star,diam,ln]]).extents/px
        out.append(dict(n=n,reference_key=[k,h],predicted_key=[k,h],combined=True,
            reference_value=z1,predicted_value=z2,glyph_separation_bp=x2-x1,box_bp=bb.tolist()))
    y=rowtop-13.25
    line(xpos(15),y,xpos(25),y,'#81909B',.30)
    for z in [15,20,25]:
        xx=xpos(z);line(xx,y,xx,y-.8,'#81909B',.34)
        txt(xx,y-2.9,str(z),5.2)
    return out
def _project(fig,ax,xyz):
    xx,yy,_=proj3d.proj_transform(*np.atleast_2d(xyz).T,ax.get_proj())
    return ax.transData.transform(np.column_stack((xx,yy)))*72/fig.dpi
def _sample_markers(fig,ax,meshes):
    out=[]
    by={(n,st):v for n,_,st,v in meshes}
    refs={n:by[n,'measured'][int(np.argmin(by[n,'measured'][:,2]))] for n in COLORS}
    ref_xy=_project(fig,ax,list(refs.values()))
    for n,color in COLORS.items():
        reference=by[n,'measured']; prediction=by[n,'predicted']
        i_ref=int(np.argmin(reference[:,2])); i_pred=int(np.argmin(prediction[:,2]))
        st,dh=reference[i_ref],prediction[i_pred]
        sxy,dxy=_project(fig,ax,[st,dh])
        clearance=float(np.min(np.linalg.norm(ref_xy-dxy,axis=1)))
        # Hollow diamond and star are drawn directly at their exact projected
        # surface locations. Broad, thin diamond wings stay visible to either
        # side of a near-coincident star, without relocating either glyph.
        shape=_motif_diamond(*dxy,DIAMOND_X,DIAMOND_Y)
        fig.add_artist(Polygon(shape/[WIDTH,HEIGHT],closed=True,transform=fig.transFigure,
          facecolor='none',edgecolor=color,linewidth=DIAMOND_LW,joinstyle='round',
          zorder=13,clip_on=False))
        shape=_motif_star(*sxy,STAR_R)
        fig.add_artist(Polygon(shape/[WIDTH,HEIGHT],closed=True,transform=fig.transFigure,
          facecolor=color,edgecolor='white',linewidth=STAR_LW,joinstyle='round',
          zorder=14,clip_on=False))
        out.append(dict(input_size=n,reference_min_sample_index=i_ref,predicted_min_sample_index=i_pred,
          reference_min_xyz=st.tolist(),predicted_min_xyz=dh.tolist(),
          reference_center_bp=sxy.tolist(),predicted_anchor_bp=dxy.tolist(),
          predicted_diamond_center_bp=dxy.tolist(),
          nearest_reference_to_predicted_anchor_bp=clearance,
          diamond_outer_width_bp=2*DIAMOND_X+DIAMOND_LW,
          diamond_outer_height_bp=2*DIAMOND_Y+DIAMOND_LW,star_radius_bp=STAR_R))
    return out
def _panel(p,with_key=True):
    fam,mode=p['family'],p['mode']
    pts=[(g['k'],g['h']) for g in p['series']]
    assert pts==FROZEN[fam]
    coords=np.array(pts,dtype=float)
    plane=(coords-coords.min(0))/np.ptp(coords,axis=0)
    tri=Delaunay(plane).simplices
    assert set(tri.flatten())==set(range(5))
    hits=Counter(tuple(sorted((int(a),int(b)))) for t in tri for a,b in combinations(t,2))
    hull=[k for k,num in hits.items() if num==1]
    interior=[k for k,num in hits.items() if num==2]
    fig=plt.figure(figsize=(WIDTH/72,HEIGHT/72),facecolor='white')
    ax=fig.add_axes([-.05,.146,.97,.825],projection='3d',computed_zorder=False)
    _frame(ax,fam)
    report={'family':fam,'mode':mode,'triangles':tri.tolist(),'hull_edges':hull,'interior_edges':interior,'surfaces':[]}
    meshes=[]; minima=[]
    faces=[]; fills=[]
    for j,(n,color) in enumerate(COLORS.items()):
        for st in ('measured','predicted'):
            z=[g[st][j] for g in p['series']]
            x=np.column_stack((coords,z))
            meshes.append((n,color,st,x))
            ids=np.flatnonzero(np.asarray(z)==min(z))
            minima.append({'input_size':n,'style':st,'keys':[list(pts[i]) for i in ids],
                           'fixture_min_value':min(z)})
            for t in tri:
                faces.append(x[t])
                fills.append(to_rgba(color,.045 if st=='measured' else .014))
    coll=Poly3DCollection(faces,facecolors=fills,edgecolors='none',zsort='average',shade=False,zorder=2)
    ax.add_collection3d(coll)
    for _,color,st,xyz in meshes:
        solid=st=='measured'
        # E2's unfilled panes + quiet surface silhouette. Diagonals are faint
        # so all 24 triangular meshes persist without a sixfold edge tangle.
        line=Line3DCollection([xyz[list(e)] for e in hull],
            colors=[to_rgba(color,.79 if solid else .84)],linewidths=.50 if solid else .42,
            linestyles='solid' if solid else (0,(3.0,2.4)),zorder=3)
        ax.add_collection3d(line)
        line=Line3DCollection([xyz[list(e)] for e in interior],
            colors=[to_rgba(color,.29 if solid else .22)],linewidths=.16,
            linestyles='solid' if solid else (0,(2.3,1.85)),zorder=3)
        ax.add_collection3d(line)
    for _,color,st,xyz in meshes:
        solid=st=='measured'
        # The explicit figure-space symbols replace ordinary dots at minima,
        # without duplicating or visually merging two markers at one vertex.
        # Otherwise every dot keeps the old style/size.
        others=np.arange(len(xyz))!=int(np.argmin(xyz[:,2]))
        ax.scatter(*xyz[others].T,marker='o',s=4.30 if solid else 7.25,
                   color=color if solid else None,facecolors=color if solid else 'none',
                   edgecolors='white' if solid else color,
                   linewidths=.16 if solid else .34,depthshade=False,zorder=5 if solid else 6)
    arbitrary=minima[0]['keys']
    assert len(arbitrary)==1 and all(e['keys']==arbitrary for e in minima)
    report['sampled_minima']=minima
    report['shared_minimum_key']=arbitrary[0]
    report['annotation_geometry']=_labels(fig,ax)
    report['surface_markers']=_sample_markers(fig,ax,meshes)
    if with_key:
        report['coordinate_key_rows']=_coordinate_key(fig,report['surface_markers'],fam)
    for n,color,st,xyz in meshes:
        xy=_project(fig,ax,xyz)
        report['surfaces'].append({'input_size':n,'style':st,'exact_vertices':xyz.tolist(),
                                   'projection_xy_bp':xy.tolist()})
    return fig,report
def _legend():
    f=plt.figure(figsize=(PAGE/72,17/72),facecolor='white')
    a=f.add_axes([0,0,1,1]);a.set_axis_off()
    handles=[Line2D([],[],color=v,marker='o',markersize=2.9,linewidth=.65,label=f'{n//1000}k rows')
              for n,v in COLORS.items()]
    handles += [Line2D([],[],color='#364651',marker='o',markersize=2.75,lw=.61,label='Reference'),
                Line2D([],[],color='#364651',marker='o',markersize=3.25,lw=.6,
                       dashes=(2.5,1.75),mfc='none',label='Predicted')]
    handles += [Line2D([],[],marker='*',markersize=5.4,mfc='#36515C',mec='white',mew=.25,
                       linestyle='none',label='Reference min.'),
                Line2D([],[],marker='D',markersize=3.8,mfc='none',mec=CHOICE,mew=.57,
                       linestyle='none',label='Predicted min.')]
    a.legend(handles=handles,ncol=7,frameon=False,loc='center',bbox_to_anchor=(.50,.5),
              fontsize=6.3,handlelength=2.00,columnspacing=1.65,handletextpad=.54)
    return f
def main():
    DEST.mkdir(parents=True,exist_ok=True)
    x=json.loads(SRC.read_text())
    assert x['kind']=='synthetic_layout_only' and x['x']['values']==list(COLORS)
    xm={(p['family'],p['mode']):p for p in x['panels']}
    audit={'kind':x['kind'],'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
           'reference_E2_vector_sha256':REF,
           'reference_E2_generator_sha256':REFSRC,
           'camera':CAMERA,'box_aspect':ASPECT,'zoom':ZOOM,
           'projection':'orthographic, continuous k/h/z within each panel, all n/status positions unchanged',
           'styles':'E2-like transparent panes, light grid, small circular filled/hollow points; lower camera and taller z aspect; face alpha .045/.014',
           'minimum_annotation':'Three exact reference minimum anchors and three exact predicted minimum anchors per panel. Stars and open diamonds lie directly on their respective reference and predicted vertices. No leaders, displaced symbols, or changes to plotted vertices or geometry. A calibrated inset separates the three input sizes; each metric is recomputed directly from the sampled vertex at its minimum.',
           'panels':[]}
    for fam in ('SW','LT'):
        for mode in ('Full','LIMIT10'):
            f,r=_panel(xm[fam,mode])
            stem=f'{fam.lower()}-{mode.lower()}'
            f.savefig(DEST/(stem+'.pdf'))
            f.savefig(HERE/(stem+'.png'),dpi=288)
            plt.close(f)
            audit['panels'].append(r)
    f=_legend();f.savefig(DEST/'legend.pdf');plt.close(f)
    assert sum(len(s['exact_vertices']) for p in audit['panels'] for s in p['surfaces'])==120
    assert all(len(p['surfaces'])==6 for p in audit['panels'])
    (HERE/'e3-3d-qa.json').write_text(json.dumps(audit,indent=2)+'\n')
if __name__=='__main__':
    main()

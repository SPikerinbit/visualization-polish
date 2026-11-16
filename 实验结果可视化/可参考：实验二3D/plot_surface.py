"""Two scientific surfaces on identical axes; no fitted heights or visual z offset."""
from pathlib import Path
import json, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d
from scipy.stats import spearmanr
import plotly.graph_objects as go

ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'surface_data.json').read_text())
pts=data['points'];x=np.array([r['k'] for r in pts]);y=np.array([r['h'] for r in pts])
u=np.array([r['U'] for r in pts]);p=np.array([r['P'] for r in pts]);z1=u/1000;z2=p/1000
idx={(r['k'],r['h']):i for i,r in enumerate(pts)}
tri=[]
for k in range(2,10):
    for h in range(1,10):
        sq=[(k,h),(k+1,h),(k+1,h+1),(k,h+1)]
        present=[q for q in sq if q in idx]
        if len(present)<3:continue
        ii=[idx[q] for q in present];tri.append(ii[:3])
        if len(ii)==4:tri.append([ii[0],ii[2],ii[3]])
tri=np.asarray(tri);assert len(tri)>0
triangle_edges={tuple(sorted((int(t[a]),int(t[b])))) for t in tri for a,b in [(0,1),(1,2),(2,0)]}
grid_edges={tuple(sorted((i,idx[q]))) for (k,h),i in idx.items() for q in [(k+1,h),(k,h+1)] if q in idx}
best=min(pts,key=lambda r:r['U']);sel=min(pts,key=lambda r:r['P'])
metrics=dict(spearman=float(spearmanr(u,p).statistic),mape=float(np.mean(abs(p/u-1))),mean_signed_error=float(np.mean(p/u-1)),regret=sel['U']/best['U']-1,minimum=best,selected=sel)
(ROOT/'metrics.json').write_text(json.dumps(metrics,indent=2))
BLUE='#087F9B';ORANGE='#DA821E';INK='#20303D';GRAY='#657581'
plt.rcParams.update({'font.family':'Arial','font.size':13,'axes.labelsize':16,'xtick.labelsize':12,'ytick.labelsize':12,'pdf.fonttype':42,'svg.fonttype':'none'})
fig=plt.figure(figsize=(13.6,8.7),facecolor='white')
ax=fig.add_axes([-.025,.075,.85,.78],projection='3d',computed_zorder=False)
# Interleave all triangles in one collection so transparent faces from both
# surfaces are depth-sorted together, instead of sorting two whole surfaces.
faces=[];colors=[];edges=[];widths=[]
for z,col,alpha,ew in [(z1,BLUE,.55,.55),(z2,ORANGE,.22,.80)]:
    xyz=np.c_[x,y,z]
    for t in tri:
        faces.append(xyz[t]);colors.append(to_rgba(col,alpha));edges.append(to_rgba(col,.64 if col==BLUE else .86));widths.append(ew)
poly=Poly3DCollection(faces,facecolors=colors,edgecolors=edges,linewidths=widths,zsort='average',antialiased=True)
ax.add_collection3d(poly)
for a,b in sorted(grid_edges-triangle_edges):
    for z,c in [(z1,BLUE),(z2,ORANGE)]:
        ax.plot(x[[a,b]],y[[a,b]],z[[a,b]],color=c,linewidth=.9,alpha=.8,zorder=2)
ax.scatter(x,y,z1,s=12,c=BLUE,edgecolors='white',linewidths=.25,alpha=.85,depthshade=False,zorder=3)
ax.scatter(x,y,z2,s=12,facecolors='none',edgecolors=ORANGE,linewidths=.65,alpha=.85,depthshade=False,zorder=4)
ax.scatter([best['k']],[best['h']],[best['U']/1000],s=175,marker='*',color=BLUE,edgecolor='white',linewidths=.9,depthshade=False,zorder=8)
ax.scatter([sel['k']],[sel['h']],[sel['P']/1000],s=85,marker='D',color=ORANGE,edgecolor='white',linewidths=.9,depthshade=False,zorder=9)
if (best['k'],best['h'])==(sel['k'],sel['h']):
    ax.plot([best['k']]*2,[best['h']]*2,[best['U']/1000,sel['P']/1000],color=INK,linewidth=1.4,zorder=7)
ax.set(xlim=(1.7,10.35),ylim=(.65,10.25),zlim=(75,375),xticks=[2,4,6,8,10],yticks=[1,3,5,7,10],zticks=[100,150,200,250,300,350])
ax.set_xlabel('Fan-in $k$',labelpad=12,color=INK);ax.set_ylabel('Segment length $h$',labelpad=13,color=INK)
ax.set_zlabel('Merge input tokens (1k)',labelpad=13,color=INK)
ax.view_init(elev=26,azim=-54);ax.set_proj_type('ortho');ax.set_box_aspect([1.45,1,.92],zoom=1.04)
for a in [ax.xaxis,ax.yaxis,ax.zaxis]:
    a.pane.fill=False;a.pane.set_edgecolor('#E8EDF0');a._axinfo['grid']['color']='#DFE6EA';a._axinfo['grid']['linewidth']=.6
    a.line.set_color('#A8B4BC')
ax.tick_params(pad=2,colors='#516370')
fig.text(.055,.945,'Full LT: predicted and measured token surfaces',fontsize=22,color=INK,weight='bold')
fig.text(.055,.903,'n = 200     m = 20     query 1030303     contiguous input     MC = 16,384',fontsize=13,color=GRAY)
handles=[Line2D([0],[0],color=BLUE,linewidth=6,alpha=.65,marker='o',markersize=5,label='Measured vLLM cost'),Line2D([0],[0],color=ORANGE,linewidth=3,alpha=.85,marker='o',markerfacecolor='white',markersize=5,label='Cost Model prediction')]
fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.052,.87),frameon=False,ncol=2,columnspacing=2.0,handlelength=2.3,fontsize=13)
same=(best['k'],best['h'])==(sel['k'],sel['h'])
fig.text(.793,.665,'SAME MINIMUM' if same else 'MINIMUM CONFIGURATIONS',fontsize=12,weight='bold',color=GRAY)
fig.text(.793,.612,f"(k, h) = ({best['k']}, {best['h']})",fontsize=23,color=INK)
fig.text(.793,.53,'Measured',fontsize=13,color=BLUE)
fig.text(.793,.485,f"{best['U']:,.0f}",fontsize=27,color=BLUE,weight='bold')
fig.text(.793,.415,'Predicted',fontsize=13,color=ORANGE)
fig.text(.793,.37,f"{sel['P']:,.0f}",fontsize=27,color=ORANGE,weight='bold')
fig.text(.793,.31,f"Prediction gap: {100*(sel['P']/sel['U']-1):+.2f}%",fontsize=12,color=GRAY)
fig.text(.793,.257,'Both heights stay on\nthe original token scale.',fontsize=12,color=GRAY,linespacing=1.6)
fig.text(.055,.061,'50 complete measured configurations. The two surfaces use the same adjacent-grid triangles.',fontsize=11,color=GRAY)
fig.text(.055,.032,'Measured: first qualified vLLM run per configuration. Prediction: current production MC, including initialization and tail.',fontsize=10.5,color=GRAY)
for ext in ['png','pdf','svg']:fig.savefig(ROOT/f'full_lt_predicted_vs_measured.{ext}',dpi=250,facecolor='white')
plt.close(fig)

# Standalone WebGL companion: rotate, zoom, hover exact values and toggle layers.
f=go.Figure()
for z,c,op,name in [(z1,BLUE,.67,'Measured vLLM'),(z2,ORANGE,.27,'Cost Model (MC 16,384)')]:
    f.add_trace(go.Mesh3d(x=x,y=y,z=z,i=tri[:,0],j=tri[:,1],k=tri[:,2],color=c,opacity=op,name=name,showlegend=True,flatshading=True,lighting=dict(ambient=.85,diffuse=.35,specular=.05),hovertemplate='k=%{x}, h=%{y}<br>Input tokens: %{z:.3f}k<extra>'+name+'</extra>',legendgroup=name))
    xx=[];yy=[];zz=[]
    # Draw shared surface edges only once.
    edgeset=triangle_edges | grid_edges
    for a,b in edgeset:xx.extend([int(x[a]),int(x[b]),None]);yy.extend([int(y[a]),int(y[b]),None]);zz.extend([float(z[a]),float(z[b]),None])
    f.add_trace(go.Scatter3d(x=xx,y=yy,z=zz,mode='lines',line=dict(color=c,width=2),hoverinfo='skip',showlegend=False,legendgroup=name))
    f.add_trace(go.Scatter3d(x=x,y=y,z=z,mode='markers',marker=dict(size=2.5,color=c),customdata=np.c_[u,p],hovertemplate='k=%{x}, h=%{y}<br>Measured: %{customdata[0]:,.0f}<br>Predicted: %{customdata[1]:,.0f}<extra></extra>',showlegend=False,legendgroup=name))
for r,col,field,name,symbol in [(best,BLUE,'U','Measured minimum','circle'),(sel,ORANGE,'P','Predicted minimum','diamond')]:
    f.add_trace(go.Scatter3d(x=[r['k']],y=[r['h']],z=[r[field]/1000],mode='markers',marker=dict(size=7,color=col,symbol=symbol,line=dict(color='white',width=2)),name=name,hovertemplate=f"{name}: ({r['k']}, {r['h']})<br>{r[field]:,.0f} tokens<extra></extra>"))
f.update_layout(title=dict(text='Full LT: predicted and measured token surfaces<br><sup>n=200 · m=20 · 50 configurations · MC=16,384 · same token scale</sup>',x=.05),template='plotly_white',font=dict(family='Arial',size=15,color=INK),margin=dict(l=20,r=20,b=30,t=110),height=820,legend=dict(orientation='h',y=1.03,x=.04),scene=dict(xaxis_title='Fan-in k',yaxis_title='Segment length h',zaxis_title='Merge input tokens (1k)',aspectmode='manual',aspectratio=dict(x=1.45,y=1,z=.92),camera=dict(eye=dict(x=1.5,y=-1.85,z=1.15),projection=dict(type='orthographic'))))
f.write_html(ROOT/'full_lt_predicted_vs_measured.html',include_plotlyjs=True,config=dict(displaylogo=False,toImageButtonOptions=dict(format='png',filename='full_lt_dual_surface',scale=3)))
print(json.dumps({k:v for k,v in metrics.items() if k not in ['minimum','selected']},indent=2))

from pathlib import Path
import json
P=Path(__file__).parent
C=[[12,3,16,7],[5,14,1,6],[11,2,15,8],[9,13,4,10]];R=[sorted(c) for c in C];Q=[sorted(R[0]+R[1]),sorted(R[2]+R[3])]
for variant,H,cy,ly,ry,my,qy,fy,py in [('A',83,76,66,54,42,32,20,10),('B',70,63,55,43,33,23,14,6.5)]:
 s=[r'''\documentclass{article}\usepackage[paperwidth=84.75365mm,paperheight=HEIGHTmm,margin=0pt]{geometry}
\usepackage{tikz}\usepackage{amsmath}\usetikzlibrary{arrows.meta}
\pagestyle{empty}\setlength{\parindent}{0pt}
\definecolor{warm}{HTML}{FDE7CE}\definecolor{edge}{HTML}{E07B00}\definecolor{ink}{HTML}{333333}
\begin{document}\noindent\begin{tikzpicture}[x=1mm,y=1mm,every node/.style={inner sep=0pt,outer sep=0pt,text=ink,font=\fontsize{8}{9}\selectfont},
 item/.style={circle,draw=ink,fill=white,line width=.45pt,minimum size=3.8mm},
 call/.style={rounded corners=.65mm,draw=edge,fill=warm,line width=.65pt,minimum width=18.6mm,minimum height=5mm,font=\fontsize{8}{9}\selectfont},
 merge/.style={call,fill=white,dashed,minimum width=22mm},
 group/.style={rounded corners=.7mm,draw=ink,dashed,line width=.45pt},
 arr/.style={-{Stealth[length=1.1mm]},line width=.55pt,draw=ink}]
\useasboundingbox (0,0) rectangle (84.75365,HEIGHT);
'''.replace('HEIGHT',str(H))]
 def items(v,c,y,name,step=4.4):
  x=c-(len(v)-1)*step/2
  for j,n in enumerate(v):s.append(fr'\node[item] ({name}{j}) at ({x+j*step},{y}) {{{n}}};')
 for i,x in enumerate([11.5,32,52.5,73]):
  s.append(fr'\node at ({x},{cy+5}) {{$C_{i+1}$}};');items(C[i],x,cy,f'C{i}')
  s.append(fr'\draw[dotted,line width=.5pt] ({x-9.3},{cy-2.7}) rectangle ({x+9.3},{cy+2.7});')
  s.append(fr'\node[call] (call{i}) at ({x},{ly}) {{ListwiseRank}};\draw[arr] ({x},{cy-2.7}) -- (call{i}.north);')
  s.append(fr'\node at ({x},{ry+4}) {{$R_{i+1}$}};');items(R[i],x,ry,f'R{i}')
  s.append(fr'\draw[arr] (call{i}.south) -- ({x},{ry+6});')
 for i,x in enumerate([21.75,62.75]):
  s.append(fr'\draw[group] ({x-19.3},{ry-2.8}) rectangle ({x+19.3},{ry+5.8});')
  s.append(fr'\node[merge] (m{i}) at ({x},{my}) {{MergeGroup}};\draw[arr] ({x},{ry-2.8}) -- (m{i}.north);')
  s.append(fr'\node at ({x},{qy+4}) {{$Q_{i+1}$}};');items(Q[i],x,qy,f'Q{i}')
  s.append(fr'\draw[arr] (m{i}.south) -- ({x},{qy+6.5});')
 s.append(fr'\node[text=black!55] at (42.25,{my}) {{Pass 1}};\node[text=black!55,anchor=east] at (29,{fy}) {{Pass 2}};')
 s.append(fr'\draw[group] (3,{qy-2.8}) rectangle (81.5,{qy+6.5});\node[merge] (final) at (42.25,{fy}) {{MergeGroup}};\draw[arr] (42.25,{qy-2.8}) -- (final.north);')
 items(list(range(1,17)),46,py,'P',4.4)
 s.append(fr'\node at (5,{py}) {{$\Pi=$}};\draw[line width=.45pt] (10.8,{py+2.6}) -- (10.8,{py+3}) -- (81.2,{py+3}) -- (81.2,{py+2.6});\draw[arr] (final.south) -- (42.25,{py+3});')
 # legend: the two source border styles, one row
 s.append(r'\node[anchor=south west,inner sep=0pt,outer sep=0pt] at (0,0) {\includegraphics[width=240.2465515bp]{alg1-legend.pdf}};')
 s.append(r'\end{tikzpicture}\end{document}');(P/f'alg1-{variant}.tex').write_text('\n'.join(s))
(P/'states.json').write_text(json.dumps({'C':C,'R':R,'Q':Q,'Pi':list(range(1,17))},indent=2))

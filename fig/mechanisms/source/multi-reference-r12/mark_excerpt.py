from lxml import etree as E
import sys
svg=E.parse(sys.argv[1]); N='{http://www.w3.org/2000/svg}'
def node(tag,**kw):return E.Element(N+tag,{k.replace('_','-'):str(v) for k,v in kw.items()})
for k in ('build','refresh'):
 p=svg.xpath(f'//*[@id="{k}"]')[0]
 p.insert(1,node('rect',x=82.3,y=28.5,width=33.0,height=56.21,rx=.9,fill='none',
                    stroke='#B78446',stroke_width='.49',stroke_dasharray='1.9 1.35'))
leg=svg.xpath('//*[@id="legend-physical-bp"]')[0]
for e,x in zip(leg,[7.5,45.,83.,204.5]):
 e.set('transform',f'translate({x} 0) scale(0.84)')
key=node('g',transform='translate(139.7 0) scale(0.84)')
key.append(node('rect',x=0,y=1.9,width=8.4,height=6.2,rx=.6,fill='none',
                stroke='#B78446',stroke_width='.58',stroke_dasharray='2.2 1.6'))
t=node('text',x=12.3,y=7.3,font_size='6.726190',text_anchor='start')
t.text='Call-result excerpt';key.append(t);leg.insert(3,key)
E.indent(svg,space='  ');svg.write(sys.argv[2],encoding='UTF-8',xml_declaration=True)

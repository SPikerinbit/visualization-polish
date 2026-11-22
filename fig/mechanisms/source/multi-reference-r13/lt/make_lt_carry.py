"""Add the carried segment to the R11/R12 tree source; usage: python make_lt_carry.py BEFORE.svg AFTER.svg"""
from lxml import etree as ET
from pathlib import Path
import sys
n={'s':'http://www.w3.org/2000/svg'}
def main(src,dst):
 t=ET.parse(str(src))
 get=lambda p:t.xpath(p,namespaces=n)[0]
 root=get('//s:g[@id="after"]')
 get('//s:g[@id="after"]/s:text[1]').text='(b) After replay'
 get('//s:desc').text='After [1,2] is emitted, the active pointers lead to R2. One call ranks [6,14] and the two path losers. Local replay (1) passes [5,6] to (2) and retains [7,14]; (2) outputs [3,4] and retains [5,6]. Pointers in the final tree denote the next refill directions.'
 edge=get('//s:g[@id="after"]/s:line[1]')
 assert edge.get('x1')=='180.9466' and edge.get('x2')=='171.2716'
 edge.set('stroke','#425E4D');edge.set('stroke-width','0.8')
 edge.addnext(ET.Element('{'+n['s']+'}polygon',points='180.947,37 179.533,39.071 178.514,37.356',fill='#425E4D'))
 tag=get('//s:g[@id="after"]/s:text[text()="(2)"]');tag.set('x','174.0');tag.set('y','32.2')
 ET.SubElement(root,'{'+n['s']+'}text',{'x':'166.8','y':'40.0','font-size':'5.5','fill':'#425E4D','text-anchor':'middle','font-weight':'normal'}).text='[5, 6]'
 t.write(str(dst),xml_declaration=True,encoding='utf-8')
if __name__=='__main__':main(*map(Path,sys.argv[1:3]))

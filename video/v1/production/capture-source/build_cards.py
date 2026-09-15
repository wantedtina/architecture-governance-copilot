from pathlib import Path
from html import escape
import resvg_py

def make(kind):
 s=['<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080"><rect width="1920" height="1080" fill="#F7F8FA"/><rect width="1310" height="10" fill="#0473EA"/><rect x="1310" width="610" height="10" fill="#38D200"/>']
 def t(x,y,lines,size=26,col='#061D33',weight=400):
  for i,line in enumerate(lines):s.append(f'<text x="{x}" y="{y+i*(size+12)}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{col}">{escape(line)}</text>')
 def b(x,y,w,h,fill='#FFFFFF',stroke='#D8E2EC'):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
 def arrow(x,y):t(x,y,['→'],45,'#008acb')
 if kind=='process':
  t(90,87,['CURRENT GOVERNANCE PROCESS'],22,'#0473ea',700);t(90,154,['Architecture work spans documents, meetings and tracked actions'],43,weight=700)
  t(90,211,['Project teams prepare and revise; Domain Architects review and decide.'],27,'#66727d')
  cards=[('Project team','Prepare the Solution Intent','Confluence document'),('Governance reference','Track review and actions','Azure Boards ticket'),('Domain review','Discuss design and evidence','Teams meeting'),('Findings and actions','Capture decisions and owners','Source evidence'),('SI revision','Update the authoritative SI','Project team'),('Review and decision','Check the revised evidence','Domain Architect')]
  for i,(title,a,c) in enumerate(cards):
   x=90+(i%3)*595;y=300+(i//3)*245;b(x,y,550,193);b(x+20,y+23,44,44,'#0473ea','#0473ea');t(x+34,y+55,[str(i+1)],25,'#fff',700);t(x+85,y+56,[title],28,weight=700);t(x+85,y+106,[a,c],24,'#526a7b')
   if i%3<2:arrow(x+556,y+110)
  b(90,823,1740,123,'#061d33','#061d33');t(120,867,['THE FRICTION'],22,'#70e545',700);t(120,914,['Decisions, evidence and ownership must be reconstructed across handoffs.'],31,'#fff')
 if kind=='solution':
  t(90,87,['PROPOSED SOLUTION'],22,'#0473ea',700);t(90,154,['Assist the work. Preserve the evidence. Keep people accountable.'],43,weight=700)
  t(90,210,['Two distinct activities, with explicit human checkpoints.'],27,'#66727d')
  t(90,306,['DRAFTING'],24,'#0473ea',700)
  for x,title,lines,fill in [(90,'Selected project context',['Template · repository','Supporting evidence'], '#fff'),(655,'AI-assisted SI draft',['Structured proposal','Traceable source context'],'#E7F2FC'),(1220,'Human-confirmed draft',['Review and edit','Ready for team use'],'#EAF8E2')]:
   b(x,337,510,162,fill);t(x+25,381,[title],29,weight=700);t(x+25,428,lines,24,'#526a7b')
  arrow(610,430);arrow(1175,430)
  t(90,568,['GOVERNANCE REVIEW'],24,'#0473ea',700)
  for x,w,title,lines,fill in [(90,365,'Authoritative inputs',['SI + transcript','Review metadata'],'#fff'),(520,365,'Review proposal',['Findings · decisions','Actions + evidence'],'#E7F2FC'),(950,365,'Human Review',['Edit · include / exclude','Confirm reviewed record'],'#EAF8E2'),(1380,450,'Governance outputs',['Minutes + work items','Controlled delivery'],'#061d33')]:
   b(x,600,w,174,fill);t(x+23,644,[title],27,'#fff' if fill=='#061d33' else '#061d33',700);t(x+23,690,lines,23,'#c7d8e5' if fill=='#061d33' else '#526a7b')
  for x in [466,896,1326]:arrow(x,699)
  t(90,857,['A confirmed draft is not silently treated as a published review source.'],26,'#526a7b')
  t(90,916,['Evidence traceability'],27,'#0473ea',700);t(690,916,['Visible human choices'],27,'#238500',700);t(1290,916,['No automatic approval'],27,weight=700)
 if kind=='value':
  t(90,87,['WHAT WE STRENGTHENED'],22,'#0473ea',700);t(90,154,['From a traceable record to visible, controlled action'],44,weight=700)
  t(90,210,['Responding to judge feedback through demonstrated behavior.'],27,'#66727d')
  for i,(title,lines) in enumerate([('Visible human edits',['Owner changes and exclusions','Explicit confirmation before outputs']),('Evidence through outputs',['Original quote → reviewed action','Minutes and work item stay traceable']),('Consistency and delivery',['Changed inputs invalidate outputs','Preview → Confirm → Create → Verify'])]):
   x=90+i*590;b(x,330,550,350);t(x+28,393,[title],29,weight=700);t(x+28,466,lines,25,'#526a7b')
  b(90,765,1740,170,'#061d33','#061d33');t(120,817,['Expected value'],28,'#70e545',700);t(120,863,['Less repeated reconstruction. Easier verification.'],34,'#fff');t(120,909,['Business validation is the next step; benefits have not been quantified.'],25,'#c7d8e5')
 t(90,1035,['ARCHITECTURE GOVERNANCE COPILOT  ·  ACCELERATE 3.0'],18,'#66727d',700)
 s.append('</svg>');p=Path('frames')/(kind+'.svg');p.write_text('\n'.join(s));p.with_suffix('.png').write_bytes(resvg_py.svg_to_bytes(svg_path=str(p)))
for k in ['process','solution','value']:make(k)

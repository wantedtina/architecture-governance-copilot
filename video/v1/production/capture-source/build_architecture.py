from pathlib import Path
from html import escape
import resvg_py
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"><title>Architecture Governance Copilot - System architecture</title><desc>Project Team and Domain Architect use a Service Bench front end. SKE contains the backend, persistent database and integration adapters. Teams transcripts are imported manually. SKE sends telemetry automatically to COP, the Central Observability Platform, with Grafana and Kibana.</desc><defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto-start-reverse"><path d="M0,0 L8,4 L0,8" fill="none" stroke="#8fbbd5" stroke-width="1.4"/></marker></defs><rect width="1920" height="1080" fill="#061D33"/><rect width="1310" height="9" fill="#0473EA"/><rect x="1310" width="610" height="9" fill="#38D200"/>']
def t(x,y,lines,size=22,color='#fff',weight=400):
 for i,line in enumerate(lines):s.append(f'<text x="{x}" y="{y+i*(size+9)}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(line)}</text>')
def box(x,y,w,h,fill='#123a59',stroke='#527d9b',dash=False):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"'+(' stroke-dasharray="9 7"' if dash else '')+'/>')
def ar(d,two=False,dash=False):s.append(f'<path d="{d}" fill="none" stroke="#8fbbd5" stroke-width="2.5" marker-end="url(#arr)"'+(' marker-start="url(#arr)"' if two else '')+(' stroke-dasharray="7 5"' if dash else '')+'/>')
t(80,74,['SYSTEM ARCHITECTURE'],22,'#70e545',700);t(80,134,['Architecture Governance Copilot'],47,'#fff',700);t(80,181,['Selected context. AI-assisted drafting and review. Human-controlled action.'],26,'#b4ccdc')
box(355,230,315,570,'#08233a','#0473ea',True);t(382,270,['SERVICE BENCH'],22,'#7fc3ff',700)
box(710,230,600,570,'#08233a','#38d200',True);t(737,270,['SKE'],22,'#70e545',700)
box(1360,230,500,570,'#08233a','#6289a5',True);t(1386,270,['ENTERPRISE SERVICES'],22,'#b4ccdc',700)
box(55,336,260,144,'#fff','#d8e2ec');t(77,374,['Project Team'],28,'#061d33',700);t(77,411,['Product Owners','Developers · action owners'],19,'#33576e');t(77,462,['Primary users'],18,'#0b66c3',700)
box(55,510,260,117,'#fff','#d8e2ec');t(77,549,['Domain Architect'],25,'#061d33',700);t(77,583,['Architecture review','Formal decision authority'],18,'#33576e')
box(385,340,255,219,'#0b66c3','#58a8f4');t(407,381,['AGC Front End'],26,'#fff',700);t(407,424,['Context selection','Drafting and review','Evidence inspection','Human confirmation'],21)
ar('M317,408 H379');ar('M317,566 H341 V490 H379')
box(55,668,260,112,'#0e304b','#527d9b');t(77,705,['Teams transcript'],23,'#fff',700);t(77,741,['User export / manual transfer'],18,'#c7d8e5')
box(385,630,255,125,'#0e304b','#527d9b');t(407,668,['Transcript intake'],23,'#fff',700);t(407,703,['Manual import / paste','Review metadata'],20,'#c7d8e5');ar('M317,722 H379');ar('M511,628 V565')
ar('M642,447 H739',True);t(663,423,['HTTPS'],17,'#7fc3ff')
box(745,340,245,238,'#12456a','#70e545');t(765,379,['AGC Backend API'],23,'#fff',700);t(765,424,['Drafting and governance','Schema + evidence checks','Confirmed context scope','Minutes + work items','Controlled delivery'],18)
t(883,613,['State + audit'],16,'#80d8f5');ar('M866,580 V632',True)
# Explicit persistence store, with cylinder silhouette.
s.append('<path d="M745,661 C745,629 990,629 990,661 V775 C990,804 745,804 745,775 Z" fill="#173f59" stroke="#00a1e0" stroke-width="2"/><ellipse cx="867.5" cy="661" rx="122.5" ry="19" fill="#173f59" stroke="#00a1e0" stroke-width="2"/>')
t(810,711,['Database'],25,'#fff',700);t(765,740,['Records · source versions','Actions · receipts · audit'],18,'#c7d8e5')
t(1030,307,['INTEGRATION ADAPTERS'],17,'#9be880',700)
for y,title,lines in [(335,'Confluence',['Templates + SI snapshots']),(450,'AIF provider',['Scoped AI requests']),(621,'Azure DevOps',['Repos + Boards','Controlled work items'])]:
 box(1030,y,250,95 if len(lines)==1 else 120,'#0e304b','#70e545' if title=='AIF provider' else '#527d9b');t(1050,y+33,[title],23,'#70e545' if title=='AIF provider' else '#fff',700);t(1050,y+65,lines,18,'#c7d8e5')
ar('M992,467 H1010 V383 H1024');ar('M1010,467 H1024');ar('M1010,467 V680 H1024')
for y,title,lines in [(328,'Confluence API',['Governed templates','Versioned Solution Intents']),(450,'AI Factory (AIF)',['Confirmed context in','Structured proposal out']),(588,'Azure Repos API',['Selected repository + revision']),(684,'Azure Boards API',['Governance metadata + work items'])]:
 box(1410,y,420,105 if len(lines)==2 else 83,'#123a59','#70e545' if title=='AI Factory (AIF)' else '#527d9b');t(1435,y+33,[title],25,'#70e545' if title=='AI Factory (AIF)' else '#fff',700);t(1435,y+65,lines,19,'#c7d8e5')
ar('M1282,382 H1404',True);ar('M1282,499 H1404',True);ar('M1282,669 H1350 V629 H1404',True);ar('M1350,669 V725 H1404',True)
# COP is an enterprise platform outside the application SKE deployment.
box(1360,850,500,147,'#0e304b','#00a1e0');t(1386,887,['COP'],27,'#80d8f5',700);t(1459,887,['Central Observability Platform'],20,'#fff',700);t(1386,924,['Logs · traces · metrics'],23,'#c7d8e5');t(1386,966,['Grafana / Kibana'],23,'#fff',700)
ar('M1265,802 V826 H1600 V844',False,True);t(920,850,['Automatic SKE telemetry'],20,'#80d8f5')
box(355,890,955,107,'#0b2a40','#527d9b');t(382,927,['Enterprise controls'],24,'#fff',700);t(382,963,['Identity and permissions · secrets · encryption · data policy'],22,'#c7d8e5')
t(80,1046,['ARCHITECTURE GOVERNANCE COPILOT  ·  TWO TOKENS ONE BRAIN'],19,'#b4ccdc',700)
s.append('</svg>');p=Path('export/system-architecture.svg');p.write_text('\n'.join(s));Path('frames/system-architecture.png').write_bytes(resvg_py.svg_to_bytes(svg_path=str(p)));Path('export/system-architecture.png').write_bytes(Path('frames/system-architecture.png').read_bytes())

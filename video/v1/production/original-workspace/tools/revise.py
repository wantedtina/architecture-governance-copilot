from pathlib import Path
import json
p=Path('tools/build_cards.py');s=p.read_text()
a=s.index("  cards=[");b=s.index("  b(90,823",a)
s=s[:a]+'''  cards=[('Prepare the SI','Describe the proposed solution','Tool: Confluence'),('Set up governance tracking','Link the review and its actions','Tool: Azure Boards'),('Review the design','Discuss the SI and its evidence','Tool: Teams'),('Record findings and actions','Capture decisions and owners','Owner: Project team'),('Revise the SI','Apply the agreed changes','Tool: Confluence'),('Review and decide','Check the revised SI','Owner: Domain Architect')]
  for i,(title,a,c) in enumerate(cards):
   col=i if i<3 else 5-i
   x=90+col*595;y=300+(i//3)*245;b(x,y,550,193);b(x+20,y+23,44,44,'#0473ea','#0473ea');t(x+34,y+55,[str(i+1)],25,'#fff',700);t(x+85,y+56,[title],26,weight=700);t(x+85,y+106,[a],24,'#526a7b');t(x+85,y+148,[c],22,'#526a7b')
  s.append('<defs><marker id="flow" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="none" stroke="#008acb" stroke-width="1.5"/></marker></defs>')
  for d in ['M645,397 H676','M1240,397 H1271','M1555,499 V536','M1275,642 H1244','M680,642 H649']:
   s.append(f'<path d="{d}" fill="none" stroke="#008acb" stroke-width="3" marker-end="url(#flow)"/>')
'''+s[b:]
s=s.replace("['Two distinct activities, with explicit human checkpoints.']","['Draft and review in the app. Keep the authoritative SI in Confluence.']")
s=s.replace("'Human-confirmed draft',['Review and edit','Ready for team use']","'User-reviewed draft',['Accept, change or reject','User updates Confluence']")
s=s.replace("  t(90,857,['A confirmed draft is not silently treated as a published review source.'],26,'#526a7b')\n  t(90,916,['Evidence traceability'],27,'#0473ea',700);t(690,916,['Visible human choices'],27,'#238500',700);t(1290,916,['No automatic approval'],27,weight=700)","  b(90,812,1740,143,'#061d33','#061d33');t(115,851,['CONFLUENCE REMAINS THE SI SOURCE OF TRUTH'],24,'#70e545',700);t(115,896,['The app produces drafts and suggested changes; it does not write to or edit Confluence.'],26,'#fff');t(115,934,['Users decide what to use, then write and update the SI themselves in Confluence.'],25,'#c7d8e5')")
p.write_text(s)
p=Path('tools/build_architecture.py');s=p.read_text()
s=s.replace("t(77,411,['Product Owners','Developers · action owners'],19,'#33576e');t(77,462,['Primary users'],18,'#0b66c3',700)","t(77,414,['Draft preparation','Action follow-through'],19,'#33576e')")
s=s.replace("box(55,510,260,117", "box(55,510,260,144").replace("t(77,549,['Domain Architect'],25","t(77,548,['Domain Architect'],25").replace("t(77,583,['Architecture review','Formal decision authority'],18","t(77,588,['Architecture review','Formal decision authority'],19")
s=s.replace("['Identity and permissions · secrets · encryption · data policy']","['Role-based permissions · secrets · encryption · data policy']")
s=s.replace("['Templates + SI snapshots']","['Read-only templates + SI']")
s=s.replace("['Governed templates','Versioned Solution Intents']","['Authoritative SI + templates','Users write and edit here']")
p.write_text(s)
rows=json.loads(Path('/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/2026-09-14-v2.1/story.json').read_text())
updates={
'title':(10,["Hello, we're Two Tokens One Brain. Let me show you how Architecture Governance Copilot helps teams prepare and follow up on architecture reviews."]),
'process':(18,["Today, a project team writes its Solution Intent in Confluence, tracks the review in Azure Boards, and discusses the design in Teams.","Afterwards, someone has to bring the decisions, evidence and action owners back together. That's the work we're trying to make easier."]),
'solution':(20,["Our app helps with drafting and review, but Confluence remains the source of truth for the Solution Intent.","We only produce drafts and suggested changes. The app never edits Confluence. Users decide what to keep and make those changes themselves."]),
'architecture':(23,["Both project teams and Domain Architects use the app, with different permissions and responsibilities.","The interface sits in Service Bench. SKE hosts the backend and database, with adapters for Confluence, AI Factory and Azure DevOps.","Teams transcripts are imported manually. Logs, traces and metrics go to COP."]),
'draft':(27,["Let's start with the project team. I open the project context, which brings together the template, repository revision and governance details.","I save the supporting evidence, confirm the package, and generate a Solution Intent draft.","I review and confirm that draft here. I would then make any changes I want in Confluence myself. The governance review is a separate step."]),
'inputs':(19,["For the review, I select the authoritative Solution Intent, import the meeting transcript, and load the review details.","I check and confirm these inputs before running the analysis. The app then puts together a proposal, with evidence for us to inspect."]),
'human':(33,["This is where I review what the app has proposed. The transcript says Riley will document the retry controls. I'm changing that action's owner to Taylor Kim.","Notice that Riley's original words stay visible, alongside my change.","I'm also leaving the retention finding out of this record. That doesn't mean the issue is resolved or approved.","The outcome is still Changes Requested. I confirm my reviewed record before generating the outputs."]),
'outputs':(23,["The change summary shows what I edited and left out. Let's follow that retry action: here's Riley's original quote, then Taylor as the owner I confirmed, followed by the minutes and work-item preview.","We can check how the final action came from the original discussion, and see where I changed it."]),
'delivery':(29,["Next, I'll deliver the work item. I preview the request and check the owner, due date, parent reference and supporting evidence.","The summary and JSON show the same request. Once I'm happy with it, I confirm and create the work item.","The app reads it back to check the result. The receipt is visible here, and this action can't simply be submitted again."]),
'invalidation':(19,["Now let's see what happens if I change the transcript. I add some new context, and the previous outputs become invalid.","I need to run the analysis and review again before using new outputs. The work item I already delivered is still recorded."]),
'value':(8,["We've made edits easier to see, evidence easier to follow, and delivery easier to check. That's our response to the feedback."]),
'close':(9,["That's our demo. We want teams to spend less time piecing reviews together, while keeping people in control. Thank you for watching."])
}
for r in rows:r['duration'],r['sentences']=updates[r['id']]
assert sum(r['duration'] for r in rows)==238
Path('story.json').write_text(json.dumps(rows,indent=2)+'\n')
p=Path('tools/voice.py');s=p.read_text().replace('narration-v2.wav','narration-v2.2.wav').replace('copilot-v2.srt','copilot-v2.2.srt');p.write_text(s)

from pathlib import Path
import json,shutil
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import fitz
out=Path('export');rows=json.loads(Path('story.json').read_text())
def mm(t):return f'{t//60:02}:{t%60:02}'
s=['# Narration - v2.2','','Reference video: 3:58. Read the paragraphs, not the headings or timecodes.','Speak as if presenting the demo to the judges. Use natural pauses, not an advertising voice.','The temporary track uses the installed Daniel voice. Your recording will replace it; timing and subtitles will then be adjusted.',''];n=0;sections=[]
for r in rows:
 s.extend([f"## {mm(n)}-{mm(n+r['duration'])} - {r['title']}",'',' '.join(r['sentences']),''])
 sections.append({'id':r['id'],'start':n,'end':n+r['duration'],'title':r['title']});n+=r['duration']
s.extend(['## Pronunciation','','SI: ess-eye. SKE: ess-kay-ee. COP: see-oh-pee. JSON: jay-son.','Each section may be recorded separately. Leave a short pause before and after.',''])
(out/'NARRATION_V2.2.md').write_text('\n'.join(s))
old=Path('/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2.1/export')
shutil.copy2(old/'FORM_TEXT.md',out/'FORM_TEXT.md')
for k in ['process','solution']:
 for ext in ['png','svg']:shutil.copy2(Path('frames')/(k+'.'+ext),out/(k+'.'+ext))
pieces=json.loads((old/'edit-timeline.json').read_text())['demo_source_pieces']
(out/'edit-timeline.json').write_text(json.dumps({'revision':'v2.2','duration_seconds':n,'sections':sections,'demo_source_pieces':pieces},indent=2)+'\n')
c=canvas.Canvas(str(out/'system-architecture.pdf'),pagesize=(960,540));c.setTitle('Architecture Governance Copilot - System architecture');c.setAuthor('Two Tokens One Brain');c.drawImage(ImageReader('frames/system-architecture.png'),0,0,960,540);c.showPage();c.save()
d=fitz.open(out/'system-architecture.pdf');d[0].get_pixmap(matrix=fitz.Matrix(2,2)).save('qa/architecture-pdf.png')
notes='''# Review v2.2 - clearer flow and presenter narration

Application revision: `81835b9ced0c709f4003522557b6423bc4bdaa18`.

## Changes

- The process slide uses a continuous snake: 1, 2, 3 across the top, then down to 4,
  then left to 5 and 6. Each step has an action description and a labelled Tool or Owner.
- The solution slide explicitly identifies Confluence as the SI source of truth. The app
  produces drafts and suggested changes; users decide what to use and edit Confluence themselves.
  The app does not write or edit Confluence. This is a design boundary, not a claim of compliance certification.
- Project Team and Domain Architect have equal actor boxes and typography in the architecture,
  with different responsibilities and role-based permissions. There is no Primary users label.
  The Confluence adapter is read-only; manual user edits take place in Confluence UI.
- Narration is rewritten as a direct presentation to judges, with a greeting, first-person
  demo walkthrough and a spoken thank-you. It retains evidence, human edits, finding exclusion,
  controlled delivery and changed-input invalidation. No quantified benefit is invented.
- The video starts on the title slide and lasts 3:58. The full demo footage, cursor halo and
  click highlights are retained. Narration and captions are regenerated against the new timeline.

## Deliverables

- `architecture-governance-copilot-v2.2-narrated.mp4`: 1080p, 30 fps, H.264/AAC,
  temporary Daniel English narration and burned-in English captions.
- `architecture-governance-copilot-v2.2.srt`: matching standalone captions.
- `NARRATION_V2.2.md`: complete recording script with section times.
- `system-architecture.pdf`, `.png`, `.svg`: architecture diagram and editable source.
- `process.png`, `.svg`, `solution.png`, `.svg`: revised slide images and editable sources.
- `FORM_TEXT.md`: unchanged approved three-field text.
- `edit-timeline.json`: section times and preserved demo edit mapping.

## Scope

The architecture represents the agreed system design, including persistence and enterprise controls;
it does not assert production deployment or live integration acceptance. Teams transcripts remain
manual imports. This session changes presentation materials only. No application code, tests,
fixtures, dependencies, refinement register, historical media or tags were changed. Previous exports
are retained. Nothing was committed, pushed, uploaded or submitted.

Final human voice replacement remains pending the user's recording.
'''
(out/'README.md').write_text(notes)
repo=Path('/Users/wantedtina/Repos/architecture-governance-copilot-submission-materials/docs/submission/2026-09-14');dest=repo/'v2.2';dest.mkdir(exist_ok=True)
for source,name in [('NARRATION_V2.2.md','NARRATION.md'),('README.md','REVISION_NOTES.md'),('system-architecture.svg','system-architecture.svg'),('process.svg','process.svg'),('solution.svg','solution.svg')]:shutil.copy2(out/source,dest/name)
p=repo/'README.md';s=p.read_text();a=s.index('## Current review version');b=s.index('Status:',a)
s=s[:a]+'''## Current review version - v2.2

[V2.2 revision notes](v2.2/REVISION_NOTES.md), [recording script](v2.2/NARRATION.md),
and [architecture](v2.2/system-architecture.svg) supersede earlier presentation versions.
The 3:58 video starts with the title and uses a continuous six-step process diagram, an explicit
Confluence source-of-truth boundary, equal application-user roles and conversational narration.
The complete demonstration, temporary English voice, subtitles and click highlights remain.

External files: `/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2.2/export/`.
The approved three-field form text is unchanged. Earlier preparation records below are historical
and do not override v2.2. Human voice-over replacement is pending.

'''+s[b:];p.write_text(s)
print('PDF, recording script, timeline and documentation generated.')

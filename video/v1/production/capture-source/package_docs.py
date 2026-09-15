from pathlib import Path
import json,shutil
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
out=Path('export');rows=json.loads(Path('story.json').read_text());root=Path('/Users/wantedtina/Repos/architecture-governance-copilot-submission-materials/docs/submission/2026-09-14');v2=root/'v2';v2.mkdir(exist_ok=True)
def mm(n):return f'{n//60:02}:{n%60:02}'
text=['# Narration - revised project introduction','','Reference picture: 3:58. Temporary narration uses the installed macOS Daniel voice.','Record only the paragraphs; headings and timecodes are directions, not spoken text.','Each section may be recorded separately, with a short pause before and after. The human voice replaces the temporary track; picture and subtitles will be re-aligned.',''];t=0
for r in rows:
 text += [f"## {mm(t)}-{mm(t+r['duration'])} - {r['title']}",'',' '.join(r['sentences']),''];t+=r['duration']
text+=['## Pronunciation','','SI: ess-eye. SKE: ess-kay-ee. COP: see-oh-pee. AI: ay-eye. JSON: jay-son.','No background music is required. Keep raw recordings outside Git.','']
(out/'NARRATION_V2.md').write_text('\n'.join(text));shutil.copy2(out/'NARRATION_V2.md',v2/'NARRATION.md');shutil.copy2(out/'system-architecture.svg',v2/'system-architecture.svg')
for name in ['process','solution','value']:shutil.copy2(Path('frames')/(name+'.svg'),v2/(name+'.svg'))
shutil.copy2(root/'FORM_TEXT.md',out/'FORM_TEXT.md')
c=canvas.Canvas(str(out/'system-architecture.pdf'),pagesize=(960,540));c.setTitle('Architecture Governance Copilot - System architecture');c.setAuthor('Two Tokens One Brain');c.drawImage(ImageReader('frames/system-architecture.png'),0,0,960,540);c.showPage();c.save()
(v2/'REVISION_NOTES.md').write_text('''# Revision 2 - project introduction and architecture

This revision supersedes the first silent review copy. It follows the historical human-voice
video's introduction structure: current process and pain, proposed solution, architecture,
working demonstration, value and close. A seven-second Human Review hook preserves the requested
opening while the subsequent introduction supplies context before the full workflow.

## User feedback addressed

- Introduce the project to judges, rather than concatenate unexplained UI steps.
- Include a generated English narration preview, burned-in subtitles and a separate SRT.
- Re-record normal UI interactions with a yellow cursor halo and red labelled target outline.
- Preserve end-to-end drafting, separate authoritative review, confirmation, outputs and delivery.
- Demonstrate the approved Riley Chen to Taylor Kim edit, retention-finding exclusion, original
  evidence to confirmed record to outputs, and the actual input-change invalidation warning.
- Retain the historical opening/closing branding and exact team credits.
- Derive the architecture from the historical Service Bench / SKE / adapter / enterprise-service
  layout. Remove Production/Target wording from the artifact title.
- Make Project Team the primary user, with Product Owners and developers/action owners. Give
  Domain Architect its own actor box and review/decision responsibility. Remove Human reviewers.
- Add an explicit persistent Database for records, source versions, actions, receipts and audit.
- Add COP (Central Observability Platform) outside the SKE application boundary, with automatic
  SKE telemetry and Grafana/Kibana. This topology reflects the user's supplied design information.
- Retain manual Teams transcript import; no Teams API connector.
- Preserve the three approved form paragraphs byte-for-byte.

## Scope

Application commit remains 81835b9ced0c709f4003522557b6423bc4bdaa18. The architecture describes
the agreed system design; it does not assert that the locked PoC implements persistence or that
live integrations have passed acceptance. No application code, tests, dependencies, refinement
register, history or tags are changed. All media/audio/PDF exports remain outside Git, under
/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2/export/.

Temporary speech is system-generated Daniel narration at a conversational preview pace, not a
clone of the user's voice. Final human recording will replace it after review.
''')
print('Documentation and PDF ready')

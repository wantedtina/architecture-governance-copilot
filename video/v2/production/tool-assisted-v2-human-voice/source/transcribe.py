"""Run local ASR only; never transmit recordings to a service."""
from pathlib import Path
import subprocess,json,concurrent.futures,os
ROOT=Path(__file__).resolve().parents[1]; W=ROOT/'tools/whisper.cpp'
if not (W/'build/bin/whisper-cli').is_file():
 W=Path('/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/tool-assisted-v2-human-voice/tools/whisper.cpp')
# Resolve local libraries after retiring the former build-directory path.
ENV=os.environ.copy()
ENV['DYLD_LIBRARY_PATH']=str(W/'build/bin')+(os.pathsep+ENV['DYLD_LIBRARY_PATH'] if ENV.get('DYLD_LIBRARY_PATH') else '')
rows=json.loads((ROOT/'source/v2-story.json').read_text())
def run(row):
 k=row['id']; cmd=[str(W/'build/bin/whisper-cli'),'-m',str(W/'models/ggml-base.en.bin'),'-f',str(ROOT/'audio'/(k+'-asr.wav')),'-l','en','-t','2','-ojf','-ml','1','-sow','-of',str(ROOT/'qa'/(k+'-asr'))]
 (ROOT/'qa'/(k+'-asr-command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
 with (ROOT/'qa'/(k+'-asr.log')).open('w') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True,timeout=180,env=ENV)
 data=json.loads((ROOT/'qa'/(k+'-asr.json')).read_text());return k,''.join(x['text'] for x in data['transcription'])
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 for k,t in ex.map(run,rows):print(k+': '+t,flush=True)

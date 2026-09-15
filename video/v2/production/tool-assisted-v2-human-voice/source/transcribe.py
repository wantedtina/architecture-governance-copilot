"""Run local ASR only; never transmit recordings to a service."""
from pathlib import Path
import subprocess,json,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]; W=ROOT/'tools/whisper.cpp'
rows=json.loads((ROOT/'source/v2-story.json').read_text())
def run(row):
 k=row['id']; cmd=[str(W/'build/bin/whisper-cli'),'-m',str(W/'models/ggml-base.en.bin'),'-f',str(ROOT/'audio'/(k+'-asr.wav')),'-l','en','-t','2','-ojf','-ml','1','-sow','-of',str(ROOT/'qa'/(k+'-asr'))]
 (ROOT/'qa'/(k+'-asr-command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
 with (ROOT/'qa'/(k+'-asr.log')).open('w') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True,timeout=180)
 data=json.loads((ROOT/'qa'/(k+'-asr.json')).read_text());return k,''.join(x['text'] for x in data['transcription'])
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 for k,t in ex.map(run,rows):print(k+': '+t,flush=True)

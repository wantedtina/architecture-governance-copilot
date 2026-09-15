from pathlib import Path
import json,subprocess
FF='/Users/wantedtina/.cache/uv/archive-v0/UrHfmy6kUrGrSBmd/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
old=Path('/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2')
rows=json.loads(Path('story.json').read_text());outs=[]
static={'title':'/Users/wantedtina/Repos/architecture-governance-copilot/video/assets/opening-title.png','process':'frames/process.png','solution':'frames/solution.png','architecture':'frames/system-architecture.png','value':'frames/value.png','close':'/Users/wantedtina/Repos/architecture-governance-copilot/video/assets/closing-card.png'}
for row in rows:
 k=row['id']
 if k in static:
  p=Path('clips/edited')/(k+'.mp4')
  if p.exists():outs.append(p.resolve());continue
  subprocess.run([FF,'-y','-loglevel','error','-loop','1','-i',static[k],'-vf','scale=1840:1035:flags=lanczos,pad=1920:1080:40:0:color=0x061d33,setsar=1,format=yuv420p','-t',str(row['duration']),'-r','30','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','4',str(p)],check=True)
 else:p=old/'clips/edited'/(k+'.mp4')
 outs.append(p.resolve());print('Picture ready:',k,flush=True)
Path('clips/concat.txt').write_text(''.join(f"file '{p}'\n" for p in outs))
subprocess.run([FF,'-y','-loglevel','error','-f','concat','-safe','0','-i','clips/concat.txt','-c','copy','clips/picture.mp4'],check=True)
subs=json.loads(Path('audio/subtitles.json').read_text())
def ass_ts(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
def srt_ts(t):
 c=round(t*1000);return f'{c//3600000:02}:{c//60000%60:02}:{c//1000%60:02},{c%1000:03}'
def wrap(t):
 if len(t)<=66:return [t]
 w=t.split();i=min(range(1,len(w)),key=lambda i:abs(len(' '.join(w[:i]))-len(' '.join(w[i:]))));return [' '.join(w[:i]),' '.join(w[i:])]
ass=(old/'audio/subtitles.ass').read_text().split('Dialogue:')[0]
for a,b,t in subs:ass+=f'Dialogue: 0,{ass_ts(a)},{ass_ts(b)},Default,,0,0,0,,'+'\\N'.join(wrap(t))+'\n'
Path('audio/subtitles.ass').write_text(ass)
Path('export/architecture-governance-copilot-v2.2.srt').write_text('\n\n'.join(f'{i+1}\n{srt_ts(a)} --> {srt_ts(b)}\n'+'\n'.join(wrap(t)) for i,(a,b,t) in enumerate(subs))+'\n')
subprocess.run([FF,'-y','-loglevel','error','-i','clips/picture.mp4','-i','audio/narration-v2.2.wav','-vf','drawbox=x=0:y=968:w=1920:h=112:color=0x061d33:t=fill,ass=audio/subtitles.ass','-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','18','-threads','4','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','192k','-ar','48000','-t','238','-movflags','+faststart','export/architecture-governance-copilot-v2.2-narrated.mp4'],check=True)
print('V2.2 rendered.',flush=True)

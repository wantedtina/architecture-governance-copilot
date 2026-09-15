from pathlib import Path
import json,subprocess,textwrap
FF='/Users/wantedtina/.cache/uv/archive-v0/UrHfmy6kUrGrSBmd/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
rows=json.loads(Path('story.json').read_text());dur=json.loads(Path('clips/durations.json').read_text());TMP=Path('clips/edited');TMP.mkdir(exist_ok=True)
pieces={'hook':[(4,8,7)],'draft':[(0,5,7),(5,9,5),(9,14,8),(14,19.9,7)],'inputs':[(0,13.8,16),(17.6,dur['inputs'],3)],'human':[(0,6,11),(6,10,7),(10,18,9),(18,22.3,6)],'outputs':[(0,4,5),(4,10,12),(10,15,6)],'delivery':[(0,5,5),(5,10,5),(10,17,7),(17,23,12)],'invalidation':[(0,9,8),(9,dur['invalidation'],11)]}
static={'title':'/Users/wantedtina/Repos/architecture-governance-copilot/video/assets/opening-title.png','process':'frames/process.png','solution':'frames/solution.png','architecture':'frames/system-architecture.png','value':'frames/value.png','close':'/Users/wantedtina/Repos/architecture-governance-copilot/video/assets/closing-card.png'}
outs=[]
for row in rows:
 key=row['id'];outfile=TMP/(key+'.mp4');duration=row['duration'];
 if key not in ['delivery','invalidation'] and outfile.exists():outs.append(outfile.resolve());continue
 cmd=[FF,'-y','-loglevel','error']
 if key in pieces:
  src='human-clean' if key in ['hook','human'] else key;cmd+=['-i',f'clips/{src}.webm'];filters=[];labels=[]
  n=len(pieces[key]);filters.append('[0:v]split='+str(n)+''.join(f'[s{i}]' for i in range(n)))
  for i,(start,end,target) in enumerate(pieces[key]):
   filters.append(f'[s{i}]trim=start={start}:end={end},setpts={target/(end-start):.8f}*(PTS-STARTPTS),fps=30,tpad=stop_mode=clone:stop_duration=1,trim=duration={target}[p{i}]');labels.append(f'[p{i}]')
  filters.append(''.join(labels)+f'concat=n={n}:v=1:a=0,scale=1680:945:flags=lanczos,pad=1920:1080:120:0:color=0x061d33,setsar=1,format=yuv420p[out]')
  cmd+=['-filter_complex',';'.join(filters),'-map','[out]']
 else:cmd+=['-loop','1','-i',static[key],'-vf','scale=1840:1035:flags=lanczos,pad=1920:1080:40:0:color=0x061d33,setsar=1,format=yuv420p']
 cmd+=['-t',str(duration),'-r','30','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','4',str(outfile)];subprocess.run(cmd,check=True);outs.append(outfile.resolve());print('Picture',key,duration,flush=True)
concat=TMP/'concat.txt';concat.write_text(''.join(f"file '{p}'\n" for p in outs));subprocess.run([FF,'-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','clips/picture-v2.mp4'],check=True)
subtitles=json.loads(Path('audio/subtitles.json').read_text())
def stamp(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,36,&H00FFFFFF,&H00FFFFFF,&H00331D06,&H00331D06,0,0,0,0,100,100,0,0,1,1,0,2,120,120,24,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def wrap_caption(text):
 if len(text)<=66:return [text]
 words=text.split();i=min(range(1,len(words)),key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))));return [' '.join(words[:i]),' '.join(words[i:])]
for a,b,text in subtitles:ass+=f'Dialogue: 0,{stamp(a)},{stamp(b)},Default,,0,0,0,,'+'\\N'.join(wrap_caption(text))+'\n'
Path('audio/subtitles.ass').write_text(ass)
subprocess.run([FF,'-y','-loglevel','error','-i','clips/picture-v2.mp4','-i','audio/narration-v2.wav','-vf','drawbox=x=0:y=968:w=1920:h=112:color=0x061d33:t=fill,ass=audio/subtitles.ass','-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','18','-threads','4','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','192k','-ar','48000','-t','238','-movflags','+faststart','export/architecture-governance-copilot-v2-narrated.mp4'],check=True)
Path('export/edit-timeline.json').write_text(json.dumps(pieces,indent=2));print('Narrated, subtitled v2 ready.',flush=True)

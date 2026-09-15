"""Replace narration at native speed and retime preserved V2 pictures and captions."""
from pathlib import Path
import json,hashlib,shutil,subprocess,re,math,wave,concurrent.futures
ROOT=Path(__file__).resolve().parents[1];V2=ROOT.parent/'tool-assisted-v2';FF=json.loads((ROOT/'source/v2-runtime.json').read_text())['ffmpeg']
rows=json.loads((ROOT/'source/v2-timeline.json').read_text());story=json.loads((ROOT/'source/v2-story.json').read_text());voice=json.loads((ROOT/'source/voice-map.json').read_text())
REMOVED="That's our response to the feedback."
# Local ASR word boundaries inspected against measured pauses. Preserve canonical script
# names rather than replacing them with low-confidence ASR homophones.
BOUNDS={
 'title':[(.43,2.32),(2.4,8.72)],
 'process':[(.424,3.997),(4.347,8.868),(9.336,14.765),(15.139,16.8)],
 'solution':[(.751,2.98),(3.02,5.97),(6.641,11.54),(11.962,14.95)],
 'architecture':[(.934,7.345),(7.861,12.515),(13.004,16.235),(16.886,21.77)],
 'draft':[(.739,3.633),(4.12,8.015),(8.532,12.841),(13.541,15.609),(16.288,19.333),(20.041,21.962)],
 'inputs':[(.485,4.756),(5.359,8.638),(9.171,12.548),(13.007,17.086)],
 'human':[(1.121,3.419),(4.009,9.952),(10.275,14.472),(14.987,18.837),(19.471,23.154),(23.722,29.8)],
 'outputs':[(1.113,6.535),(7.033,14.02),(14.615,19.55)],
 'delivery':[(.916,4.789),(5.261,7.699),(8.181,10.535),(11.149,13.803),(14.504,16.813),(17.31,21.543)],
 'invalidation':[(1.019,3.55),(4.119,8.077),(8.498,12.402),(12.844,15.378)],
 'value':[(.952,4.156),(4.432,5.905)],
 'close':[(.926,5.417),(5.797,8.031)]}

def run(cmd,timeout=180):return subprocess.run(cmd,capture_output=True,check=True,timeout=timeout)
def stamp(t,srt=False):
 n=round(t*(1000 if srt else 100));b=1000 if srt else 100
 return f'{n//(3600*b):02}:{n//(60*b)%60:02}:{n//b%60:02}'+(','+f'{n%b:03}' if srt else '.'+f'{n%b:02}')
def wrap(t):
 if len(t)<=64:return t
 w=t.split();k=min(range(1,len(w)),key=lambda i:abs(len(' '.join(w[:i]))-len(' '.join(w[i:]))))
 return ' '.join(w[:k])+'\n'+' '.join(w[k:])
header=(V2/'production/audio/title.ass').read_text().split('Dialogue:')[0]
newrows=[];captionjson=[];srt=[];base=0;video_inputs=[]
(ROOT/'assets/picture').mkdir(exist_ok=True)
for old,s in zip(rows,story):
 k=old['id'];f=ROOT/voice[k]
 picture=ROOT/'assets/picture'/(k+'.mp4');original=V2/'production/clips'/(k+'.mp4')
 if not picture.exists():shutil.copy2(original,picture)
 assert hashlib.sha256(picture.read_bytes()).digest()==hashlib.sha256(original.read_bytes()).digest()
 video_inputs.append({'original':str(original),'copy':str(picture.relative_to(ROOT)),'sha256':hashlib.sha256(picture.read_bytes()).hexdigest()})
 with wave.open(str(ROOT/'audio'/(k+'-asr.wav'))) as w:raw_duration=w.getnframes()/w.getframerate()
 D=max(10 if k in ['title','close'] else 0,math.ceil(raw_duration+.45))
 caps=[x[:] for x in old['captions']]
 if k=='value':
  caps[-1][2]=caps[-1][2].replace(' '+REMOVED,'')
  s['sentences']=[t.replace(' '+REMOVED,'') for t in s['sentences']]
 if k=='outputs':caps=caps[:2]+[[caps[2][0],caps[3][1],caps[2][2]+' '+caps[3][2]]]
 assert len(caps)==len(BOUNDS[k])
 # Map V2 picture time to the user's speech, preserving the order and every source shot.
 anchors=[(0.,0.)];newcaps=[]
 for (a,b,text),(c,d) in zip(caps,BOUNDS[k]):
  assert 0<=c<d<=raw_duration,(k,c,d,raw_duration)
  anchors.extend([(a,c),(b,d)]);newcaps.append([c,d,text])
  srt.append([base+c,base+d,text]);captionjson.append({'text':text,'startMs':round((base+c)*1000),'endMs':round((base+d)*1000),'timestampMs':None,'confidence':None})
 if k=='outputs':anchors.extend([(8.5,9.12),(10.25,11.319)])
 anchors.append((float(old['duration']),float(D)));anchors.sort()
 assert all(a[0]<b[0] and a[1]<b[1] for a,b in zip(anchors,anchors[1:])),(k,anchors)
 # Two-pass loudness normalization. No time-stretch, no denoise, no removed speech.
 first=run([FF,'-hide_banner','-i',str(f),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr.decode()
 measurement=json.JSONDecoder().raw_decode(first[first.rfind('{'):])[0];(ROOT/'qa'/(k+'-loudness-input.json')).write_text(json.dumps(measurement,indent=2)+'\n')
 af='loudnorm=I=-16:TP=-1.5:LRA=11:measured_I='+measurement['input_i']+':measured_TP='+measurement['input_tp']+':measured_LRA='+measurement['input_lra']+':measured_thresh='+measurement['input_thresh']+':offset='+measurement['target_offset']+':linear=true:print_format=json'
 cmd=[FF,'-v','info','-i',str(f),'-af',af,'-ar','48000','-ac','2','-f','s16le','-']
 rr=run(cmd);pcm=rr.stdout; (ROOT/'qa'/(k+'-loudness-output.log')).write_bytes(rr.stderr)
 assert len(pcm)<=D*48000*4
 with wave.open(str(ROOT/'audio'/(k+'.wav')),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(pcm+bytes(D*48000*4-len(pcm)))
 ass=header+''.join(f'Dialogue: 0,{stamp(a)},{stamp(b)},Default,,0,0,0,,'+wrap(t).replace('\n','\\N')+'\n' for a,b,t in newcaps)
 (ROOT/'audio'/(k+'.ass')).write_text(ass)
 newrows.append({'id':k,'title':s['title'],'start':base,'end':base+D,'duration':D,'raw_audio_duration':raw_duration,'audio_speed':1.0,'voice':voice[k],'captions':newcaps,'picture_anchors':anchors})
 s['duration']=D;base+=D
assert base<=240
(ROOT/'source/timeline.json').write_text(json.dumps(newrows,indent=2)+'\n');(ROOT/'source/story.json').write_text(json.dumps(story,indent=2)+'\n')
(ROOT/'source/PICTURE_MANIFEST.json').write_text(json.dumps(video_inputs,indent=2)+'\n')
(ROOT/'source/captions.json').write_text(json.dumps(captionjson,indent=2)+'\n')
(ROOT/'export/architecture-governance-copilot-v2-human-voice.srt').write_text('\n\n'.join(f'{i}\n{stamp(a,True)} --> {stamp(b,True)}\n'+wrap(t) for i,(a,b,t) in enumerate(srt,1))+'\n')
with wave.open(str(ROOT/'audio/narration-human.wav'),'wb') as out:
 out.setnchannels(2);out.setsampwidth(2);out.setframerate(48000)
 for row in newrows:
  with wave.open(str(ROOT/'audio'/(row['id']+'.wav'))) as inp:out.writeframes(inp.readframes(inp.getnframes()))
print(json.dumps([{'id':r['id'],'start':r['start'],'end':r['end']} for r in newrows],indent=2),flush=True)

def render(row):
 k=row['id'];pts=row['picture_anchors'];expr=''
 for i in range(len(pts)-2,-1,-1):
  a,c=pts[i];b,d=pts[i+1];line=f'({c:.6f}+(T-{a:.6f})*{(d-c)/(b-a):.9f})'
  expr=line if not expr else f'if(lt(T,{b:.6f}),{line},{expr})'
 # The former subtitle band is completely repainted before the new captions are burned in.
 vf=f"setpts='({expr})/TB',fps=30,tpad=stop_mode=clone:stop_duration=1,trim=end_frame={row['duration']*30},setpts=N/(30*TB),drawbox=x=0:y=968:w=1920:h=112:color=0x061d33:t=fill,ass=filename={ROOT}/audio/{k}.ass:fontsdir=/System/Library/Fonts/Supplemental,format=yuv420p"
 (ROOT/'source'/(k+'.filter')).write_text(vf+'\n')
 cmd=[FF,'-y','-hide_banner','-v','warning','-threads','2','-i',str(ROOT/'assets/picture'/(k+'.mp4')),'-filter_threads','2','-filter_script:v',str(ROOT/'source'/(k+'.filter')),'-an','-frames:v',str(row['duration']*30),'-r','30','-c:v','libx264','-preset','fast','-crf','17','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360',str(ROOT/'clips'/(k+'.mp4'))]
 (ROOT/'source'/(k+'-command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
 with (ROOT/'qa'/(k+'-render.log')).open('w') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True,timeout=300)
 return k
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for k in ex.map(render,newrows):print('Rendered '+k,flush=True)
(ROOT/'clips/concat.txt').write_text(''.join("file '"+str(ROOT/'clips'/(r['id']+'.mp4'))+"'\n" for r in newrows))
cmd=[FF,'-y','-v','warning','-f','concat','-safe','0','-i',str(ROOT/'clips/concat.txt'),'-i',str(ROOT/'audio/narration-human.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',str(base),'-movflags','+faststart',str(ROOT/'export/architecture-governance-copilot-v2-human-voice.mp4')]
(ROOT/'source/final-command.json').write_text(json.dumps(cmd,indent=2)+'\n');run(cmd)
print('Human-voice export complete:',base,'seconds.',flush=True)

from pathlib import Path
import subprocess,re,json,textwrap
FF='/Users/wantedtina/.cache/uv/archive-v0/UrHfmy6kUrGrSBmd/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
def duration(p):
 r=subprocess.run([FF,'-hide_banner','-i',str(p)],capture_output=True,text=True).stderr;m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',r);return int(m[1])*3600+int(m[2])*60+float(m[3])
def stamp(n):
 ms=round(n*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
rows=json.loads(Path('story.json').read_text());base=0;subs=[];records=[]
for row in rows:
 ds=[];sources=[]
 for i,sentence in enumerate(row['sentences']):
  p=Path('audio')/f"{row['id']}-{i}.aiff";txt=p.with_suffix('.txt');speech=sentence.replace('SKE','S K E').replace('COP','C O P').replace('SI ','S I ').replace('JSON','Jay son');txt.write_text(speech)
  if not p.exists():subprocess.run(['say','-v','Daniel','-r','145','-f',str(txt),'-o',str(p)],check=True)
  sources.append(p);ds.append(duration(p))
 total=sum(ds);available=row['duration']-.7;tempo=max(.90,total/available);scaled=[d/tempo for d in ds]
 filters=[];args=[FF,'-y','-loglevel','error']
 for p in sources:args+=['-i',str(p)]
 filters.append(''.join(f'[{i}:a]' for i in range(len(sources)))+f"concat=n={len(sources)}:v=0:a=1,atempo={tempo:.8f},adelay=300|300,apad,atrim=duration={row['duration']},aresample=48000,aformat=channel_layouts=stereo[out]")
 args+=['-filter_complex',';'.join(filters),'-map','[out]','-c:a','pcm_s16le',str(Path('audio')/(row['id']+'.wav'))];subprocess.run(args,check=True)
 cursor=base+.30
 for sentence,d in zip(row['sentences'],scaled):
  import math
  words=sentence.split();chunks=[]
  n=max(1,math.ceil(len(words)/17))
  while words:
   take=math.ceil(len(words)/n)
   if n>1:
    candidates=[i for i in range(max(7,take-4),min(len(words)-7,take+3)+1) if words[i-1].endswith(('.',',',';',':'))]
    if candidates:take=min(candidates,key=lambda i:abs(i-take))
    while take>7 and words[take-1].lower() in {'a','an','the','to','of','in','with','and','i'}:take-=1
   chunks.append(' '.join(words[:take]));words=words[take:];n-=1
  count=sum(len(c.split()) for c in chunks)
  for chunk in chunks:
   length=d*len(chunk.split())/count;subs.append((cursor,cursor+length-.04,chunk));cursor+=length
 records.append({'id':row['id'],'start':base,'end':base+row['duration'],'source_speech_duration':total,'tempo':tempo,'spoken_duration':sum(scaled)})
 print(row['id'],'raw',round(total,2),'tempo',round(tempo,3),'target',row['duration'],flush=True);base+=row['duration']
Path('audio/concat.txt').write_text(''.join("file '"+str(Path('audio',row['id']+'.wav').resolve())+"'\n" for row in rows))
subprocess.run([FF,'-y','-loglevel','error','-f','concat','-safe','0','-i','audio/concat.txt','-af','loudnorm=I=-16:TP=-1.5:LRA=11','-ar','48000','-c:a','pcm_s16le','audio/narration-v2.wav'],check=True)
Path('export/architecture-governance-copilot-v2.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n'+ '\n'.join(textwrap.wrap(t,66)) for i,(a,b,t) in enumerate(subs))+'\n')
Path('audio/timing.json').write_text(json.dumps(records,indent=2));Path('audio/subtitles.json').write_text(json.dumps(subs,indent=2));print('Narration ready',base,flush=True)

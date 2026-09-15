"""Preserve source provenance, revise diagram routing, and time accepted narration."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, importlib.metadata, wave
import resvg_py
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import fitz

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'production'
V1=Path('/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2.2')
RAW=Path('/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-v2/clips')
REPO=Path('/Users/wantedtina/Repos/architecture-governance-copilot')
FF='/Users/wantedtina/.cache/uv/archive-v0/UrHfmy6kUrGrSBmd/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
manifest=[]
def copy(src,dest):
    dest=P/'assets'/dest;dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dest)
    sha=hashlib.sha256(src.read_bytes()).hexdigest()
    assert sha==hashlib.sha256(dest.read_bytes()).hexdigest()
    manifest.append({'original':str(src),'copy':str(dest.relative_to(ROOT)),'sha256':sha})
    return dest

def run(cmd):
    return subprocess.run(cmd,check=True,capture_output=True,text=True)
def duration(p):
    out=subprocess.run([FF,'-hide_banner','-i',str(p)],capture_output=True,text=True).stderr
    m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',out)
    return int(m[1])*3600+int(m[2])*60+float(m[3])
def stamp(t,srt=False):
    c=round(t*(1000 if srt else 100));base=1000 if srt else 100
    return f'{c//(3600*base):02}:{c//(60*base)%60:02}:{c//base%60:02}'+((','+f'{c%base:03}') if srt else ('.'+f'{c%base:02}'))
def wrap(t):
    if len(t)<=64:return t
    words=t.split();points=range(1,len(words))
    cut=min(points,key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))))
    return ' '.join(words[:cut])+'\n'+' '.join(words[cut:])

assert subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()=='81835b9ced0c709f4003522557b6423bc4bdaa18'
assert hashlib.sha256((V1/'export/architecture-governance-copilot-v2.2-narrated.mp4').read_bytes()).hexdigest()=='fe52d4bdf9cf42114a77d9646af4a27f2de2bc82108e845491cdc8f89282068a'
rows=json.loads((V1/'story.json').read_text())
oldsubs=json.loads((V1/'audio/subtitles.json').read_text())
oldtimeline=json.loads((V1/'export/edit-timeline.json').read_text())['sections']
for n in ['draft','inputs','human-clean','outputs','delivery','invalidation']:copy(RAW/(n+'.webm'),Path('footage')/(n+'.webm'))
for n in ['process','solution','value']:
    for ext in ['svg','png']:copy(V1/'frames'/(n+'.'+ext),Path('slides')/(n+'.'+ext))
for n in ['opening-title','closing-card']:copy(REPO/'video/assets'/(n+'.png'),Path('slides')/(n+'.png'))
arch=copy(V1/'export/system-architecture.svg',Path('slides/system-architecture-v1.svg')).read_text()
old1='d="M1282,669 H1350 V629 H1404"';new1='d="M1282,650 H1330 V629 H1404"'
old2='d="M1350,669 V725 H1404"';new2='d="M1282,713 H1330 V725 H1404"'
assert old1 in arch and old2 in arch
arch=arch.replace(old1,new1).replace(old2,new2)
(P/'assets/slides/system-architecture.svg').write_text(arch)
(ROOT/'export/system-architecture.svg').write_text(arch)
(ROOT/'export/system-architecture.png').write_bytes(resvg_py.svg_to_bytes(svg_string=arch))
shutil.copy2(ROOT/'export/system-architecture.png',P/'assets/slides/system-architecture.png')
c=canvas.Canvas(str(ROOT/'export/system-architecture.pdf'),pagesize=(960,540))
c.setTitle('Architecture Governance Copilot - System Architecture');c.setAuthor('Two Tokens One Brain')
c.drawImage(ImageReader(str(ROOT/'export/system-architecture.png')),0,0,960,540);c.showPage();c.save()
d=fitz.open(ROOT/'export/system-architecture.pdf');d[0].get_pixmap(matrix=fitz.Matrix(2,2)).save(P/'qa/architecture-pdf.png')
shutil.copy2(V1/'export/FORM_TEXT.md',ROOT/'export/FORM_TEXT.md')
for n in ['process','solution']:
    for ext in ['png','svg']:shutil.copy2(P/'assets/slides'/(n+'.'+ext),ROOT/'export'/(n+'.'+ext))

# Preserve every spoken word. Give the feedback/closing one additional second each,
# taken from the static solution section. Do not slow the Daniel source recordings.
changes={'solution':18,'value':9,'close':10}
timeline=[];allsubs=[];base=0
for row,oldrow in zip(rows,oldtimeline):
    key=row['id'];D=changes.get(key,row['duration']);row['duration']=D
    selected=[t for a,b,t in oldsubs if oldrow['start']<=a<oldrow['end']]
    assert ' '.join(selected)==' '.join(row['sentences'])
    clips=[];lengths=[]
    for i,sentence in enumerate(row['sentences']):
        source=copy(V1/'audio'/f'{key}-{i}.aiff',Path('voice')/f'{key}-{i}.aiff')
        copy(V1/'audio'/f'{key}-{i}.txt',Path('voice')/f'{key}-{i}.txt')
        clips.append(source);lengths.append(duration(source))
    tempo=max(1.0,sum(lengths)/(D-.60-.18*(len(clips)-1)))
    spoken=[x/tempo for x in lengths]
    extra=D-.30-sum(spoken)
    gap=extra/(len(clips)) if len(clips)>1 else 0
    cursor=.30;groups=[];subs=[];remain=selected[:]
    pcm=bytearray(D*48000*4)
    for i,(path,sentence,raw,spokenD) in enumerate(zip(clips,row['sentences'],lengths,spoken)):
        chunks=[];used=''
        while used!=sentence:
            chunk=remain.pop(0);chunks.append(chunk);used=' '.join(chunks)
            assert sentence.startswith(used),(key,i,used,sentence)
        # Candidate cue boundaries are snapped to nearby measured pauses where present.
        detector=subprocess.run([FF,'-hide_banner','-i',str(path),'-af',f'atempo={tempo:.9f},silencedetect=noise=-35dB:d=0.10','-f','null','-'],capture_output=True,text=True).stderr
        silence_starts=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',detector)]
        silence_ends=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',detector)]
        pauses=[(a+b)/2 for a,b in zip(silence_starts,silence_ends) if .2<a<b<spokenD-.2]
        bounds=[0];weight=sum(len(x.split()) for x in chunks);acc=0
        for chunk in chunks[:-1]:
            acc+=len(chunk.split());estimate=spokenD*acc/weight
            candidates=[x for x in pauses if abs(x-estimate)<.40 and x>bounds[-1]+1.0]
            bounds.append(min(candidates,key=lambda x:abs(x-estimate)) if candidates else estimate)
        bounds.append(spokenD)
        for j,chunk in enumerate(chunks):subs.append([cursor+bounds[j],cursor+bounds[j+1]-.04,chunk])
        speech_pcm=subprocess.run([FF,'-v','error','-i',str(path),'-af',f'atempo={tempo:.9f}','-ar','48000','-ac','2','-f','s16le','-'],check=True,capture_output=True,timeout=20).stdout
        start_sample=round(cursor*48000)*4
        assert start_sample+len(speech_pcm)<=len(pcm),(key,'audio exceeds section')
        pcm[start_sample:start_sample+len(speech_pcm)]=speech_pcm
        groups.append({'index':i,'text':sentence,'start':round(cursor,4),'end':round(cursor+spokenD,4),'source_duration':raw,'tempo':tempo,'measured_pause_candidates':pauses})
        cursor+=spokenD+gap
    assert not remain
    with wave.open(str(P/'audio'/(key+'.wav')),'wb') as wav:
        wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(48000);wav.writeframes(pcm)
    print('Audio ready:',key,flush=True)
    record={'id':key,'title':row['title'],'start':base,'end':base+D,'duration':D,'tempo':tempo,'speech':groups,'captions':subs}
    timeline.append(record);allsubs.extend([[base+a,base+b,t] for a,b,t in subs]);base+=D
assert base==238
(P/'audio/concat.txt').write_text(''.join("file '"+str(P/'audio'/(r['id']+'.wav'))+"'\n" for r in rows))
run([FF,'-y','-v','error','-f','concat','-safe','0','-i',str(P/'audio/concat.txt'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11','-ar','48000','-c:a','pcm_s16le',str(P/'audio/narration-v2.wav')])
header='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,34,&H00FFFFFF,&H00FFFFFF,&H00061D33,&H00061D33,0,0,0,0,100,100,0,0,1,0,0,2,100,100,24,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
for row in timeline:
    ass=header
    for a,b,t in row['captions']:ass+=f'Dialogue: 0,{stamp(a)},{stamp(b)},Default,,0,0,0,,'+wrap(t).replace('\n','\\N')+'\n'
    (P/'audio'/(row['id']+'.ass')).write_text(ass)
(ROOT/'export/architecture-governance-copilot-v2.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a,True)} --> {stamp(b,True)}\n'+wrap(t) for i,(a,b,t) in enumerate(allsubs))+'\n')
(P/'source/timeline.json').write_text(json.dumps(timeline,indent=2)+'\n')
(P/'source/story.json').write_text(json.dumps(rows,indent=2)+'\n')
(P/'source/asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(P/'source/runtime.json').write_text(json.dumps({'ffmpeg':FF,'packages':{n:importlib.metadata.version(n) for n in ['resvg-py','pymupdf','reportlab']},'application_commit':'81835b9ced0c709f4003522557b6423bc4bdaa18','renderer':'FFmpeg; no Remotion SDK installed or invoked'},indent=2)+'\n')
print(json.dumps([{'id':r['id'],'start':r['start'],'end':r['end'],'tempo':round(r['tempo'],3),'speech':[(g['start'],g['end']) for g in r['speech']]} for r in timeline],indent=2))

from pathlib import Path
import json,subprocess,hashlib,re,wave,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'production'
ff=json.loads((P/'source/runtime.json').read_text())['ffmpeg'];video=ROOT/'export/architecture-governance-copilot-v2-narrated.mp4'
meta=subprocess.run([ff,'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
(P/'qa/video-metadata.txt').write_text(meta)
assert '00:03:58.00' in meta and '1920x1080' in meta and '30 fps' in meta and 'Video: h264' in meta and 'Audio: aac' in meta
r=subprocess.run([ff,'-v','error','-i',str(video),'-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True,timeout=90)
assert not r.stderr.strip(),r.stderr
frames=re.findall(r'frame=(\d+)',r.stdout);assert frames and int(frames[-1])==7140,frames
(P/'qa/decode.txt').write_text(r.stdout+r.stderr)
rows=json.loads((P/'source/timeline.json').read_text());manifest=json.loads((P/'source/asset-manifest.json').read_text())
for entry in manifest:
    assert hashlib.sha256((ROOT/entry['copy']).read_bytes()).hexdigest()==entry['sha256']
    assert hashlib.sha256(Path(entry['original']).read_bytes()).hexdigest()==entry['sha256']
oldstory=json.loads(Path('/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/2026-09-14-v2.2/story.json').read_text())
newstory=json.loads((P/'source/story.json').read_text())
assert [s['sentences'] for s in oldstory]==[s['sentences'] for s in newstory]
assert [s['id'] for s in oldstory]==[s['id'] for s in newstory]
allsubs=[]
for row,story in zip(rows,newstory):
    assert ' '.join(t for a,b,t in row['captions'])==' '.join(story['sentences'])
    for a,b,t in row['captions']:
        assert 0<=a<b<=row['duration']
        allsubs.append((row['start']+a,row['start']+b,t))
assert all(allsubs[i][0]>=allsubs[i-1][1] for i in range(1,len(allsubs)))
with wave.open(str(P/'audio/narration-v2.wav')) as wav:
    assert wav.getnchannels()==2 and wav.getframerate()==48000 and wav.getnframes()==238*48000
oldsvg=ET.parse(P/'assets/slides/system-architecture-v1.svg');newsvg=ET.parse(ROOT/'export/system-architecture.svg')
assert list(oldsvg.getroot().itertext())==list(newsvg.getroot().itertext())
assert (ROOT/'export/FORM_TEXT.md').read_bytes()==Path('/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/2026-09-14-v2.2/export/FORM_TEXT.md').read_bytes()
result={'duration_seconds':238,'video_frames':7140,'resolution':'1920x1080','fps':30,'full_decode':'pass','caption_count':len(allsubs),'caption_overlaps':0,'spoken_words_unchanged':True,'section_order_unchanged':True,'architecture_text_unchanged':True,'source_files_verified':len(manifest),'captured_new_application_footage':False,'human_voice_replacement':'pending user recording','v1_sha256':hashlib.sha256(Path('/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/2026-09-14-v2.2/export/architecture-governance-copilot-v2.2-narrated.mp4').read_bytes()).hexdigest(),'video_bytes':video.stat().st_size}
assert result['v1_sha256']=='fe52d4bdf9cf42114a77d9646af4a27f2de2bc82108e845491cdc8f89282068a'
(P/'qa/verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

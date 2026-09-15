from pathlib import Path
import json,hashlib,subprocess,re,wave
R=Path(__file__).resolve().parents[1];FF=json.loads((R/'source/v2-runtime.json').read_text())['ffmpeg'];v=R/'export/architecture-governance-copilot-v2-human-voice.mp4'
rows=json.loads((R/'source/timeline.json').read_text());D=rows[-1]['end'];old=json.loads((R/'source/v2-story.json').read_text());new=json.loads((R/'source/story.json').read_text())
meta=subprocess.run([FF,'-hide_banner','-i',str(v)],capture_output=True,text=True).stderr
(R/'qa/metadata.txt').write_text(meta)
assert '00:03:39.00' in meta and '1920x1080' in meta and '30 fps' in meta and 'Video: h264' in meta and 'Audio: aac' in meta
rr=subprocess.run([FF,'-v','error','-i',str(v),'-progress','pipe:1','-f','null','-'],check=True,capture_output=True,text=True,timeout=90)
assert not rr.stderr.strip();assert int(re.findall(r'frame=(\d+)',rr.stdout)[-1])==D*30
(R/'qa/full-decode.txt').write_text(rr.stdout)
for entry in json.loads((R/'source/INPUT_MANIFEST.json').read_text()):
 assert hashlib.sha256(Path(entry['source']).read_bytes()).hexdigest()==entry['sha256']
 if 'copy' in entry:assert hashlib.sha256((R/entry['copy']).read_bytes()).hexdigest()==entry['sha256']
for entry in json.loads((R/'source/PICTURE_MANIFEST.json').read_text()):
 assert hashlib.sha256(Path(entry['original']).read_bytes()).hexdigest()==entry['sha256']==hashlib.sha256((R/entry['copy']).read_bytes()).hexdigest()
removed="That's our response to the feedback."
assert removed not in (R/'export/architecture-governance-copilot-v2-human-voice.srt').read_text()
assert removed not in (R/'export/NARRATION_HUMAN_VOICE.md').read_text()
for a,b,r in zip(old,new,rows):
 expected=[s.replace(' '+removed,'') for s in a['sentences']] if a['id']=='value' else a['sentences']
 assert expected==b['sentences'];assert ' '.join(t for _,_,t in r['captions'])==' '.join(expected)
 assert r['audio_speed']==1
 with wave.open(str(R/'audio'/(r['id']+'.wav'))) as w:assert w.getnframes()==r['duration']*48000
caps=json.loads((R/'source/captions.json').read_text())
assert all(0<=c['startMs']<c['endMs']<=D*1000 for c in caps)
assert all(a['endMs']<=b['startMs'] for a,b in zip(caps,caps[1:]))
with wave.open(str(R/'audio/narration-human.wav')) as w:assert w.getnframes()==D*48000
loud=subprocess.run([FF,'-hide_banner','-i',str(v),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
(R/'qa/final-audio-loudness.txt').write_text(loud.stderr)
summary=loud.stderr[loud.stderr.rfind('Summary:'):]
result={'duration_seconds':D,'frame_count':D*30,'format':'1920x1080, 30 fps, H.264/AAC','full_decode':'pass','human_voice_segments':12,'audio_speed':1.0,'time_stretch_applied':False,'captions':len(caps),'caption_overlaps':0,'requested_sentence_removed':True,'other_script_words_unchanged':True,'source_recordings_unchanged':True,'v2_video_and_source_clips_unchanged':True,'video_bytes':v.stat().st_size,'video_sha256':hashlib.sha256(v.read_bytes()).hexdigest(),'audio_loudness_summary':summary}
(R/'qa/verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

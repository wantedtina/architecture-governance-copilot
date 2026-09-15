from pathlib import Path
import subprocess,json,hashlib
ff='/Users/wantedtina/.cache/uv/archive-v0/UrHfmy6kUrGrSBmd/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
p=Path('export/architecture-governance-copilot-v2.2-narrated.mp4')
r=subprocess.run([ff,'-hide_banner','-i',str(p),'-f','null','-'],capture_output=True,text=True,check=True);Path('qa/final-decode.txt').write_text(r.stderr)
assert 'Duration: 00:03:58.00' in r.stderr
subs=json.loads(Path('audio/subtitles.json').read_text());last=0
for a,b,t in subs:assert last<=a<b<=238;last=b
srt=Path('export/architecture-governance-copilot-v2.2.srt').read_text().strip().split('\n\n');assert len(srt)==len(subs)==48 and all(len(b.splitlines())<=4 for b in srt)
for t in [1,6,92]:subprocess.run([ff,'-y','-loglevel','error','-ss',str(t),'-i',str(p),'-frames:v','1',f'qa/final-{t}.png'],check=True)
assert Path('export/FORM_TEXT.md').read_bytes()==Path('/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/2026-09-14-v2.1/export/FORM_TEXT.md').read_bytes()
f=Path('export/README.md');f.write_text(f.read_text()+f'''\n## Verification\n\n- The final export decodes in full: 238.00 seconds, 1080p, 30 fps.\n- Video size: {p.stat().st_size:,} bytes.\n- All 48 captions are ordered, within the video duration, and at most two lines.\n- Six-second interval contact sheets cover the full sequence. Full-size slide and demo samples\n  were inspected; final opening and drafting subtitle regrouping received separate checks.\n- The architecture PDF was rendered back to PNG and visually inspected.\n- Approved form text matches v2.1 byte-for-byte. The original checkout is clean at the locked\n  commit and the historical submission tag is unchanged.\n''')
Path('export/SHA256SUMS.txt').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in sorted(Path('export').iterdir()) if f.is_file() and f.name!='SHA256SUMS.txt'))
print('Final decode/captions/form checks passed:',p.stat().st_size,'bytes; 238 seconds; 48 captions.')

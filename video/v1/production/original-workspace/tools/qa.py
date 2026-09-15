from pathlib import Path
import subprocess,json,re
from PIL import Image,ImageDraw
ff='/Users/wantedtina/.cache/uv/archive-v0/UrHfmy6kUrGrSBmd/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
p=Path('export/architecture-governance-copilot-v2.2-narrated.mp4')
r=subprocess.run([ff,'-hide_banner','-i',str(p),'-f','null','-'],capture_output=True,text=True,check=True);Path('qa/decode.txt').write_text(r.stderr)
assert 'Duration: 00:03:58.00' in r.stderr and re.search(r'frame=\s*7140',r.stderr)
subprocess.run([ff,'-y','-loglevel','error','-i',str(p),'-vf','fps=1/6,scale=480:270','qa/six-%02d.png'],check=True)
files=sorted(Path('qa').glob('six-*.png'))
for start in range(0,len(files),20):
 group=files[start:start+20];sheet=Image.new('RGB',(1920,((len(group)+3)//4)*300),'#061d33');draw=ImageDraw.Draw(sheet)
 for i,f in enumerate(group):
  x=i%4*480;y=i//4*300;sheet.paste(Image.open(f),(x,y));draw.text((x+8,y+274),str((start+i)*6+3)+' s',fill='white')
 sheet.save(f'qa/contact-{start//20+1}.jpg')
for t in [2,17,40,59,131,190,211,234]:
 subprocess.run([ff,'-y','-loglevel','error','-ss',str(t),'-i',str(p),'-frames:v','1',f'qa/full-{t}.png'],check=True)
subs=json.loads(Path('audio/subtitles.json').read_text());last=0
for a,b,t in subs:assert last<=a<b<=238;last=b
srt=Path('export/architecture-governance-copilot-v2.2.srt').read_text().strip().split('\n\n')
assert len(srt)==len(subs) and all(len(b.splitlines())<=4 for b in srt)
print('Decode: 238 seconds / 7140 frames. Captions:',len(subs),'Video bytes:',p.stat().st_size)

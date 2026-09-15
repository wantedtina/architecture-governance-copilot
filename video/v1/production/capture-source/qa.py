from pathlib import Path
import subprocess,json,re,hashlib
from PIL import Image,ImageDraw
FF='/Users/wantedtina/.cache/uv/archive-v0/UrHfmy6kUrGrSBmd/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1';p=Path('export/architecture-governance-copilot-v2-narrated.mp4')
info=subprocess.run([FF,'-hide_banner','-i',str(p)],capture_output=True,text=True).stderr;print(info)
subprocess.run([FF,'-v','error','-i',str(p),'-f','null','-'],check=True);print('Full A/V decode passed')
volume=subprocess.run([FF,'-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
Path('audio/export-loudness.txt').write_text(volume);print(volume[volume.rfind('{'):])
marks=list(range(2,238,4));frames=Path('frames/qa');frames.mkdir(exist_ok=True)
for t in marks:subprocess.run([FF,'-y','-loglevel','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=640:360',str(frames/f'{t:03}.png')],check=True)
for part in range((len(marks)+11)//12):
 ts=marks[part*12:part*12+12];im=Image.new('RGB',(1920,390*4),'#061d33');d=ImageDraw.Draw(im)
 for i,t in enumerate(ts):x=i%3*640;y=i//3*390;im.paste(Image.open(frames/f'{t:03}.png'),(x,y));d.text((x+10,y+363),f'{t//60:02}:{t%60:02}',fill='white')
 im.save(f'frames/final-sheet-{part}.jpg')
for t in [5,57,68,84,94,125,136,159,190,201,215,226,234]:subprocess.run([FF,'-y','-loglevel','error','-ss',str(t),'-i',str(p),'-frames:v','1',f'frames/full-{t}.png'],check=True)
assert hashlib.sha256(Path('export/FORM_TEXT.md').read_bytes()).hexdigest()==hashlib.sha256(Path('/Users/wantedtina/Deliverables/architecture-governance-copilot/2026-09-14-draft/review-copy/FORM_TEXT.md').read_bytes()).hexdigest()
print('Approved form unchanged. Video bytes',p.stat().st_size)

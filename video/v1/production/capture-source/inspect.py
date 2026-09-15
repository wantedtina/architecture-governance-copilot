from pathlib import Path
import subprocess,re,json
from PIL import Image,ImageDraw
FF='/Users/wantedtina/.cache/uv/archive-v0/UrHfmy6kUrGrSBmd/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1';records={}
for p in Path('clips').glob('*.webm'):
 r=subprocess.run([FF,'-hide_banner','-i',str(p)],capture_output=True,text=True).stderr;m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',r)
 if not m:continue
 dur=int(m[1])*3600+int(m[2])*60+float(m[3]);records[p.stem]=dur
 folder=Path('frames')/p.stem;folder.mkdir(exist_ok=True)
 subprocess.run([FF,'-y','-loglevel','error','-i',str(p),'-vf','fps=1/3,scale=480:270',str(folder/'%03d.png')],check=True)
 fs=sorted(folder.glob('*.png'));im=Image.new('RGB',(1440,300*((len(fs)+2)//3)),'#061d33');d=ImageDraw.Draw(im)
 for i,f in enumerate(fs):
  x=i%3*480;y=i//3*300;im.paste(Image.open(f),(x,y));d.text((x+8,y+273),f'{p.stem} {i*3+1.5}s',fill='white')
 im.save(Path('frames')/(p.stem+'-sheet.jpg'))
Path('clips/durations.json').write_text(json.dumps(records));print(records)

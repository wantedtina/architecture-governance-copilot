"""Render owned V2 segments once from immutable copied sources, then stream-copy join."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import subprocess,json,sys
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'production'
FF=json.loads((P/'source/runtime.json').read_text())['ffmpeg']
rows=json.loads((P/'source/timeline.json').read_text())
# source_start, source_end, output_end. The output start is the previous output end.
EDL={
'draft':[(0,5.65,10.4),(5.65,14.8,17.3),(14.8,18.0,20.5),(18,19.7,24.2),(19.7,22,27)],
'inputs':[(0,4.2,4),(4.2,7.8,8.4),(7.8,11.7,12.2),(11.7,15,15.3),(15,18.9,19)],
'human':[(0,3.45,6.2),(3.45,7.75,11.3),(7.75,9.6,16.6),(9.6,12.6,19.5),(12.6,16.9,24.5),(16.9,17.5,28.1),(17.5,20.5,31.7),(20.5,22.8,33)],
'outputs':[(.8,3.6,5.5),(3.6,8.9,14.4),(8.9,12.5,21.5),(12.5,14.5,23)],
'delivery':[(0,4.8,4.7),(4.8,7.8,10.5),(7.8,12.3,14.5),(12.3,14.85,17.2),(14.85,16.9,19.45),(16.9,19,22.3),(19,24.5,29)],
'invalidation':[(0,5.4,3.1),(5.4,9.2,7.3),(9.2,16.3,19)]}
static={'title':'opening-title','process':'process','solution':'solution','architecture':'system-architecture','value':'value','close':'closing-card'}
# Focus outlines use source coordinates, with the full slide/UI retained underneath.
FOCUS={
'process':[(.5,4.2,88,298,554,198),(4.2,6.6,683,298,554,198),(6.6,9.2,1278,298,554,198),(9.5,14.7,88,543,1744,198),(14.7,17.6,88,820,1744,129)],
'solution':[(.4,3.0,87,335,1745,441),(3.0,6.9,87,809,1745,148),(7.6,11.3,653,335,1080,168),(11.3,17.2,87,809,1745,148)],
'architecture':[(.3,6.6,52,333,266,150),(.3,6.6,52,507,266,150),(6.8,9.0,382,337,261,225),(9,12.2,742,337,251,458),(12.2,16.5,1027,330,806,441),(16.75,19.45,52,626,591,158),(19.45,22.5,1357,847,506,153)],
'human':[(11.7,14.2,412,464,1080,59),(14.2,16.0,394,83,670,42)],
'outputs':[(6.0,8.5,394,383,537,211),(8.5,10.25,967,300,546,117),(10.25,12.2,967,431,546,276)],
}
(P/'source/edit-list.json').write_text(json.dumps({'frame_rate':30,'sections':EDL,'focus_regions':FOCUS},indent=2)+'\n')

def produce(row):
    key=row['id'];D=row['duration'];cmd=[FF,'-y','-hide_banner','-loglevel','warning','-threads','2'];chain=[]
    if key in static:
        cmd+=['-loop','1','-framerate','30','-i',str(P/'assets/slides'/(static[key]+'.png'))]
        chain.append('[0:v]scale=1840:1035:flags=lanczos,pad=1920:1080:40:0:color=0x061d33,setsar=1[base]')
        scale=1840/1920;offset=40
    else:
        src='human-clean' if key=='human' else key
        cmd+=['-i',str(P/'assets/footage'/(src+'.webm'))]
        parts=EDL[key];chain.append('[0:v]split='+str(len(parts))+''.join(f'[s{i}]' for i in range(len(parts))))
        prev=0;shotmeta=[]
        for i,(a,b,end) in enumerate(parts):
            endframe=round(end*30);startframe=round(prev*30);N=endframe-startframe;outD=N/30
            chain.append(f'[s{i}]trim=start={a}:end={b},setpts=(PTS-STARTPTS)*{outD/(b-a):.10f},fps=30,tpad=stop_mode=clone:stop_duration=1,trim=end_frame={N},setpts=N/(30*TB)[p{i}]')
            shotmeta.append({'source_start':a,'source_end':b,'output_start_frame':startframe,'output_end_frame':endframe});prev=end
        assert round(prev*30)==D*30
        chain.append(''.join(f'[p{i}]' for i in range(len(parts)))+f'concat=n={len(parts)}:v=1:a=0,scale=1680:945:flags=lanczos,pad=1920:1080:120:0:color=0x061d33,setsar=1[base]')
        scale=1680/1600;offset=120
    vf=[]
    for a,b,x,y,w,h in FOCUS.get(key,[]):
        color='0x23a9eb@0.85' if key not in ['architecture'] else '0x7ee650@0.9'
        vf.append(f"drawbox=x={round(offset+x*scale)}:y={round(y*scale)}:w={round(w*scale)}:h={round(h*scale)}:color={color}:t=3:enable='between(t,{a},{b})'")
    vf+=['drawbox=x=0:y=968:w=1920:h=112:color=0x061d33:t=fill',f'ass=filename={P}/audio/{key}.ass:fontsdir=/System/Library/Fonts/Supplemental','format=yuv420p']
    chain.append('[base]'+','.join(vf)+'[out]')
    script=P/'source'/(key+'.fffilter');script.write_text(';\n'.join(chain)+'\n')
    target=P/'clips'/(key+'.mp4')
    cmd+=['-filter_complex_threads','2','-filter_complex_script',str(script),'-map','[out]','-an','-frames:v',str(D*30),'-r','30','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360',str(target)]
    (P/'source'/(key+'-command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
    with (P/'qa'/(key+'-render.log')).open('w') as log:
        subprocess.run(cmd,stdout=log,stderr=log,check=True,timeout=300)
    return key

selected=set(sys.argv[1:])
todo=[r for r in rows if not selected or r['id'] in selected]
with ThreadPoolExecutor(max_workers=3) as executor:
    futures=[executor.submit(produce,r) for r in todo]
    for f in as_completed(futures):print('Rendered:',f.result(),flush=True)
if all((P/'clips'/(r['id']+'.mp4')).is_file() for r in rows):
    (P/'clips/concat.txt').write_text(''.join("file '"+str(P/'clips'/(r['id']+'.mp4'))+"'\n" for r in rows))
    cmd=[FF,'-y','-v','warning','-f','concat','-safe','0','-i',str(P/'clips/concat.txt'),'-i',str(P/'audio/narration-v2.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','238','-movflags','+faststart',str(ROOT/'export/architecture-governance-copilot-v2-narrated.mp4')]
    (P/'source/final-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
    result=subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=120)
    (P/'qa/final-mux.log').write_text(result.stderr)
    print('Final V2 export complete.',flush=True)

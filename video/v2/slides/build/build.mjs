import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=path.resolve('..'), build=path.join(root,'build'), base='/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals';
const p=Presentation.create({slideSize:{width:1920,height:1080}});
const inputs=JSON.parse(await fs.readFile('slides.json','utf8'));
const story=JSON.parse(await fs.readFile(base+'/tool-assisted-v2-human-voice/source/story.json','utf8'));
const col=v=>!v||v==='none'?'none':/^#[0-9a-f]{3}$/i.test(v)?'#'+v.slice(1).split('').map(c=>c+c).join(''):v;
const line=a=>({fill:col(a.stroke),width:Number(a['stroke-width']||0),style:a['stroke-dasharray']?'dashed':'solid'});
function poly(s,points,fill,stroke,closed=false){
 const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]),x=Math.min(...xs),y=Math.min(...ys),w=Math.max(1,Math.max(...xs)-x),h=Math.max(1,Math.max(...ys)-y);
 const commands=points.map((pt,i)=>({[i?'lineTo':'moveTo']:{x:pt[0]-x,y:pt[1]-y}}));if(closed)commands.push({close:{}});
 s.shapes.add({geometry:'custom',position:{left:x,top:y,width:w,height:h},fill,line:stroke,customPaths:[{width:w,height:h,commands}]});
}
function parse(d){const t=d.match(/[A-Za-z]|[-+]?(?:\d*\.)?\d+/g);let i=0,x=0,y=0,cmd='',pts=[],closed=false;const num=()=>Number(t[i++]);
 while(i<t.length){if(/[A-Za-z]/.test(t[i]))cmd=t[i++];if(cmd==='M'||cmd==='L'){x=num();y=num();pts.push([x,y]);}else if(cmd==='H'){x=num();pts.push([x,y]);}else if(cmd==='V'){y=num();pts.push([x,y]);}else if(cmd==='C'){let x0=x,y0=y,x1=num(),y1=num(),x2=num(),y2=num(),x3=num(),y3=num();for(let n=1;n<=32;n++){let v=n/32,u=1-v;pts.push([u*u*u*x0+3*u*u*v*x1+3*u*v*v*x2+v*v*v*x3,u*u*u*y0+3*u*u*v*y1+3*u*v*v*y2+v*v*v*y3]);}x=x3;y=y3;}else if(cmd==='Z'){closed=true;break;}else throw Error(cmd);}return {pts,closed};}
function arrow(s,tip,prev,a){let dx=tip[0]-prev[0],dy=tip[1]-prev[1],len=Math.hypot(dx,dy);dx/=len;dy/=len;let u=Number(a['stroke-width']||2.5),back=[tip[0]-dx*7*u,tip[1]-dy*7*u];poly(s,[[back[0]-dy*4*u,back[1]+dx*4*u],[tip[0]+dx*u,tip[1]+dy*u],[back[0]+dy*4*u,back[1]-dx*4*u]],'none',{fill:col(a.stroke),width:1.4*u,style:'solid'});}
async function imageSlide(file,key){const s=p.slides.add();s.images.add({blob:new Uint8Array(await fs.readFile(file)),contentType:'image/png',alt:story.find(r=>r.id===key).title,fit:'contain',position:{left:0,top:0,width:1920,height:1080}});s.speakerNotes.textFrame.setText(story.find(r=>r.id===key).sentences.join('\n\n'));}
await imageSlide(base+'/tool-assisted-v2/production/assets/slides/opening-title.png','title');
for(const inp of inputs){const s=p.slides.add();s.background.fill='#061D33';
 for(const e of inp.elements){const a=e.a;
 if(e.tag==='rect')s.shapes.add({geometry:'rect',position:{left:Number(a.x||0),top:Number(a.y||0),width:Number(a.width),height:Number(a.height)},fill:col(a.fill),line:line(a),...(a.rx?{borderRadius:Number(a.rx)}:{})});
 else if(e.tag==='ellipse')s.shapes.add({geometry:'ellipse',position:{left:Number(a.cx)-Number(a.rx),top:Number(a.cy)-Number(a.ry),width:Number(a.rx)*2,height:Number(a.ry)*2},fill:col(a.fill),line:line(a)});
 else if(e.tag==='text'){let f=Number(a['font-size']),x=Number(a.x),y=Number(a.y);const sh=s.shapes.add({name:e.text,geometry:'textbox',position:{left:x,top:y-f*.905,width:1910-x,height:f*1.3},fill:'none',line:{fill:'none',width:0}});sh.text=e.text;sh.text.style={typeface:'Arial',fontSize:f,bold:Number(a['font-weight']||400)>=600,color:col(a.fill),wrap:'none',autoFit:'none',verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0}};}
 else if(e.tag==='path'){const {pts,closed}=parse(a.d);poly(s,pts,col(a.fill),line(a),closed);if(a['marker-end'])arrow(s,pts.at(-1),pts.at(-2),a);if(a['marker-start'])arrow(s,pts[0],pts[1],a);}
 }const key=inp.name==='system-architecture'?'architecture':inp.name;s.speakerNotes.textFrame.setText(story.find(r=>r.id===key).sentences.join('\n\n'));
}
await imageSlide(base+'/tool-assisted-v2/production/assets/slides/closing-card.png','close');
await (await PresentationFile.exportPptx(p)).save(path.join(build,'candidate.pptx'));
for(let i=0;i<p.slides.items.length;i++){let png=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));}
console.log('Six-slide draft exported.');

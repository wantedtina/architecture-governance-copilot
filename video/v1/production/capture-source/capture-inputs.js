async page => {
const pause=ms=>page.waitForTimeout(ms);
const focus=async l=>{await l.evaluate(el=>el.scrollIntoView({block:'center',behavior:'instant'}));await pause(250);};
const cue=async(l,label)=>{
 await focus(l);const b=await l.boundingBox();await page.mouse.move(b.x+b.width/2,b.y+b.height/2,{steps:12});
 await page.evaluate(({b,label})=>{
  document.getElementById('video-cue')?.remove();document.getElementById('video-cursor')?.remove();
  const ring=document.createElement('div');ring.id='video-cursor';ring.style.cssText=`position:fixed;left:${b.x+b.width/2-17}px;top:${b.y+b.height/2-17}px;width:34px;height:34px;border-radius:50%;background:#FFD60055;border:3px solid #FFB900;pointer-events:none;z-index:2147483647;box-sizing:border-box`;document.body.appendChild(ring);
  const mark=document.createElement('div');mark.id='video-cue';mark.style.cssText=`position:fixed;left:${b.x-5}px;top:${b.y-5}px;width:${b.width+10}px;height:${b.height+10}px;border:3px solid #ff4b4b;border-radius:8px;pointer-events:none;z-index:2147483646;box-sizing:border-box`;
  const badge=document.createElement('div');badge.textContent=label;badge.style.cssText='position:absolute;left:0;bottom:calc(100% + 6px);background:#c92e35;color:white;font:bold 15px Arial;padding:6px 9px;border-radius:4px;white-space:nowrap';mark.appendChild(badge);document.body.appendChild(mark);
 },{b,label});await pause(700);
};
const clear=async()=>page.evaluate(()=>document.getElementById('video-cue')?.remove());
const click=async(l,label)=>{await cue(l,label);await l.click();await pause(650);await clear();};
const button=n=>page.getByRole('button',{name:n,exact:true});
await click(button('article Load fake Confluence SI'),'Load authoritative SI');
await click(button('notes Load synthetic transcript'),'Load imported transcript');
await click(button('dataset Load synthetic metadata'),'Load review metadata');
await click(page.getByRole('tab',{name:'Review transcript',exact:true}),'Inspect transcript');
await pause(900);
await click(button('Confirm review input manifest'),'Confirm exact input package');
await click(button('Analyze with Fake AIF'),'Analyze review evidence');
await pause(1500);

}
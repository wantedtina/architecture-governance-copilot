from pathlib import Path
helper='''async page => {
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
'''
scripts={
'draft':'''await click(button('edit_document Draft a Solution Intent'),'Draft a Solution Intent');
await click(button('Open Demonstration Project'),'Open project context');
await click(button('Add sample evidence'),'Add supporting evidence');
await click(button('Save evidence'),'Save evidence');
await pause(600);
await click(button('Confirm Context & Continue'),'Confirm selected context');
await click(button('Generate SI Draft'),'Generate SI draft');
await pause(900);
await click(button('Confirm SI draft'),'Confirm reviewed draft');
await pause(1800);
await click(button('fact_check Start a separate review'),'Start a separate governance review');
''',
'inputs':'''await click(button('article Load fake Confluence SI'),'Load authoritative SI');
await click(button('notes Load synthetic transcript'),'Load imported transcript');
await click(button('dataset Load synthetic metadata'),'Load review metadata');
await click(page.getByRole('tab',{name:'Review transcript',exact:true}),'Inspect transcript');
await pause(900);
await click(button('Confirm review input manifest'),'Confirm exact input package');
await click(button('Analyze with Fake AIF'),'Analyze review evidence');
await pause(1500);
''',
'human':'''await click(page.getByRole('tab',{name:/Actions ·/}),'Review proposed actions');
const owner=page.getByRole('textbox',{name:'Owner (required for Delivery)',exact:true}).first();
await cue(owner,'Edit owner');await owner.fill('Taylor Kim');await owner.press('Tab');await pause(850);await clear();await focus(owner);await pause(2600);
await click(page.getByRole('tab',{name:/Findings ·/}),'Review findings');
const title=page.getByRole('textbox',{name:'Title',exact:true}).nth(2);await focus(title);await pause(800);
const include=page.getByRole('checkbox',{name:'Include in reviewed record',exact:true}).nth(2);
await cue(include,'Exclude this finding');await include.focus();await include.press('Space');await pause(850);await clear();await focus(title);await pause(1800);
await click(button('Confirm Reviewed Record & Generate Outputs'),'Confirm reviewed record');await pause(1300);
''',
'outputs':'''await focus(page.getByRole('heading',{name:'Human Review Changes',exact:true}));await pause(2500);
await page.getByRole('heading',{name:'Evidence-to-Output Comparison',exact:true}).evaluate(el=>el.scrollIntoView({block:'start'}));await pause(4800);
await focus(page.getByRole('heading',{name:'Actual minutes entry',exact:true}));await pause(2800);
await click(button('send Continue to Work Item Delivery'),'Continue to controlled delivery');await pause(700);
''',
'delivery':'''await focus(page.getByRole('combobox',{name:'Action to deliver',exact:true}));await pause(1100);
await click(button('preview Preview Azure DevOps request'),'Preview the exact request');
await page.getByRole('heading',{name:'Review the prepared request',exact:true}).evaluate(el=>el.scrollIntoView({block:'start'}));await pause(2600);
await click(page.getByRole('tab',{name:'Request JSON',exact:true}),'Inspect request JSON');await pause(900);
await click(page.getByRole('tab',{name:'Work item summary',exact:true}),'Return to readable summary');
await click(button('check_circle Confirm request'),'Confirm this request');await pause(900);
await click(button('send Create work item'),'Create the work item');await pause(1000);
await focus(page.getByRole('heading',{name:'Delivery result',exact:true}));await pause(3400);
''',
'invalidation':'''await click(button('Back to Human Review'),'Return to review');
await click(button('← Back to Review Inputs'),'Return to source inputs');
await click(page.getByRole('tab',{name:'Review transcript',exact:true}),'Update transcript');
const input=page.getByRole('textbox',{name:'User-provided review transcript',exact:true});
await cue(input,'Add new review context');await input.fill((await input.inputValue())+'\\nAdditional context for manual review: support ownership still requires confirmation.');await input.press('Tab');await pause(900);await clear();
await focus(page.getByText('Inputs changed → outputs invalidated.',{exact:false}).first());await pause(3800);
'''}
for name,body in scripts.items():Path(f'tools/capture-{name}.js').write_text(helper+body+'\n}')

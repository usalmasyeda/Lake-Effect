// AI-assisted: written with Claude (an AI assistant). Records the guided website demo video.
const { chromium } = require('playwright');
const OVERLAY = `
window.addEventListener('DOMContentLoaded', () => {
  const c = document.createElement('div'); c.id='fake-cursor';
  c.innerHTML = '<svg width="34" height="40" viewBox="0 0 34 40"><path d="M3 2 L3 32 L11 25 L17 38 L23 35 L17 22 L28 22 Z" fill="#FFFFFF" stroke="#07131F" stroke-width="2.5" stroke-linejoin="round"/></svg>';
  Object.assign(c.style,{position:'fixed',left:'0',top:'0',zIndex:2147483647,pointerEvents:'none',transform:'translate(800px,450px)',filter:'drop-shadow(0 2px 4px rgba(0,0,0,.6))'});
  const r = document.createElement('div'); Object.assign(r.style,{position:'fixed',width:'46px',height:'46px',borderRadius:'50%',border:'4px solid #A8D65C',zIndex:2147483646,pointerEvents:'none',opacity:'0',transition:'opacity .5s, transform .5s'});
  const cap = document.createElement('div'); cap.id='cap';
  Object.assign(cap.style,{position:'fixed',left:'50%',bottom:'34px',transform:'translateX(-50%)',zIndex:2147483645,pointerEvents:'none',background:'rgba(7,19,31,.94)',color:'#EAF4F4',border:'2px solid #A8D65C',padding:'14px 26px',font:'600 30px Inter, system-ui, sans-serif',whiteSpace:'nowrap',opacity:'0',transition:'opacity .3s'});
  document.body.append(cap, r, c);
  document.addEventListener('mousemove', e => { c.style.transform = 'translate(' + (e.clientX-3) + 'px,' + (e.clientY-2) + 'px)'; }, true);
  document.addEventListener('mousedown', e => { r.style.transition='none'; r.style.left=(e.clientX-23)+'px'; r.style.top=(e.clientY-23)+'px'; r.style.opacity='1'; r.style.transform='scale(.4)'; requestAnimationFrame(()=>{ r.style.transition='opacity .6s, transform .6s'; r.style.opacity='0'; r.style.transform='scale(1.3)'; }); }, true);
  window.__cap = t => { cap.style.opacity = t ? '1' : '0'; if (t) cap.innerHTML = t; };
});`;
(async () => { const b = await chromium.launch();
  const ctx = await b.newContext({viewport:{width:1600,height:900}, recordVideo:{dir:'out', size:{width:1600,height:900}}});
  await ctx.addInitScript(OVERLAY);
  const p = await ctx.newPage();
  const t0=Date.now(); const mark=(s)=>console.log(((Date.now()-t0)/1000).toFixed(1), s);
  const cap = t => p.evaluate(t=>window.__cap(t), t);
  const center = async sel => { const bb = await (await p.$(sel)).boundingBox(); return [bb.x+bb.width/2, bb.y+bb.height/2]; };
  const moveTo = async (x,y,steps=22) => { await p.mouse.move(x,y,{steps}); await p.waitForTimeout(150); };
  const clickAt = async (x,y) => { await moveTo(x,y); await p.mouse.down(); await p.mouse.up(); };
  await p.goto('https://usalmasyeda.github.io/Lake-Effect/', {waitUntil:'networkidle'}); await p.waitForTimeout(2500);
  await p.evaluate(()=>window.scrollTo(0,205)); await p.mouse.move(820,520); await p.waitForTimeout(700); mark('start');
  // 1 scanner
  await cap('<span style="color:#A8D65C">1</span> &nbsp;The Trend Scanner ranks what is really changing');
  let [x,y] = await center('.var-btn[data-id="chlorophyll"]'); await clickAt(x,y); await p.waitForTimeout(1600);
  // 2 slider
  await cap('<span style="color:#A8D65C">2</span> &nbsp;Drag the slider to watch the lake change, year by year');
  const sb = await (await p.$('#chlorophyll-year-slider')).boundingBox(); const sy = sb.y+sb.height/2;
  const xAt = v => sb.x + 8 + (v-2003)/(2025-2003)*(sb.width-16);
  await moveTo(xAt(2025), sy); await p.mouse.down();
  for (let v=2025; v>=2003; v-=2) { await p.mouse.move(xAt(v), sy, {steps:4}); await p.waitForTimeout(170); }
  await p.waitForTimeout(400);
  for (let v=2003; v<=2025; v+=2) { await p.mouse.move(xAt(v), sy, {steps:4}); await p.waitForTimeout(150); }
  await p.mouse.move(xAt(2025), sy, {steps:3}); await p.mouse.up(); await p.waitForTimeout(500); mark('slider');
  // 3 trends
  await cap('<span style="color:#A8D65C">3</span> &nbsp;Switch on long-term trends: green = significant increase');
  [x,y] = await center('#trend-map-toggle'); await clickAt(x,y); await p.waitForTimeout(3000);
  // 4 pixel
  await cap('<span style="color:#A8D65C">4</span> &nbsp;Click any square for its change per decade and p-value');
  const mb = await (await p.$('#map')).boundingBox(); await clickAt(mb.x+mb.width*0.5, mb.y+mb.height*0.5); await p.waitForTimeout(2700);
  await p.evaluate(()=>state.map && state.map.closePopup()); mark('pixel');
  // 5 temperature
  await cap('<span style="color:#A8D65C">5</span> &nbsp;Compare water temperature: rising, but not significant yet');
  [x,y] = await center('.var-btn[data-id="temperature"]'); await clickAt(x,y); await p.waitForTimeout(2700);
  // 6 other lake
  await cap('<span style="color:#A8D65C">6</span> &nbsp;Pick any of the five Great Lakes');
  [x,y] = await center('#lake-select'); await clickAt(x,y); await p.waitForTimeout(500);
  await p.selectOption('#lake-select','Lake Huron'); await p.waitForTimeout(4000); mark('huron');
  await ctx.close(); await b.close(); })();

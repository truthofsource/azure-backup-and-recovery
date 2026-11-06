'use strict';
const el = id => document.getElementById(id);
const node = (tag, text, cls) => {const n=document.createElement(tag); n.textContent=text; if(cls)n.className=cls;return n;};
function render(r) {
  document.title=r.title+' | Engineering Labs';
  for(const k of ['title','domain','subtitle','scenario','outcome','boundary'])el(k).textContent=r[k];
  el('metrics').replaceChildren(...r.metrics.map(m=>{const d=node('div','','metric');d.append(node('span',m.label),node('strong',m.value),node('small',m.detail));return d;}));
  el('flow').replaceChildren(...r.flow.map((s,i)=>{const d=node('li','');d.append(node('span',String(i+1).padStart(2,'0'),'step'),node('span',s));return d;}));
  el('summary').replaceChildren(...r.checks.slice(0,4).map(c=>{const d=node('div','','check');d.append(node('span',c.passed?'PASS':'FAIL',c.passed?'badge pass':'badge fail'),node('span',c.name));return d;}));
  el('checks').replaceChildren(...r.checks.map(c=>{const tr=node('tr','');tr.append(node('td',c.name),node('td',c.detail),node('td',c.passed?'PASS':'FAIL',c.passed?'positive':'negative'));return tr;}));
  el('rows').replaceChildren(...r.records.map(row=>{const tr=node('tr','');tr.append(...row.map(v=>node('td',String(v))));return tr;}));
  el('notes').replaceChildren(...r.notes.map(s=>node('li',s)));
  el('time').textContent='Executed '+new Date(r.executedAt).toLocaleString();
}
document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('hidden',t.id!==b.dataset.tab));document.querySelectorAll('.nav').forEach(n=>n.classList.toggle('active',n===b));}));
async function load(run=false){const b=el('run');b.disabled=true;el('error').textContent='';try{const response=await fetch(run?'/api/run':'/api/report',run?{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}:{});if(!response.ok)throw Error('The local demonstration could not complete. Check the CLI output and retry.');render(await response.json());}catch(e){el('error').textContent=e.message;}finally{b.disabled=false;}}
el('run').addEventListener('click',()=>load(true));load();

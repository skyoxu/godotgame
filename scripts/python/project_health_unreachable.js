'use strict';
const el=id=>document.getElementById(id);
let items=[];
function shortName(path){const parts=String(path||'').split('/');return parts[parts.length-1]||String(path||'');}
function render(){
  const filter=el('scene-filter').value;
  const filtered=items.filter(item=>filter==='all'||(filter==='parse-error'&&item.parse_error)||(filter==='with-scripts'&&(item.functional_summary?.scripts||[]).length));
  const list=el('scene-list');list.replaceChildren();
  for(const item of filtered){const card=document.createElement('div');card.className='scene-card scene-unreachable';card.title=item.path;const strong=document.createElement('strong');strong.textContent=shortName(item.path);const p=document.createElement('small');p.textContent=item.description||item.path;card.append(strong,p);if(item.parse_error){const error=document.createElement('p');error.textContent=`parse error: ${item.parse_error}`;card.append(error);}const scripts=item.functional_summary?.scripts||[];if(scripts.length){const script=document.createElement('p');script.textContent=`scripts: ${scripts.join(', ')}`;card.append(script);}list.append(card);}
  el('unreachable-status').textContent=`${filtered.length} of ${items.length} unconfirmed scenes`;
}
async function load(){const response=await fetch('/api/knowledge/godot/unreachable',{cache:'no-store'});const data=await response.json();if(!response.ok)throw new Error(data.reason||`HTTP ${response.status}`);items=data.items||[];render();}
el('scene-filter').addEventListener('change',render);
load().catch(error=>el('unreachable-status').textContent=error.message);

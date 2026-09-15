'use strict';
const el=id=>document.getElementById(id);
let graphState=null;
let sessionToken='';

async function getJson(path){
  const response=await fetch(path,{cache:'no-store'});
  const data=await response.json();
  if(!response.ok) throw new Error(data.reason||`HTTP ${response.status}`);
  return data;
}
async function token(){
  if(sessionToken)return sessionToken;
  sessionToken=(await getJson('/api/knowledge/session')).token;
  return sessionToken;
}
async function rescan(){
  el('scene-status').textContent='Scanning immutable local main…';
  const response=await fetch('/api/knowledge/scan',{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json','X-Project-Health-Token':await token()},body:'{}'});
  const data=await response.json();
  if(!response.ok)throw new Error(data.reason||`HTTP ${response.status}`);
  await loadGraph();
}
function shortName(path){const parts=String(path||'').split('/');return parts[parts.length-1]||String(path||'');}
function nodeClass(path,evidence){
  const node=graphState?.nodes?.[path]||{};
  if(node.classification==='unreachable-candidate' && evidence!=='possible')return 'scene-unreachable';
  return evidence==='possible'?'scene-possible':'scene-effective';
}
function edgeChildren(path){return (graphState?.edges||[]).filter(edge=>edge.source===path && graphState?.nodes?.[edge.target]);}
function showScene(path){
  const node=graphState?.nodes?.[path]; if(!node)return;
  el('scene-preview-title').textContent=shortName(path);
  const body=el('scene-preview-body');body.replaceChildren();
  const dl=document.createElement('dl');dl.className='scene-detail-grid';
  const add=(key,value)=>{const dt=document.createElement('dt');dt.textContent=key;const dd=document.createElement('dd');dd.textContent=String(value??'');dl.append(dt,dd);};
  add('Path',path);add('Classification',node.classification);add('Description',node.description||'');
  add('Scripts',(node.functional_summary?.scripts||[]).join(', '));add('Events',(node.functional_summary?.events||[]).join(', '));add('Routes',(node.functional_summary?.scene_routes||[]).join(', '));add('Config refs',(node.functional_summary?.config_references||[]).join(', '));
  body.append(dl);
  const nodes=document.createElement('details');const ns=document.createElement('summary');ns.textContent=`Scene nodes (${node.nodes?.length||0})`;nodes.append(ns);
  for(const item of node.nodes||[]){const p=document.createElement('p');p.textContent=`${item.parent||'.'}/${item.name||'(unnamed)'} · ${item.type||'inherited'}${item.resources?.length?` · ${item.resources.join(', ')}`:''}`;nodes.append(p);}body.append(nodes);
  const refs=(graphState.code_references||[]).filter(ref=>(node.functional_summary?.scripts||[]).includes(ref.source));
  const evidence=document.createElement('details');const es=document.createElement('summary');es.textContent=`Script evidence (${refs.length})`;evidence.append(es);
  for(const ref of refs){const p=document.createElement('p');p.textContent=`${ref.evidence_level||ref.classification} · ${ref.source}:${ref.line||'?'} → ${ref.target||'(dynamic)'} · ${ref.evidence||''}`;evidence.append(p);}body.append(evidence);
  el('scene-preview').showModal();
}
function renderBranch(path,evidence='effective',stack=new Set()){
  const branch=document.createElement('div');branch.className='scene-map-branch';
  const card=document.createElement('button');card.type='button';card.className=`scene-card ${nodeClass(path,evidence)}`;card.title=path;
  const strong=document.createElement('strong');strong.textContent=shortName(path);const small=document.createElement('small');small.textContent=`${graphState.nodes[path]?.classification||'unknown'} · ${evidence}`;card.append(strong,small);card.onclick=()=>showScene(path);branch.append(card);
  if(stack.has(path)){const cycle=document.createElement('span');cycle.className='scene-cycle';cycle.textContent='cycle';branch.append(cycle);return branch;}
  const nextStack=new Set(stack);nextStack.add(path);const edges=edgeChildren(path);
  if(edges.length){const children=document.createElement('div');children.className='scene-map-children';for(const edge of edges){const row=document.createElement('div');row.className='scene-edge-row';const line=document.createElement('span');line.className='scene-edge-line';const label=document.createElement('span');label.className=`scene-edge-label ${edge.evidence_level==='possible'?'scene-possible':'scene-effective'}`;label.textContent=`${edge.evidence_level||'possible'} · ${edge.kind||'relation'}`;row.append(line,label);children.append(row,renderBranch(edge.target,edge.evidence_level||'possible',nextStack));}branch.append(children);}
  return branch;
}
function render(){
  const box=el('scene-graph');box.replaceChildren();
  const main=graphState?.main_scene;
  if(main && graphState.nodes?.[main])box.append(renderBranch(main));
  else{const p=document.createElement('p');p.textContent='No confirmed main scene. Open Unconfirmed scenes to inspect candidates.';box.append(p);}
  const confirmed=Object.values(graphState?.nodes||{}).filter(node=>node.classification==='confirmed-reachable').length;
  const possible=(graphState?.edges||[]).filter(edge=>edge.evidence_level==='possible').length;
  el('scene-status').textContent=`revision ${(graphState?.revision||'workspace').slice(0,12)} · ${Object.keys(graphState?.nodes||{}).length} scenes · ${confirmed} confirmed reachable · ${possible} possible relations · ${(graphState?.diagnostics||[]).length} diagnostics`;
}
async function loadGraph(){graphState=await getJson('/api/knowledge/scene-graph');render();}
el('scene-graph-refresh').onclick=()=>loadGraph().catch(error=>el('scene-status').textContent=error.message);
el('scene-probe').onclick=()=>rescan().catch(error=>el('scene-status').textContent=error.message);
el('scene-preview-close').onclick=()=>el('scene-preview').close();
loadGraph().catch(error=>el('scene-status').textContent=error.message);

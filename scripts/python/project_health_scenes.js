'use strict';
const el=id=>document.getElementById(id);
let graphState=null;
let sessionToken='';
let activeView='graph';
let compositionPage=1;
const compositionPageSize=20;

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
  const card=document.createElement('button');card.type='button';card.className=`scene-card ${nodeClass(path,evidence)}`;card.title=path;card.dataset.scenePath=path;
  const strong=document.createElement('strong');strong.textContent=shortName(path);const small=document.createElement('small');small.textContent=`${graphState.nodes[path]?.classification||'unknown'} · ${evidence}`;card.append(strong,small);card.onclick=()=>showScene(path);branch.append(card);
  if(stack.has(path)){const cycle=document.createElement('span');cycle.className='scene-cycle';cycle.textContent='cycle';branch.append(cycle);return branch;}
  const nextStack=new Set(stack);nextStack.add(path);const edges=edgeChildren(path);
  if(edges.length){const children=document.createElement('div');children.className='scene-map-children';for(const edge of edges){const row=document.createElement('div');row.className='scene-edge-row';const line=document.createElement('span');line.className='scene-edge-line';const label=document.createElement('span');label.className=`scene-edge-label ${edge.evidence_level==='possible'?'scene-possible':'scene-effective'}`;label.textContent=`${edge.evidence_level||'possible'} · ${edge.kind||'relation'}`;row.append(line,label);children.append(row,renderBranch(edge.target,edge.evidence_level||'possible',nextStack));}branch.append(children);}
  return branch;
}
function renderGraph(){
  const box=el('scene-graph');box.replaceChildren();
  const main=graphState?.main_scene;
  if(main && graphState.nodes?.[main])box.append(renderBranch(main));
  else{const p=document.createElement('p');p.textContent='No confirmed main scene. Open Unconfirmed scenes to inspect candidates.';box.append(p);}
  const confirmed=Object.values(graphState?.nodes||{}).filter(node=>node.classification==='confirmed-reachable').length;
  const possible=(graphState?.edges||[]).filter(edge=>edge.evidence_level==='possible').length;
  el('scene-status').textContent=`revision ${(graphState?.revision||'workspace').slice(0,12)} · ${Object.keys(graphState?.nodes||{}).length} scenes · ${confirmed} confirmed reachable · ${possible} possible relations · ${(graphState?.diagnostics||[]).length} diagnostics`;
}

const graphHost=el('scene-graph');
const compositionHost=document.createElement('div');compositionHost.id='scene-structure';compositionHost.hidden=true;graphHost.insertAdjacentElement('afterend',compositionHost);
const compositionToolbar=document.createElement('div');compositionToolbar.className='scene-composition-toolbar';compositionToolbar.hidden=true;compositionHost.insertAdjacentElement('beforebegin',compositionToolbar);
const resourceType=document.createElement('select');resourceType.setAttribute('aria-label','Resource type');
for(const [value,label] of [['all','All resources'],['scene','Scenes'],['script','Scripts'],['config','Configuration'],['asset','Assets'],['other','Other']]){const option=document.createElement('option');option.value=value;option.textContent=label;resourceType.append(option);}
const includeUnreachable=document.createElement('input');includeUnreachable.type='checkbox';includeUnreachable.id='include-unreachable';
const includeLabel=document.createElement('label');includeLabel.htmlFor='include-unreachable';includeLabel.textContent=' Include resources outside route tree';
const firstPage=document.createElement('button');firstPage.type='button';firstPage.textContent='First';
const previousPage=document.createElement('button');previousPage.type='button';previousPage.textContent='Previous';
const nextPage=document.createElement('button');nextPage.type='button';nextPage.textContent='Next';
const lastPage=document.createElement('button');lastPage.type='button';lastPage.textContent='Last';
const pageInfo=document.createElement('span');pageInfo.className='scene-composition-page-info';
compositionToolbar.append(resourceType,includeUnreachable,includeLabel,firstPage,previousPage,nextPage,lastPage,pageInfo);
const graphButton=document.createElement('button');graphButton.type='button';graphButton.textContent='Scene route tree';graphButton.setAttribute('aria-pressed','true');
const compositionButton=document.createElement('button');compositionButton.type='button';compositionButton.textContent='Scene composition';compositionButton.setAttribute('aria-pressed','false');
el('scene-graph-refresh').parentNode.insertBefore(compositionButton,el('scene-graph-refresh'));
el('scene-graph-refresh').parentNode.insertBefore(graphButton,compositionButton);

function resourceKind(path){
  const suffix=(String(path||'').split('.').pop()||'').toLowerCase();
  if(suffix==='tscn')return 'scene';
  if(['gd','cs'].includes(suffix))return 'script';
  if(['json','cfg','ini','csv','yaml','yml','toml','tres','res'].includes(suffix))return 'config';
  if(['png','jpg','jpeg','webp','svg','gif','wav','ogg','mp3','ttf','otf','glb'].includes(suffix))return 'asset';
  return 'other';
}
function routeTreeClosure(){
  const nodes=graphState?.nodes||{};
  const seen=new Set();
  const pending=graphState?.main_scene&&nodes[graphState.main_scene]?[graphState.main_scene]:[];
  const bySource=new Map();
  for(const edge of graphState?.edges||[]){
    if(!edge.source||!edge.target||!nodes[edge.target])continue;
    if(!bySource.has(edge.source))bySource.set(edge.source,[]);
    bySource.get(edge.source).push(edge.target);
  }
  while(pending.length){const current=pending.pop();if(seen.has(current))continue;seen.add(current);for(const target of bySource.get(current)||[])pending.push(target);}
  return seen;
}
function compositionResources(){
  const resources=new Map();
  const add=(path,kind,origin)=>{
    if(!path||String(path).startsWith('SubResource('))return;
    const existing=resources.get(path)||{path,kind:kind||resourceKind(path),origins:[]};
    if(origin&&!existing.origins.includes(origin))existing.origins.push(origin);
    resources.set(path,existing);
  };
  const closure=routeTreeClosure();
  for(const [path,scene] of Object.entries(graphState?.nodes||{})){
    if(!includeUnreachable.checked&&!closure.has(path))continue;
    add(path,'scene',closure.has(path)?'route tree':'outside route tree');
    for(const script of scene.functional_summary?.scripts||[])add(script,'script','attached script');
    for(const config of scene.functional_summary?.config_references||[])add(config,'config','scene config reference');
    for(const node of scene.nodes||[])for(const resource of node.resources||[])add(resource,resourceKind(resource),'node resource');
  }
  const referencesBySource=new Map();
  for(const ref of graphState?.code_references||[]){if(!ref.source||!ref.target)continue;if(!referencesBySource.has(ref.source))referencesBySource.set(ref.source,[]);referencesBySource.get(ref.source).push(ref);}
  const pending=[...resources.values()].filter(item=>item.kind==='script').map(item=>item.path);
  const visited=new Set();
  while(pending.length){
    const source=pending.shift();if(visited.has(source))continue;visited.add(source);
    for(const ref of referencesBySource.get(source)||[]){const kind=resourceKind(ref.target);add(ref.target,kind,ref.classification==='dynamic-candidate'?'dynamic candidate':'script reference');if(kind==='script')pending.push(ref.target);}
  }
  return [...resources.values()].sort((left,right)=>left.path.localeCompare(right.path));
}
function renderComposition(){
  compositionHost.replaceChildren();
  const all=compositionResources();
  const filtered=resourceType.value==='all'?all:all.filter(item=>item.kind===resourceType.value);
  const pages=Math.max(1,Math.ceil(filtered.length/compositionPageSize));compositionPage=Math.min(Math.max(1,compositionPage),pages);
  const start=(compositionPage-1)*compositionPageSize;
  const table=document.createElement('table');table.className='scene-composition-table';
  const head=document.createElement('thead');head.innerHTML='<tr><th>Name</th><th>Type</th><th>Evidence</th></tr>';table.append(head);
  const body=document.createElement('tbody');
  for(const item of filtered.slice(start,start+compositionPageSize)){
    const row=document.createElement('tr');row.dataset.resourcePath=item.path;row.dataset.resourceType=item.kind;row.title=item.path;
    const name=document.createElement('td');
    if(item.kind==='scene'&&graphState?.nodes?.[item.path]){const button=document.createElement('button');button.type='button';button.textContent=shortName(item.path);button.title=item.path;button.onclick=()=>showScene(item.path);name.append(button);}else{name.textContent=shortName(item.path);name.title=item.path;}
    const kind=document.createElement('td');kind.textContent=item.kind;
    const evidence=document.createElement('td');evidence.textContent=item.origins.join(', ')||'-';
    row.append(name,kind,evidence);body.append(row);
  }
  table.append(body);compositionHost.append(table);
  if(!filtered.length){const empty=document.createElement('p');empty.textContent='No resources in this category.';compositionHost.append(empty);}
  pageInfo.textContent=`Page ${compositionPage} / ${pages} · ${filtered.length} resources`;
  firstPage.disabled=previousPage.disabled=compositionPage<=1;nextPage.disabled=lastPage.disabled=compositionPage>=pages;
  el('scene-status').textContent=`Scene composition · ${filtered.length} resources · revision ${(graphState?.revision||'workspace').slice(0,12)}`;
}
function setView(view){
  activeView=view;
  const graphVisible=view==='graph';
  graphHost.hidden=!graphVisible;compositionHost.hidden=graphVisible;compositionToolbar.hidden=graphVisible;
  graphButton.setAttribute('aria-pressed',String(graphVisible));compositionButton.setAttribute('aria-pressed',String(!graphVisible));
  if(graphVisible)renderGraph();else renderComposition();
}
async function loadGraph(){
  graphState=await getJson('/api/knowledge/scene-graph');
  renderGraph();
  if(activeView==='composition')renderComposition();
}

graphButton.onclick=()=>setView('graph');
compositionButton.onclick=()=>{compositionPage=1;setView('composition');};
resourceType.onchange=()=>{compositionPage=1;renderComposition();};
includeUnreachable.onchange=()=>{compositionPage=1;renderComposition();};
firstPage.onclick=()=>{compositionPage=1;renderComposition();};
previousPage.onclick=()=>{compositionPage--;renderComposition();};
nextPage.onclick=()=>{compositionPage++;renderComposition();};
lastPage.onclick=()=>{compositionPage=Number.MAX_SAFE_INTEGER;renderComposition();};
el('scene-graph-refresh').onclick=()=>loadGraph().catch(error=>el('scene-status').textContent=error.message);
el('scene-probe').onclick=()=>rescan().catch(error=>el('scene-status').textContent=error.message);
el('scene-preview-close').onclick=()=>el('scene-preview').close();
loadGraph().catch(error=>el('scene-status').textContent=error.message);

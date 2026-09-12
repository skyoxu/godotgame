'use strict';
const el = id => document.getElementById(id);
const pretty = value => JSON.stringify(value, null, 2);
const PAGE_SIZE = 20;
let token = '';
let currentPage = 1;
let operationPoll = null;
let selectedTasks = new Set();
let visibleTaskIds = [];
let allTasks = [];
let runtimeById = new Map();
let eligibleById = new Map();
let activeFilter = null;
let activeTaskDetail = null;
let currentConfig = null;
let currentStatus = null;

const consumerHelp = {
  'repository-session': '综合调查：候选只作为证据发现，不改变任何章节状态。',
  chapter4: 'Chapter 4：架构/契约候选为 observe-only；排名不等于接受。',
  chapter5: 'Chapter 5：任务级验收/规则候选为 observe-only；不得掩盖 acceptance / refs 缺陷。',
  chapter6: 'Chapter 6：实施前候选必须人工 accept/reject、freeze，并经过 strict Impact handoff。',
  review: 'Review：必须使用独立 review consumer 上下文，不能复用 Chapter 6 freeze。'
};
const sourcePathRequirements = [
  ['tasks','任务定义与任务视图：关联任务编号、验收条件和 gameplay 范围。','.taskmaster/tasks'],
  ['product_requirements','产品需求：理解功能目标、用户价值和需求边界。','docs/prd'],
  ['architecture_decisions','架构决策：解释技术选择、约束及演进原因。','docs/adr'],
  ['architecture','架构与功能设计：定位基础架构、Overlay 和契约说明。','docs/architecture'],
  ['agent_rules','代理规则：约束自动化实施和仓库操作。','docs/agents'],
  ['workflows','工作流：定位章节流程、执行协议和操作指南。','docs/workflows'],
  ['domain_code','领域代码与契约：分析规则、状态和可调参数读取链。','Game.Core'],
  ['engine_code','引擎实现：关联 Godot 场景、脚本、资源和素材。','Game.Godot'],
  ['domain_tests','领域测试：定位不依赖引擎的验收证据。','Game.Core.Tests'],
  ['engine_tests','引擎测试：定位场景/引擎集成的 GdUnit4 证据。','Tests.Godot'],
  ['project_entry','项目入口：环境要求和常用命令。','README.md'],
  ['repository_rules','仓库路由规则：权威来源和不可协商约束。','AGENTS.md'],
  ['delivery_profile','交付配置：识别交付模式和安全策略。','DELIVERY_PROFILE.md'],
  ['root_workflow','完整工作流：理解章节关系和 stop-loss。','workflow.md'],
  ['testing_rules','测试规范：测试分层和质量门禁。','docs/testing-framework.md']
];

async function api(name, body) {
  if (!token) {
    const response = await fetch('/api/knowledge/session', {cache:'no-store'});
    const result = await response.json();
    if (!response.ok) throw new Error(result.reason || 'Unable to create local session');
    token = result.token;
  }
  const path = name.startsWith('/api/') ? name : '/api/knowledge/' + name;
  const options = body === undefined ? {cache:'no-store'} : {
    method:'POST', cache:'no-store',
    headers:{'Content-Type':'application/json','X-Project-Health-Token':token},
    body:JSON.stringify(body)
  };
  const response = await fetch(path, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.reason || `HTTP ${response.status}`);
  return result;
}
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function textParagraph(parent, value, className='') {
  const p=document.createElement('p'); p.textContent=String(value ?? ''); if(className)p.className=className; parent.append(p); return p;
}
function button(text, action, className='') {
  const b=document.createElement('button'); b.type='button'; b.textContent=text; if(className)b.className=className;
  b.onclick=event=>{event.preventDefault(); Promise.resolve(action()).catch(showError);}; return b;
}
function showError(error) { el('message').textContent = error?.message || String(error); }

function setPageLocked(locked, message='The page is locked until the active operation finishes.') {
  el('app-main').inert = Boolean(locked);
  el('operation-lock').hidden = !locked;
  el('operation-lock-message').textContent = message;
}
async function refreshOperation() {
  try {
    const state=await api('operation');
    const scope=state.task_ids?.length ? ` · tasks ${state.task_ids.join(', ')}` : '';
    setPageLocked(state.active, state.active ? `${state.action}${state.verification_mode ? ` (${state.verification_mode})` : ''}${scope} · started ${state.started_at}` : undefined);
    return state;
  } catch (_) { return null; }
}
function startOperationPolling() {
  if(operationPoll) clearInterval(operationPoll);
  operationPoll=setInterval(refreshOperation,1000);
}
async function runOperation(label, action) {
  el('message').textContent=label;
  try { const result=await action(); el('message').textContent='Ready. Results are bound to the displayed snapshot.'; return result; }
  catch(error){showError(error); throw error;}
  finally{await refreshOperation();}
}

function configLines(value) { return String(value || '').split(/\r?\n/).map(line=>line.trim()).filter(Boolean); }
function renderSourcePathRequirements(config={}) {
  const container=el('config-source-requirements'); container.replaceChildren();
  for(const [key,reason,defaultPath] of sourcePathRequirements){
    const row=document.createElement('div'); const label=document.createElement('span'); label.textContent=reason;
    const input=document.createElement('input'); input.dataset.sourceKey=key; input.placeholder=defaultPath;
    input.value=config.source_path_bindings?.[key] ?? ((config.source_paths || []).includes(defaultPath) ? defaultPath : '');
    input.addEventListener('input',updateConfigPreview); row.append(label,input); container.append(row);
  }
}
function renderConfigEditor(config) {
  currentConfig=config; renderSourcePathRequirements(config);
  el('config-gdd-paths').value=(config.gdd_paths || []).join('\n');
  el('config-task-scene-bindings').value=pretty(config.task_scene_bindings || []);
  el('config-query-aliases').value=pretty(config.query_aliases || {});
  updateConfigPreview();
}
function collectConfigEditor() {
  const source_path_bindings=Object.fromEntries([...document.querySelectorAll('[data-source-key]')].map(input=>[input.dataset.sourceKey,input.value.trim()]).filter(([,value])=>value));
  return {
    ...(currentConfig || {}),
    source_paths:Object.values(source_path_bindings), source_path_bindings,
    gdd_paths:configLines(el('config-gdd-paths').value),
    task_scene_bindings:JSON.parse(el('config-task-scene-bindings').value || '[]'),
    query_aliases:JSON.parse(el('config-query-aliases').value || '{}')
  };
}
function updateConfigPreview() {
  if(!currentConfig)return;
  try{el('config-advanced').value=pretty(collectConfigEditor());}catch(error){el('config-advanced').value='Invalid JSON: '+error.message;}
}
for(const id of ['config-gdd-paths','config-task-scene-bindings','config-query-aliases']) el(id).addEventListener('input',updateConfigPreview);

function metric(label,value,filterKind=null,filterValue=null) {
  if(filterKind){
    const b=document.createElement('button'); b.className='metric metric-button'; b.type='button'; b.setAttribute('aria-pressed',String(activeFilter?.kind===filterKind && activeFilter?.value===filterValue));
    const strong=document.createElement('strong'); strong.textContent=value; const span=document.createElement('span'); span.textContent=label; b.append(strong,span); b.onclick=()=>setFilter(filterKind,filterValue); return b;
  }
  const box=document.createElement('div'); box.className='metric'; const strong=document.createElement('strong'); strong.textContent=value; const span=document.createElement('span'); span.textContent=label; box.append(strong,span); return box;
}
function renderStatus(status) {
  currentStatus=status;
  const revision=String(status.revision || 'none');
  el('revision').textContent=`${status.branch || status.snapshot_mode || 'unknown'} · ${revision.slice(0,12)}${status.scanned_at ? ` · ${status.scanned_at}` : ''}`;
  el('publication').textContent=status.publication?.note || '';
  const counts=status.counts || {};
  const nodes=[metric('indexed files',String(counts.files ?? 0)),metric('searchable text',String(counts.searchable ?? 0)),metric('bounded assets',String(counts.assets ?? 0)),metric('task data initialized',status.template_state?.task_data_initialized ? 'yes':'no')];
  el('summary').replaceChildren(...nodes);
  const gdds=status.gdd_files || (status.configured_gdd_sources || []).map(path=>({path,available:null}));
  el('gdds').replaceChildren(...(gdds.length ? gdds.map(item=>{const p=document.createElement('p');p.textContent=`${item.available===false?'○':'●'} ${item.path}${item.available===false?' · not present in snapshot':''}`;return p;}) : [Object.assign(document.createElement('p'),{textContent:'No GDD supplement configured.'})]));
  const warning=el('snapshot-warning');
  if(status.snapshot_fresh===false){warning.hidden=false;warning.textContent='Local main moved after this scan. Scan local main again before relying on task/source/runtime evidence.';}
  else if(warning){warning.hidden=true;warning.textContent='';}
}
function augmentTaskMetrics() {
  if(!currentStatus)return;
  const statusCounts={}, godotCounts={};
  for(const task of allTasks){statusCounts[task.status || 'unknown']=(statusCounts[task.status || 'unknown']||0)+1;const g=godotLabel(task).key;godotCounts[g]=(godotCounts[g]||0)+1;}
  const base=[metric('indexed files',String(currentStatus.counts?.files ?? 0)),metric('tasks',String(allTasks.length))];
  for(const [key,value] of Object.entries(statusCounts).sort()) base.push(metric(`task: ${key}`,String(value),'task_status',key));
  for(const [key,value] of Object.entries(godotCounts).sort()) base.push(metric(`Godot: ${key}`,String(value),'godot_status',key));
  el('summary').replaceChildren(...base);
}

function runtimeEvidence(id) { return runtimeById.get(String(id)); }
function godotLabel(task) {
  const evidence=runtimeEvidence(task.id);
  if(evidence?.runtime_verified) return {key:'runtime_verified',text:'runtime verified'};
  if(evidence?.status==='failed') return {key:'runtime_failed',text:'runtime failed'};
  if(evidence?.status==='runtime_unverified') return {key:'runtime_unverified',text:'runtime unverified'};
  const key=task.godot?.status || (task.godot?.runtime_eligible ? 'candidate':'unmapped');
  return {key,text:key.replaceAll('_',' ')};
}
function filteredTasks() {
  if(!activeFilter)return allTasks;
  return allTasks.filter(task=>activeFilter.kind==='task_status' ? String(task.status || 'unknown')===activeFilter.value : godotLabel(task).key===activeFilter.value);
}
function setFilter(kind,value) {
  if(activeFilter?.kind===kind && activeFilter?.value===value) activeFilter=null; else activeFilter={kind,value};
  currentPage=1; el('active-filter').textContent=activeFilter?`Filter: ${kind} = ${value}`:'Showing all tasks'; el('clear-filter').disabled=!activeFilter; augmentTaskMetrics(); renderTaskPage();
}
function updateSelection() {
  el('selection-count').textContent=`${selectedTasks.size} task${selectedTasks.size===1?'':'s'} selected`;
  el('runtime-selected').textContent=`Verify selected (${selectedTasks.size})`;
  el('runtime-selected').disabled=selectedTasks.size===0;
}
function renderPager() {
  const rows=filteredTasks(), pages=Math.max(1,Math.ceil(rows.length/PAGE_SIZE)); currentPage=Math.min(Math.max(currentPage,1),pages);
  const build=()=>{const wrap=document.createDocumentFragment();wrap.append(button('Previous',()=>{currentPage--;renderTaskPage();}));const span=document.createElement('span');span.textContent=`Page ${currentPage} / ${pages} · ${rows.length} tasks`;wrap.append(span,button('Next',()=>{currentPage++;renderTaskPage();}));const children=[...wrap.childNodes];children[0].disabled=currentPage<=1;children[2].disabled=currentPage>=pages;return children;};
  for(const id of ['pager-top','pager-bottom']) el(id).replaceChildren(...build());
}
function renderTaskPage() {
  const rows=filteredTasks(); renderPager(); const start=(currentPage-1)*PAGE_SIZE; const visible=rows.slice(start,start+PAGE_SIZE); visibleTaskIds=visible.map(row=>String(row.id));
  const body=el('tasks'); body.replaceChildren();
  if(!visible.length){const tr=document.createElement('tr');const td=document.createElement('td');td.colSpan=7;td.className='empty-result';td.textContent=allTasks.length?'No tasks match this filter.':'No business task data. This is a valid template state.';tr.append(td);body.append(tr);updateSelection();return;}
  for(const task of visible){
    const tr=document.createElement('tr');tr.dataset.task=String(task.id);
    const selectTd=document.createElement('td');selectTd.className='selection';const input=document.createElement('input');input.type='checkbox';input.value=String(task.id);input.disabled=!task.godot?.runtime_eligible;input.checked=selectedTasks.has(String(task.id));input.onchange=()=>{input.checked?selectedTasks.add(input.value):selectedTasks.delete(input.value);updateSelection();};selectTd.append(input);
    const idTd=document.createElement('td');idTd.append(button(String(task.id),()=>showTask(String(task.id)),'task-detail'));
    const titleTd=document.createElement('td');titleTd.textContent=task.title || '';
    const statusTd=document.createElement('td');statusTd.textContent=task.status || '';
    const depsTd=document.createElement('td');depsTd.textContent=(task.dependencies || []).join(', ');
    const subtasksTd=document.createElement('td');subtasksTd.textContent=Array.isArray(task.recommendedSubtasks)?task.recommendedSubtasks.join(', '):String(task.recommendedSubtasks ?? '');
    const godotTd=document.createElement('td');const label=godotLabel(task);godotTd.append(button(label.text,()=>setFilter('godot_status',label.key),'status-button'));
    tr.append(selectTd,idTd,titleTd,statusTd,depsTd,subtasksTd,godotTd);body.append(tr);
  }
  updateSelection();
}
async function loadTasks() {
  const [tasks,eligibility,latestRuntime]=await Promise.all([api('tasks'),api('runtime-eligibility'),api('runtime-latest')]);
  allTasks=tasks.tasks || []; eligibleById=new Map((eligibility.tasks || []).map(row=>[String(row.id),row]));runtimeById=new Map((latestRuntime.tasks || []).map(row=>[String(row.task_id),row]));
  for(const task of allTasks){const item=eligibleById.get(String(task.id));task.godot=task.godot || {};task.godot.runtime_eligible=Boolean(item?.eligible);}
  selectedTasks=new Set([...selectedTasks].filter(id=>eligibleById.get(id)?.eligible)); augmentTaskMetrics(); renderTaskPage();
}

function sourceButton(path,label=path) { return button(label,()=>showSource(path)); }
function semanticEntry(detail,kind,path) { return (detail?.semantic?.entries || []).find(item=>item?.kind===kind && item?.path===path) || null; }
function renderSourceContent(content, config=null, semantic=null) {
  const wrap=document.createElement('div');
  if(config){const note=document.createElement('div');note.className='source-semantic-note';note.textContent='Yellow = exact reviewed/confirmed pointer. Blue = generated semantic suggestion whose JSON pointer exists; suggestion is not authority.';wrap.append(note);}
  const pre=document.createElement('pre'); const confirmed=new Set((config?.confirmed_fields || []).map(field=>Number(field.line)).filter(Number.isFinite));
  const fieldsByPointer=new Map((config?.fields || []).map(field=>[String(field.pointer),field]));
  const suggested=new Set((semantic?.parameters || []).map(param=>fieldsByPointer.get(String(param.pointer || param.key || ''))?.line).filter(Number.isFinite).map(Number));
  String(content).split('\n').forEach((line,index)=>{const row=document.createElement('span');row.className=confirmed.has(index+1)?'source-line source-line-related':suggested.has(index+1)?'source-line source-line-suggested':'source-line';const num=document.createElement('span');num.className='source-line-number';num.textContent=String(index+1).padStart(4,' ')+'  ';row.append(num,document.createTextNode(line));pre.append(row,'\n');});
  wrap.append(pre);return wrap;
}
function imageLink(path) {
  const wrapper=document.createElement('span');wrapper.className='image-reference';const link=document.createElement('a');link.textContent=path;const revision=activeTaskDetail?.revision ? '&revision='+encodeURIComponent(activeTaskDetail.revision) : '';link.href='/api/knowledge/image?path='+encodeURIComponent(path)+revision;link.target='_blank';link.rel='noopener';
  const preview=document.createElement('span');preview.className='image-preview';preview.hidden=true;const img=document.createElement('img');img.alt=path;const message=document.createElement('span');message.textContent='Loading image…';preview.append(img,message);wrapper.append(link,preview);
  const open=()=>{preview.hidden=false;if(!img.src)img.src=link.href;};img.onload=()=>{message.hidden=true;};img.onerror=()=>{img.hidden=true;message.textContent='Preview unavailable.';};wrapper.onmouseenter=open;wrapper.onmouseleave=()=>preview.hidden=true;link.onfocus=open;wrapper.onfocusout=()=>preview.hidden=true;return wrapper;
}
async function showSource(path, config=null, semantic=null) {
  if(/\.(png|jpe?g|webp|svg)$/i.test(path)){showDialog(path,imageLink(path));return;}
  const data=await api('source?path='+encodeURIComponent(path));
  if(activeTaskDetail && data.revision!==activeTaskDetail.revision) throw new Error('Snapshot changed. Reopen the task before inspecting source.');
  showDialog(`${path} @ ${String(data.revision || '').slice(0,12)}`,renderSourceContent(data.content ?? data.text ?? '',config,semantic));
}
function showDialog(title,body,links=null) {
  el('detail-title').textContent=title;el('detail-links').replaceChildren();el('detail-body').replaceChildren();
  if(links)el('detail-links').append(links);if(body instanceof Node)el('detail-body').append(body);else el('detail-body').textContent=typeof body==='string'?body:pretty(body);if(!el('detail').open)el('detail').showModal();
}
function navGroup(parent,title,items,renderItem) {
  if(!items?.length)return;const section=document.createElement('div');section.className='navigation-group';const h=document.createElement('h3');h.textContent=`${title} (${items.length})`;section.append(h);items.forEach(item=>renderItem(section,item));parent.append(section);
}
function renderResourceChain(parent,resources) {
  for(const resource of resources || []) textParagraph(parent,`${resource.path || '[unresolved]'} · ${(resource.chain || []).join(' → ')}${resource.unresolved_reason ? ` · ${resource.unresolved_reason}`:''}`,'field-help');
}
function renderTaskDetail(data) {
  activeTaskDetail=data;const nav=data.navigation || {};const box=document.createElement('div');
  const staticBox=document.createElement('div');staticBox.className='navigation-group';const h=document.createElement('h3');h.textContent=`Static Godot: ${nav.static?.status || 'unmapped'}`;staticBox.append(h);textParagraph(staticBox,nav.static?.limitation || '');
  for(const scene of nav.static?.scenes || []) textParagraph(staticBox,`${scene.scene} · ${scene.node} → ${scene.script} · witness: ${scene.witness}`);
  for(const candidate of nav.static?.candidates || []) textParagraph(staticBox,`Candidate: ${candidate.scene} via ${candidate.evidence}`);
  for(const invalid of nav.static?.invalid_declarations || []) textParagraph(staticBox,'Invalid reviewed mapping: '+pretty(invalid),'warning-text');box.append(staticBox);
  navGroup(box,'配置文件',nav.configs,(section,item)=>{const details=document.createElement('details');const summary=document.createElement('summary');summary.textContent=`${item.path} · ${item.evidence_kind}`;details.append(summary);const semantic=semanticEntry(data,'config',item.path);details.append(sourceButton(item.path,'Open scanned source'));
    if(item.confirmed_fields?.length){textParagraph(details,'Confirmed fields:');for(const field of item.confirmed_fields)textParagraph(details,`${field.pointer} = ${pretty(field.value)} · line ${field.line} · ${field.confirmation}`,'field-help');}
    if(semantic){textParagraph(details,'Generated semantic note (non-authoritative): '+String(semantic.explanation || ''));for(const param of semantic.parameters || [])textParagraph(details,`${param.pointer || param.key} · ${param.meaning || param.description || ''}`,'field-help');}
    if(item.readers?.length){textParagraph(details,'Readers:');for(const reader of item.readers)textParagraph(details,`${reader.reader}:${reader.line} · ${reader.evidence}`,'field-help');}
    if(item.parse_error)textParagraph(details,'Parse error: '+item.parse_error,'warning-text');details.append(button('Open with field highlights',()=>showSource(item.path,item,semantic)));section.append(details);});
  navGroup(box,'代码',nav.code,(section,item)=>{const d=document.createElement('details');const s=document.createElement('summary');s.textContent=`${item.path} · ${item.evidence_kind}`;d.append(s,sourceButton(item.path,'Open scanned source'));section.append(d);});
  navGroup(box,'场景与节点',nav.scenes,(section,item)=>{const d=document.createElement('details');const s=document.createElement('summary');s.textContent=`${item.path} · ${item.evidence_kind}`;const semantic=semanticEntry(data,'scene',item.path);d.append(s,sourceButton(item.path,'Open scene source'));if(semantic){textParagraph(d,'Generated semantic note (non-authoritative): '+String(semantic.explanation || ''));if(semantic.modification_guidance)textParagraph(d,'Modification guidance: '+semantic.modification_guidance,'field-help');if(semantic.modification_impact)textParagraph(d,'Modification impact: '+semantic.modification_impact,'field-help');}for(const node of item.nodes || []){const nd=document.createElement('details');const ns=document.createElement('summary');ns.textContent=`${node.node_path} (${node.type}) · line ${node.line}`;nd.append(ns);const binding=(semantic?.bindings || []).find(row=>row.node_path===node.node_path && Number(row.line)===Number(node.line));if(binding)textParagraph(nd,'Semantic binding: '+String(binding.meaning || ''),'field-help');for(const prop of node.properties || []){textParagraph(nd,`${prop.name} = ${prop.value} · line ${prop.line}`,'field-help');renderResourceChain(nd,prop.resources);}renderResourceChain(nd,node.instance);d.append(nd);}section.append(d);});
  navGroup(box,'素材',nav.assets,(section,item)=>{const d=document.createElement('details');const s=document.createElement('summary');const semantic=semanticEntry(data,'asset',item.path);if(/\.(png|jpe?g|webp|svg)$/i.test(item.path))s.append(imageLink(item.path),document.createTextNode(` · ${item.evidence_kind}`));else s.textContent=`${item.path} · ${item.evidence_kind}`;d.append(s);if(semantic){textParagraph(d,'Generated semantic note (non-authoritative): '+String(semantic.explanation || ''));if(semantic.modification_guidance)textParagraph(d,'Modification guidance: '+semantic.modification_guidance,'field-help');if(semantic.modification_impact)textParagraph(d,'Modification impact: '+semantic.modification_impact,'field-help');}for(const user of item.users || []){textParagraph(d,`${user.source}:${user.line} · ${user.evidence}`,'field-help');const binding=(semantic?.bindings || []).find(row=>row.source===user.source && Number(row.line)===Number(user.line));if(binding)textParagraph(d,'Semantic binding: '+String(binding.meaning || ''),'field-help');}section.append(d);});
  navGroup(box,'建议验证',nav.tests,(section,item)=>{const d=document.createElement('details');const s=document.createElement('summary');s.textContent=`${item.path} · ${item.evidence_kind}`;d.append(s,sourceButton(item.path,'Open test source'));textParagraph(d,item.command || '');section.append(d);});
  if(nav.unresolved_references?.length){const d=document.createElement('details');const s=document.createElement('summary');s.textContent=`Unresolved references (${nav.unresolved_references.length})`;d.append(s);for(const item of nav.unresolved_references)textParagraph(d,`${item.source}: ${item.path} · ${item.reason}`,'field-help');box.append(d);}
  if(nav.limitations?.length){const d=document.createElement('details');const s=document.createElement('summary');s.textContent='Navigation limitations';d.append(s);for(const line of nav.limitations)textParagraph(d,line,'field-help');box.append(d);}
  if(data.semantic){const d=document.createElement('details');const s=document.createElement('summary');s.textContent='Generated semantic evidence';const pre=document.createElement('pre');pre.textContent=pretty(data.semantic);d.append(s,pre);box.append(d);}
  if(data.resource_knowledge){const d=document.createElement('details');const s=document.createElement('summary');s.textContent='Reconstructed task-resource knowledge';const pre=document.createElement('pre');pre.textContent=pretty(data.resource_knowledge);d.append(s,pre);box.append(d);}
  if(data.reviewed_resources){const d=document.createElement('details');const s=document.createElement('summary');s.textContent='Explicit reviewed resources';const pre=document.createElement('pre');pre.textContent=pretty(data.reviewed_resources);d.append(s,pre);box.append(d);}
  const raw=document.createElement('details');const rs=document.createElement('summary');rs.textContent='Raw task evidence JSON';const pre=document.createElement('pre');pre.textContent=pretty({task:data.task,runtime:data.runtime,knowledge:data.knowledge});raw.append(rs,pre);box.append(raw);
  showDialog(`Task ${data.task?.id || data.knowledge?.task_id || ''} @ ${String(data.revision || '').slice(0,12)}`,box);
}
async function showTask(id) { renderTaskDetail(await api('task?id='+encodeURIComponent(id))); }

function actionEntry(item) {
  const div=document.createElement('div');div.className='action-entry';div.append(sourceButton(item.path,item.path));const meta=document.createElement('span');meta.textContent=`score ${item.score} · line ${item.line}${item.source_binding ? ` · ${item.source_binding}`:''}`;div.append(meta);if(item.snippet){const pre=document.createElement('pre');pre.textContent=item.snippet;div.append(pre);}return div;
}
function renderActionGroup(id,countId,rows) {
  const node=el(id);node.replaceChildren();el(countId).textContent=`${rows.length} result${rows.length===1?'':'s'}`;if(!rows.length){textParagraph(node,'No result','empty-result');return;}rows.forEach(row=>node.append(actionEntry(row)));
}
function renderQuery(data,impact) {
  el('results').hidden=false;el('queries').textContent=data.queries?.length ? `Executed queries: ${data.queries.join(' · ')} · consumer=${data.consumer}` : '';
  const actionable=data.actionable || {tasks:[],configuration:[],code:[],tests:[],secondary:[]};renderActionGroup('action-tasks','action-tasks-count',actionable.tasks || []);renderActionGroup('action-configs','action-configs-count',actionable.configuration || []);renderActionGroup('action-code','action-code-count',actionable.code || []);renderActionGroup('action-tests','action-tests-count',actionable.tests || []);
  const secondary=actionable.secondary || [];el('secondary-summary').textContent=`Lower-confidence results (${secondary.length})`;el('secondary-actionable').replaceChildren();secondary.forEach(row=>el('secondary-actionable').append(actionEntry(row)));
  const knowledge=data.locator?.candidates || [];el('knowledge').replaceChildren();if(!knowledge.length)textParagraph(el('knowledge'),'No locator candidate.','empty-result');for(const item of knowledge)el('knowledge').append(actionEntry(item));
  const supplements=data.gdd_supplements || [];el('supplements').replaceChildren();if(!supplements.length)textParagraph(el('supplements'),'No matching GDD supplement.','empty-result');for(const item of supplements)el('supplements').append(actionEntry(item));
  const targets=(impact?.evidence || []).slice(0,80);el('target-count').textContent=`${targets.length} impact evidence target(s)`;el('targets').replaceChildren();for(const item of targets){el('targets').append(button(`${item.path} · ${item.relationship}${item.confirmed?' · confirmed target':''}`,()=>{el('impact-target').value=item.path;el('impact-form').requestSubmit();}));}
  el('preview').textContent=pretty({query:data,impact});
}

async function runRuntime(payload,label) {
  await runOperation(label,async()=>{const result=await api('runtime-verify',payload);await loadTasks();return result;});
}
async function load() {
  const [status,config]=await Promise.all([api('status'),api('config')]);renderStatus(status);renderConfigEditor(config);await loadTasks();await refreshOperation();startOperationPolling();el('message').textContent='Ready. Local-main investigation is read-only until an explicit config/scan/runtime action.';el('consumer-help').textContent=consumerHelp[el('consumer').value];
}

el('consumer').onchange=()=>{el('consumer-help').textContent=consumerHelp[el('consumer').value] || '';};
el('scan').onclick=()=>runOperation('Scanning local main…',async()=>{const status=await api('scan',{});renderStatus(status);await loadTasks();return status;});
el('runtime').onclick=()=>runRuntime({all_eligible:true,mode:'main'},'Verifying all runtime-eligible tasks on local main…');
el('runtime-all').onclick=()=>runRuntime({all_gameplay:true,mode:'main'},'Auditing all gameplay tasks on local main…');
el('runtime-selected').onclick=()=>runRuntime({task_ids:[...selectedTasks],mode:'main'},`Verifying ${selectedTasks.size} selected task(s) on local main…`);
el('select-page').onclick=()=>{for(const id of visibleTaskIds)if(eligibleById.get(id)?.eligible)selectedTasks.add(id);renderTaskPage();};
el('clear-selection').onclick=()=>{selectedTasks.clear();renderTaskPage();};
el('clear-filter').onclick=()=>{activeFilter=null;currentPage=1;el('active-filter').textContent='Showing all tasks';el('clear-filter').disabled=true;augmentTaskMetrics();renderTaskPage();};
el('open-config').onclick=()=>el('config-dialog').showModal();
el('close-config').onclick=()=>el('config-dialog').close();
el('save-config').onclick=()=>runOperation('Saving configuration…',async()=>{const saved=await api('config',collectConfigEditor());renderConfigEditor(saved.config);el('config-dialog').close();return saved;});
el('query-form').onsubmit=event=>{event.preventDefault();runOperation('Searching knowledge and impact…',async()=>{const request={query:el('query').value,consumer:el('consumer').value};const [data,impact]=await Promise.all([api('query',request),api('impact',{target:el('query').value,strict:false})]);renderQuery(data,impact);return data;}).catch(()=>{});};
el('impact-form').onsubmit=event=>{event.preventDefault();runOperation('Analyzing impact…',async()=>{const data=await api('impact',{target:el('impact-target').value,strict:el('impact-strict').checked});el('impact').textContent=pretty(data);return data;}).catch(()=>{});};
el('close-detail').onclick=()=>{el('detail').close();activeTaskDetail=null;};
load().catch(showError);

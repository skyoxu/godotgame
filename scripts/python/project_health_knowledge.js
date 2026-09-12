'use strict';
const $ = id => document.getElementById(id);
const PAGE_SIZE = 25;
let sessionToken = null;
let runtimeById = new Map();
let eligibleById = new Map();
let selectedTasks = new Set();
let allTasks = [];
let currentPage = 1;
let operationTimer = null;
let currentConfig = null;

async function api(path, options = {}) {
  if (!sessionToken) {
    const response = await fetch('/api/knowledge/session', {cache:'no-store'});
    const data = await response.json();
    if (!response.ok) throw new Error(data.reason || response.statusText);
    sessionToken = data.token;
  }
  const headers = {'Content-Type':'application/json', ...(options.headers || {})};
  if ((options.method || 'GET') !== 'GET') headers['X-Project-Health-Token'] = sessionToken;
  const response = await fetch(path, {...options, headers, cache:'no-store'});
  const data = await response.json();
  if (!response.ok) throw new Error(data.reason || `HTTP ${response.status}`);
  return data;
}

function escapeHtml(value) { return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function pretty(value) { return JSON.stringify(value, null, 2); }
function renderSummary(data) {
  const rev = String(data?.revision || 'unknown');
  $('summary').innerHTML = `<div><strong>${data?.counts?.files ?? 0}</strong><span>indexed files</span></div><div><strong>${data?.template_state?.task_data_initialized ? 'yes':'no'}</strong><span>task data initialized</span></div><div><strong>${escapeHtml(rev.slice(0,12))}</strong><span>revision</span></div>`;
}
function runtimeLabel(id) {
  const evidence = runtimeById.get(String(id));
  if (evidence) return `${evidence.status}${evidence.runtime_verified ? ' ✓ main' : evidence.workspace_verified ? ' ✓ workspace' : ''}`;
  return eligibleById.get(String(id))?.eligible ? 'eligible' : 'not eligible';
}
function updateSelection() {
  $('selection-count').textContent = `${selectedTasks.size} task${selectedTasks.size === 1 ? '' : 's'} selected`;
  $('verify-selected').textContent = `验证选中任务 (${selectedTasks.size})`;
  $('verify-selected').disabled = selectedTasks.size === 0;
}
async function refreshOperation() {
  try {
    const state = await api('/api/knowledge/operation');
    $('operation-lock').hidden = !state.active;
    $('app-main').inert = Boolean(state.active);
    if (state.active) {
      const scope = state.task_ids?.length ? ` · tasks ${state.task_ids.join(', ')}` : '';
      $('operation-lock-message').textContent = `${state.action}${state.verification_mode ? ` (${state.verification_mode})` : ''}${scope}`;
    }
    return state;
  } catch (_) { return null; }
}
function beginOperationPolling() {
  if (operationTimer) clearInterval(operationTimer);
  operationTimer = setInterval(refreshOperation, 1000);
}

function renderPager() {
  const pages = Math.max(1, Math.ceil(allTasks.length / PAGE_SIZE));
  currentPage = Math.min(currentPage, pages);
  const html = `<button class="page-prev" ${currentPage <= 1 ? 'disabled':''}>Previous</button><span>Page ${currentPage} / ${pages} · ${allTasks.length} tasks</span><button class="page-next" ${currentPage >= pages ? 'disabled':''}>Next</button>`;
  for (const id of ['pager-top','pager-bottom']) $(id).innerHTML = html;
  document.querySelectorAll('.page-prev').forEach(button => button.onclick = () => { currentPage--; renderTaskPage(); });
  document.querySelectorAll('.page-next').forEach(button => button.onclick = () => { currentPage++; renderTaskPage(); });
}
function renderTaskPage() {
  renderPager();
  if (!allTasks.length) {
    $('tasks').innerHTML = '<tr><td colspan="7" class="empty">没有任务数据；模板仓空状态正常。</td></tr>';
    updateSelection(); return;
  }
  const start = (currentPage - 1) * PAGE_SIZE;
  const visible = allTasks.slice(start, start + PAGE_SIZE);
  $('tasks').innerHTML = visible.map(task => {
    const eligible = Boolean(eligibleById.get(String(task.id))?.eligible);
    return `<tr data-task="${escapeHtml(task.id)}"><td><input class="task-select" type="checkbox" value="${escapeHtml(task.id)}" ${selectedTasks.has(String(task.id)) ? 'checked':''} ${eligible ? '':'disabled'}></td><td><button class="task-detail">${escapeHtml(task.id)}</button></td><td>${escapeHtml(task.title)}</td><td>${escapeHtml(task.status)}</td><td>${escapeHtml(runtimeLabel(task.id))}</td><td>${escapeHtml(task.dependencies.join(', '))}</td><td>${task.sources.map(path => `<button class="source" data-path="${escapeHtml(path)}">${escapeHtml(path)}</button>`).join('<br>')}</td></tr>`;
  }).join('');
  document.querySelectorAll('.task-detail').forEach(button => button.onclick = showTask);
  document.querySelectorAll('#tasks .source').forEach(button => button.onclick = showSource);
  document.querySelectorAll('.task-select').forEach(input => input.onchange = event => {
    if (event.target.checked) selectedTasks.add(event.target.value); else selectedTasks.delete(event.target.value);
    updateSelection();
  });
  updateSelection();
}
async function loadTasks() {
  const [data, eligibility, latestRuntime] = await Promise.all([api('/api/knowledge/tasks'), api('/api/knowledge/runtime-eligibility'), api('/api/knowledge/runtime-latest')]);
  allTasks = data.tasks || [];
  runtimeById = new Map((latestRuntime.tasks || []).map(row => [String(row.task_id), row]));
  eligibleById = new Map((eligibility.tasks || []).map(row => [String(row.id), row]));
  $('verify-all').disabled = !(eligibility.eligible_count > 0);
  $('runtime-summary').textContent = `${eligibility.eligible_count} runtime-eligible task(s). ${eligibility.note}`;
  renderTaskPage();
}
async function showTask(event) {
  const id = event.target.closest('tr').dataset.task;
  const data = await api(`/api/knowledge/task?id=${encodeURIComponent(id)}`);
  $('detail-title').textContent = `Task ${id}`; $('detail-image').innerHTML=''; $('detail-body').textContent = pretty(data); $('detail').showModal();
}
async function showSource(event) {
  const path = event.target.dataset.path;
  $('detail-title').textContent = path;
  if (/\.(png|jpe?g|webp)$/i.test(path)) {
    $('detail-body').textContent=''; $('detail-image').innerHTML = `<img alt="${escapeHtml(path)}" src="/api/knowledge/image?path=${encodeURIComponent(path)}">`;
  } else {
    const data = await api(`/api/knowledge/source?path=${encodeURIComponent(path)}`);
    $('detail-image').innerHTML=''; $('detail-body').textContent=data.text;
  }
  $('detail').showModal();
}

function sourceButton(row) {
  return `<article><button class="source" data-path="${escapeHtml(row.path)}"><strong>${escapeHtml(row.path)}</strong></button><span>score ${row.score} · line ${row.line}</span><pre>${escapeHtml(row.snippet || '')}</pre></article>`;
}
function renderQuery(data) {
  $('queries').textContent = data.queries?.length ? `Executed queries: ${data.queries.join(' · ')}` : '';
  const actionable = data.actionable || {tasks:[],configuration:[],code:[],tests:[],secondary:[]};
  for (const key of ['tasks','configuration','code','tests','secondary']) {
    const node = $(`action-${key}`);
    const rows = actionable[key] || [];
    node.innerHTML = rows.length ? rows.map(sourceButton).join('') : '<p class="empty">No result</p>';
  }
  $('actionable').hidden = false;
  $('secondary-wrap').hidden = !(actionable.secondary || []).length;
  $('raw-results-wrap').hidden = false;
  $('results').innerHTML = data.results?.length ? data.results.map(sourceButton).join('') : '<p class="empty">没有匹配项。模板仓尚未初始化业务数据时这是正常状态。</p>';
  document.querySelectorAll('#actionable .source,#secondary-wrap .source,#results .source').forEach(button => button.onclick = showSource);
}

function renderConfig(config) {
  currentConfig = config;
  $('config-source-bindings').value = pretty(config.source_path_bindings || {});
  $('config-gdd-paths').value = (config.gdd_paths || []).join('\n');
  $('config-task-scene-bindings').value = pretty(config.task_scene_bindings || []);
  $('config-query-aliases').value = pretty(config.query_aliases || {});
  $('config').value = pretty(config);
}
function collectConfig() {
  const bindings = JSON.parse($('config-source-bindings').value || '{}');
  const config = {
    ...(currentConfig || {}),
    source_path_bindings: bindings,
    source_paths: Object.values(bindings).filter(Boolean),
    gdd_paths: $('config-gdd-paths').value.split(/\r?\n/).map(line => line.trim()).filter(Boolean),
    task_scene_bindings: JSON.parse($('config-task-scene-bindings').value || '[]'),
    query_aliases: JSON.parse($('config-query-aliases').value || '{}'),
  };
  $('config').value = pretty(config);
  return config;
}
['config-source-bindings','config-gdd-paths','config-task-scene-bindings','config-query-aliases'].forEach(id => $(id).addEventListener('input', () => { try { collectConfig(); } catch (_) {} }));

async function runRuntime(payload) {
  $('status').textContent='Runtime verification running…';
  try {
    const data = await api('/api/knowledge/runtime-verify', {method:'POST',body:JSON.stringify(payload)});
    $('runtime-summary').textContent = pretty(data.summary); await loadTasks(); $('status').textContent='Runtime verification complete';
  } catch (err) { $('status').textContent=err.message; }
  finally { await refreshOperation(); }
}
async function load() {
  const [status, config] = await Promise.all([api('/api/knowledge/status'), api('/api/knowledge/config')]);
  renderSummary(status); renderConfig(config); await loadTasks(); await refreshOperation(); beginOperationPolling(); $('status').textContent='Ready';
}

$('scan').onclick = async () => { $('status').textContent='Scanning…'; try { renderSummary(await api('/api/knowledge/scan',{method:'POST',body:'{}'})); await loadTasks(); $('status').textContent='Scan complete'; } catch(err){$('status').textContent=err.message;} finally{await refreshOperation();} };
$('runtime').onclick = () => loadTasks().catch(err => $('runtime-summary').textContent=err.message);
$('verify-selected').onclick = () => runRuntime({task_ids:[...selectedTasks],mode:$('runtime-mode').value});
$('verify-all').onclick = () => runRuntime({all_eligible:true,mode:$('runtime-mode').value});
$('select-all-visible').onclick = () => { document.querySelectorAll('.task-select:not(:disabled)').forEach(input => { input.checked=true; selectedTasks.add(input.value); }); updateSelection(); };
$('clear-selection').onclick = () => { selectedTasks.clear(); document.querySelectorAll('.task-select').forEach(input => input.checked=false); updateSelection(); };
$('query-form').onsubmit = async event => { event.preventDefault(); $('queries').textContent='Searching…'; try { renderQuery(await api('/api/knowledge/query',{method:'POST',body:JSON.stringify({query:$('query').value,consumer:$('consumer').value})})); } catch(err){$('queries').textContent=err.message;} };
$('impact-form').onsubmit = async event => { event.preventDefault(); $('impact').textContent='Analyzing…'; try { $('impact').textContent=pretty(await api('/api/knowledge/impact',{method:'POST',body:JSON.stringify({target:$('impact-target').value,strict:$('impact-strict').checked})})); } catch(err){$('impact').textContent=err.message;} };
$('save-config').onclick = async () => { try { const saved=await api('/api/knowledge/config',{method:'POST',body:JSON.stringify(collectConfig())}); renderConfig(saved.config); $('status').textContent='Configuration saved; scan to apply'; } catch(err){$('status').textContent=err.message;} finally{await refreshOperation();} };
$('close-detail').onclick = () => $('detail').close();
load().catch(err => $('status').textContent=err.message);

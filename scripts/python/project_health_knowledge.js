let sessionToken = null;
let runtimeById = new Map();
let selectedTasks = new Set();
let operationTimer = null;
const $ = id => document.getElementById(id);

async function api(path, options = {}) {
  if (!sessionToken) {
    const response = await fetch('/api/knowledge/session', {cache: 'no-store'});
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

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function renderSummary(data) {
  const files = data?.counts?.files ?? 0;
  const initialized = data?.template_state?.task_data_initialized ? 'yes' : 'no';
  const rev = String(data?.revision || 'unknown');
  $('summary').innerHTML = `<div><strong>${files}</strong><span>indexed files</span></div><div><strong>${initialized}</strong><span>task data initialized</span></div><div><strong>${escapeHtml(rev.slice(0,12))}</strong><span>revision</span></div>`;
}

function runtimeLabel(id, eligible) {
  const evidence = runtimeById.get(String(id));
  if (evidence) return `${evidence.status}${evidence.runtime_verified ? ' ✓ main' : evidence.workspace_verified ? ' ✓ workspace' : ''}`;
  return eligible ? 'eligible' : 'not eligible';
}

function updateSelection() {
  $('selection-count').textContent = `${selectedTasks.size} selected`;
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
  operationTimer = setInterval(() => refreshOperation(), 1000);
}

async function loadTasks() {
  const [data, eligibility, latestRuntime] = await Promise.all([
    api('/api/knowledge/tasks'), api('/api/knowledge/runtime-eligibility'), api('/api/knowledge/runtime-latest')
  ]);
  runtimeById = new Map((latestRuntime.tasks || []).map(row => [String(row.task_id), row]));
  const eligibleById = new Map((eligibility.tasks || []).map(row => [String(row.id), row]));
  if (!data.tasks.length) {
    $('tasks').innerHTML = '<tr><td colspan="7" class="empty">没有任务数据；模板仓空状态正常。</td></tr>';
    selectedTasks.clear(); updateSelection(); $('verify-all').disabled = true;
    return;
  }
  $('tasks').innerHTML = data.tasks.map(task => {
    const runtime = eligibleById.get(String(task.id));
    const eligible = Boolean(runtime?.eligible);
    const checked = selectedTasks.has(String(task.id)) ? 'checked' : '';
    return `<tr data-task="${escapeHtml(task.id)}"><td><input class="task-select" type="checkbox" value="${escapeHtml(task.id)}" ${checked} ${eligible ? '' : 'disabled'}></td><td><button class="task-detail">${escapeHtml(task.id)}</button></td><td>${escapeHtml(task.title)}</td><td>${escapeHtml(task.status)}</td><td>${escapeHtml(runtimeLabel(task.id, eligible))}</td><td>${escapeHtml(task.dependencies.join(', '))}</td><td>${task.sources.map(path => `<button class="source" data-path="${escapeHtml(path)}">${escapeHtml(path)}</button>`).join('<br>')}</td></tr>`;
  }).join('');
  document.querySelectorAll('.task-detail').forEach(button => button.addEventListener('click', showTask));
  document.querySelectorAll('.source').forEach(button => button.addEventListener('click', showSource));
  document.querySelectorAll('.task-select').forEach(input => input.addEventListener('change', event => {
    if (event.target.checked) selectedTasks.add(event.target.value); else selectedTasks.delete(event.target.value);
    updateSelection();
  }));
  $('verify-all').disabled = !(eligibility.eligible_count > 0);
  $('runtime-summary').textContent = `${eligibility.eligible_count} runtime-eligible task(s). ${eligibility.note}`;
  updateSelection();
}

async function showTask(event) {
  const id = event.target.closest('tr').dataset.task;
  const data = await api(`/api/knowledge/task?id=${encodeURIComponent(id)}`);
  $('detail-title').textContent = `Task ${id}`;
  $('detail-image').innerHTML = '';
  $('detail-body').textContent = JSON.stringify(data, null, 2);
  $('detail').showModal();
}

async function showSource(event) {
  const path = event.target.dataset.path;
  if (/\.(png|jpe?g|webp)$/i.test(path)) {
    $('detail-title').textContent = path;
    $('detail-body').textContent = '';
    $('detail-image').innerHTML = `<img alt="${escapeHtml(path)}" src="/api/knowledge/image?path=${encodeURIComponent(path)}">`;
  } else {
    const data = await api(`/api/knowledge/source?path=${encodeURIComponent(path)}`);
    $('detail-title').textContent = path;
    $('detail-image').innerHTML = '';
    $('detail-body').textContent = data.text;
  }
  $('detail').showModal();
}

async function runRuntime(payload) {
  $('status').textContent = 'Runtime verification running…';
  await refreshOperation(); beginOperationPolling();
  try {
    const data = await api('/api/knowledge/runtime-verify', {method:'POST', body:JSON.stringify(payload)});
    $('runtime-summary').textContent = JSON.stringify(data.summary, null, 2);
    await loadTasks();
    $('status').textContent = 'Runtime verification complete';
  } catch (err) { $('status').textContent = err.message; }
  finally { await refreshOperation(); }
}

async function load() {
  const [status, config] = await Promise.all([api('/api/knowledge/status'), api('/api/knowledge/config')]);
  renderSummary(status); $('config').value = JSON.stringify(config, null, 2); await loadTasks(); await refreshOperation(); beginOperationPolling(); $('status').textContent = 'Ready';
}

$('scan').addEventListener('click', async () => {
  $('status').textContent = 'Scanning…';
  try { renderSummary(await api('/api/knowledge/scan', {method:'POST', body:'{}'})); await loadTasks(); $('status').textContent = 'Scan complete'; }
  catch (err) { $('status').textContent = err.message; }
  finally { await refreshOperation(); }
});
$('runtime').addEventListener('click', () => loadTasks().catch(err => { $('runtime-summary').textContent = err.message; }));
$('verify-selected').addEventListener('click', () => runRuntime({task_ids:[...selectedTasks], mode:$('runtime-mode').value}));
$('verify-all').addEventListener('click', () => runRuntime({all_eligible:true, mode:$('runtime-mode').value}));
$('select-all-visible').addEventListener('click', () => {
  document.querySelectorAll('.task-select:not(:disabled)').forEach(input => { input.checked = true; selectedTasks.add(input.value); }); updateSelection();
});
$('clear-selection').addEventListener('click', () => { selectedTasks.clear(); document.querySelectorAll('.task-select').forEach(input => input.checked = false); updateSelection(); });
$('query-form').addEventListener('submit', async event => {
  event.preventDefault(); $('results').textContent = 'Searching…';
  try {
    const data = await api('/api/knowledge/query', {method:'POST', body:JSON.stringify({query:$('query').value})});
    if (!data.results.length) { $('results').innerHTML = '<p class="empty">没有匹配项。模板仓尚未初始化业务数据时这是正常状态。</p>'; return; }
    $('results').innerHTML = data.results.map(row => `<article><button class="source" data-path="${escapeHtml(row.path)}"><strong>${escapeHtml(row.path)}</strong></button><span>score ${row.score} · line ${row.line}</span><pre>${escapeHtml(row.snippet)}</pre></article>`).join('');
    document.querySelectorAll('#results .source').forEach(button => button.addEventListener('click', showSource));
  } catch (err) { $('results').textContent = err.message; }
});
$('impact-form').addEventListener('submit', async event => {
  event.preventDefault(); $('impact').textContent = 'Analyzing…';
  try { $('impact').textContent = JSON.stringify(await api('/api/knowledge/impact', {method:'POST', body:JSON.stringify({target:$('impact-target').value, strict:$('impact-strict').checked})}), null, 2); }
  catch (err) { $('impact').textContent = err.message; }
});
$('save-config').addEventListener('click', async () => {
  try { await api('/api/knowledge/config', {method:'POST', body:JSON.stringify(JSON.parse($('config').value))}); $('status').textContent = 'Configuration saved; scan to apply'; }
  catch (err) { $('status').textContent = err.message; }
  finally { await refreshOperation(); }
});
$('close-detail').addEventListener('click', () => $('detail').close());
load().catch(err => { $('status').textContent = err.message; });

let token = '';
const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.body) headers.set('Content-Type', 'application/json');
  if (token) headers.set('X-Project-Health-Token', token);
  const response = await fetch(path, {...options, headers});
  const data = await response.json();
  if (!response.ok) throw new Error(data.reason || data.status || `HTTP ${response.status}`);
  return data;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function renderSummary(data) {
  const files = data?.counts?.files ?? 0;
  const initialized = data?.template_state?.task_data_initialized ? 'yes' : 'no';
  const revision = data?.revision || 'unknown';
  $('summary').innerHTML = `<div><strong>${files}</strong><span>indexed files</span></div><div><strong>${initialized}</strong><span>task data initialized</span></div><div><strong>${escapeHtml(revision.slice(0, 12))}</strong><span>revision</span></div>`;
}

async function loadTasks() {
  const data = await api('/api/knowledge/tasks');
  if (!data.tasks.length) {
    $('tasks').innerHTML = '<tr><td colspan="5" class="empty">没有任务数据；模板仓空状态正常。</td></tr>';
    return;
  }
  $('tasks').innerHTML = data.tasks.map(task => `<tr data-task="${escapeHtml(task.id)}"><td><button class="task-detail">${escapeHtml(task.id)}</button></td><td>${escapeHtml(task.title)}</td><td>${escapeHtml(task.status)}</td><td>${escapeHtml(task.dependencies.join(', '))}</td><td>${task.sources.map(path => `<button class="source" data-path="${escapeHtml(path)}">${escapeHtml(path)}</button>`).join('<br>')}</td></tr>`).join('');
  document.querySelectorAll('.task-detail').forEach(button => button.addEventListener('click', showTask));
  document.querySelectorAll('.source').forEach(button => button.addEventListener('click', showSource));
}

async function showTask(event) {
  const id = event.target.closest('tr').dataset.task;
  const data = await api(`/api/knowledge/task?id=${encodeURIComponent(id)}`);
  $('detail-title').textContent = `Task ${id}`;
  $('detail-body').textContent = JSON.stringify(data, null, 2);
  $('detail').showModal();
}

async function showSource(event) {
  const path = event.target.dataset.path;
  const data = await api(`/api/knowledge/source?path=${encodeURIComponent(path)}`);
  $('detail-title').textContent = path;
  $('detail-body').textContent = data.text;
  $('detail').showModal();
}

async function load() {
  const session = await api('/api/knowledge/session');
  token = session.token;
  const [status, config] = await Promise.all([api('/api/knowledge/status'), api('/api/knowledge/config')]);
  renderSummary(status);
  $('config').value = JSON.stringify(config, null, 2);
  await loadTasks();
  $('status').textContent = 'Ready';
}

$('scan').addEventListener('click', async () => {
  $('status').textContent = 'Scanning…';
  try {
    const data = await api('/api/knowledge/scan', {method: 'POST', body: '{}'});
    renderSummary(data); await loadTasks(); $('status').textContent = 'Scan complete';
  } catch (err) { $('status').textContent = err.message; }
});

$('runtime').addEventListener('click', async () => {
  try {
    const data = await api('/api/knowledge/runtime-eligibility');
    $('runtime-summary').textContent = `${data.eligible_count} runtime-eligible task(s). ${data.note}`;
  } catch (err) { $('runtime-summary').textContent = err.message; }
});

$('query-form').addEventListener('submit', async (event) => {
  event.preventDefault(); $('results').textContent = 'Searching…';
  try {
    const data = await api('/api/knowledge/query', {method: 'POST', body: JSON.stringify({query: $('query').value})});
    if (!data.results.length) { $('results').innerHTML = '<p class="empty">没有匹配项。模板仓尚未初始化业务数据时这是正常状态。</p>'; return; }
    $('results').innerHTML = data.results.map(item => `<article><h3>${escapeHtml(item.path)}</h3><p>score=${item.score} · line ${item.line}</p><pre>${escapeHtml(item.snippet || '')}</pre></article>`).join('');
  } catch (err) { $('results').textContent = err.message; }
});

$('impact-form').addEventListener('submit', async (event) => {
  event.preventDefault(); $('impact').textContent = 'Analyzing…';
  try { $('impact').textContent = JSON.stringify(await api('/api/knowledge/impact', {method: 'POST', body: JSON.stringify({target: $('impact-target').value})}), null, 2); }
  catch (err) { $('impact').textContent = err.message; }
});

$('save-config').addEventListener('click', async () => {
  try { await api('/api/knowledge/config', {method: 'POST', body: JSON.stringify(JSON.parse($('config').value))}); $('status').textContent = 'Configuration saved; scan to apply'; }
  catch (err) { $('status').textContent = err.message; }
});

$('close-detail').addEventListener('click', () => $('detail').close());
load().catch(err => { $('status').textContent = err.message; });

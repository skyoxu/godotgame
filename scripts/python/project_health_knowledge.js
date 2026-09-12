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

function renderSummary(data) {
  const files = data?.counts?.files ?? 0;
  const initialized = data?.template_state?.task_data_initialized ? 'yes' : 'no';
  const revision = data?.revision || 'unknown';
  $('summary').innerHTML = `<div><strong>${files}</strong><span>indexed files</span></div><div><strong>${initialized}</strong><span>task data initialized</span></div><div><strong>${revision.slice(0, 12)}</strong><span>revision</span></div>`;
}

async function load() {
  const session = await api('/api/knowledge/session');
  token = session.token;
  const [status, config] = await Promise.all([api('/api/knowledge/status'), api('/api/knowledge/config')]);
  renderSummary(status);
  $('config').value = JSON.stringify(config, null, 2);
  $('status').textContent = 'Ready';
}

$('scan').addEventListener('click', async () => {
  $('status').textContent = 'Scanning…';
  try {
    const data = await api('/api/knowledge/scan', {method: 'POST', body: '{}'});
    renderSummary(data);
    $('status').textContent = 'Scan complete';
  } catch (err) { $('status').textContent = err.message; }
});

$('query-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  $('results').textContent = 'Searching…';
  try {
    const data = await api('/api/knowledge/query', {method: 'POST', body: JSON.stringify({query: $('query').value})});
    if (!data.results.length) { $('results').innerHTML = '<p class="empty">没有匹配项。模板仓尚未初始化业务数据时这是正常状态。</p>'; return; }
    $('results').innerHTML = data.results.map(item => `<article><h3>${escapeHtml(item.path)}</h3><p>score=${item.score} · line ${item.line}</p><pre>${escapeHtml(item.snippet || '')}</pre></article>`).join('');
  } catch (err) { $('results').textContent = err.message; }
});

$('impact-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  $('impact').textContent = 'Analyzing…';
  try {
    const data = await api('/api/knowledge/impact', {method: 'POST', body: JSON.stringify({target: $('impact-target').value})});
    $('impact').textContent = JSON.stringify(data, null, 2);
  } catch (err) { $('impact').textContent = err.message; }
});

$('save-config').addEventListener('click', async () => {
  try {
    const config = JSON.parse($('config').value);
    await api('/api/knowledge/config', {method: 'POST', body: JSON.stringify(config)});
    $('status').textContent = 'Configuration saved; scan to apply';
  } catch (err) { $('status').textContent = err.message; }
});

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

load().catch(err => { $('status').textContent = err.message; });

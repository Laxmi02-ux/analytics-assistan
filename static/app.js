let chartInstance = null;

async function loadKpis() {
  try {
    const res = await fetch('/api/kpis');
    const data = await res.json();
    document.getElementById('kpiRevenue').innerText = `$${data.total_revenue.toLocaleString()}`;
    document.getElementById('kpiProfit').innerText = `$${data.total_profit.toLocaleString()}`;
    document.getElementById('kpiMargin').innerText = `${data.gross_margin_pct}%`;
    document.getElementById('kpiRoi').innerText = `${data.roi_pct}%`;
    document.getElementById('kpiRetention').innerText = `${data.retention_pct}%`;
  } catch (err) {
    console.error('Failed to load KPIs', err);
  }
}

function appendMessage(text, className) {
  const box = document.getElementById('chatBox');
  const div = document.createElement('div');
  div.className = `msg ${className}`;
  div.innerText = text;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function renderChart(labels, dataValues, metricName, chartType) {
  const ctx = document.getElementById('analyticsChart').getContext('2d');
  if (chartInstance) chartInstance.destroy();

  document.getElementById('chartTitle').innerText = metricName;

  chartInstance = new Chart(ctx, {
    type: chartType || 'line',
    data: {
      labels: labels,
      datasets: [{
        label: metricName,
        data: dataValues,
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.35)',
        fill: chartType !== 'bar',
        borderRadius: chartType === 'bar' ? 6 : 0,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: '#e2e8f0' } } },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#29344a' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#29344a' } },
      }
    }
  });
}

async function sendMessage(overrideText) {
  const input = document.getElementById('userInput');
  const msg = (overrideText !== undefined ? overrideText : input.value).trim();
  if (!msg) return;

  appendMessage(msg, 'user-msg');
  input.value = '';

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();

    appendMessage(data.reply.replace(/\*\*/g, ''), 'bot-msg');

    if (data.type === 'chart') {
      renderChart(data.labels, data.data, data.metric, data.chart_type);
    }
  } catch (err) {
    appendMessage('Something went wrong reaching the server.', 'bot-msg');
    console.error(err);
  }
}

document.getElementById('sendBtn').addEventListener('click', () => sendMessage());
document.getElementById('userInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendMessage();
});
document.querySelectorAll('.chip').forEach((chip) => {
  chip.addEventListener('click', () => sendMessage(chip.dataset.msg));
});

// Initial load
loadKpis();
sendMessage('Show revenue');

// Frontend streamer + chart logic
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const trainBtn = document.getElementById('trainBtn');

let timer = null;
let buffer = [];
const MAX_POINTS = 120;
let lastAnomalies = [];

function updateDashboard(sample) {
  document.getElementById('latest').innerText = new Date(sample.timestamp * 1000).toLocaleTimeString();
  document.getElementById('heartRate').innerText = sample.heart_rate;
  document.getElementById('spO2').innerText = sample.blood_oxygen;
  document.getElementById('activity').innerText = sample.activity_level;
  document.getElementById('anomalyStatus').innerText = sample.is_anomaly ? 'ANOMALY' : 'Normal';
  document.getElementById('anomalyStatus').style.color = sample.is_anomaly ? '#b30000' : '#1a7d1a';

  if (sample.is_anomaly) {
    document.getElementById('recommendationText').innerText = 'Anomaly flagged — rest, take deep breaths, and contact a medical professional if the condition persists.';
    const card = document.getElementById('recommendationCard');
    card.style.display = 'block';
    card.animate([{ transform: 'translateY(-6px)', opacity: 0 }, { transform: 'translateY(0)', opacity: 1 }], { duration: 220, easing: 'ease-out' });
    // highlight the anomaly bubble
    const a = document.getElementById('anomalyStatus');
    a.style.background = 'rgba(239,68,68,0.12)';
    a.style.color = '#ef4444';
    a.style.border = '1px solid rgba(239,68,68,0.16)';
    a.style.transform = 'scale(1.03)';
    a.style.boxShadow = '0 10px 30px rgba(239,68,68,0.09)';
    setTimeout(()=>{ a.style.transform = ''; }, 350);
  } else {
    const card = document.getElementById('recommendationCard');
    card.style.display = 'none';
    const a = document.getElementById('anomalyStatus');
    a.style.background = 'rgba(16,185,129,0.08)';
    a.style.color = '#10b981';
    a.style.border = '1px solid rgba(16,185,129,0.12)';
  }

  // add to anomaly timeline
  if (sample.is_anomaly) {
    const list = document.getElementById('anomalyList');
    const item = document.createElement('div');
    item.style.padding = '8px';
    item.style.marginBottom = '6px';
    item.style.borderRadius = '6px';
    item.style.background = '#fff3f3';
    item.style.border = '1px solid #f1c0c0';
    item.innerHTML = `<strong>${new Date(sample.timestamp * 1000).toLocaleTimeString()}</strong> — HR ${sample.heart_rate} bpm, SpO2 ${sample.blood_oxygen}%`;
    list.prepend(item);
    lastAnomalies.unshift(item);
    if (lastAnomalies.length > 8) {
      const old = lastAnomalies.pop();
      if (old && old.parentElement) old.parentElement.removeChild(old);
    }
  }

  // push to buffer
  buffer.push(sample);
  if (buffer.length > MAX_POINTS) buffer.shift();

  redrawChart();
  document.getElementById('pointsCount').innerText = buffer.length;
  // small header count
  const ptsSmall = document.getElementById('pointsCount_small');
  if (ptsSmall) ptsSmall.innerText = buffer.length + ' points'
}

async function fetchSample() {
  try {
    const res = await fetch('/api/stream');
    const sample = await res.json();
    // mark connection healthy
    _setOnline(true);
    updateDashboard(sample);
  } catch (e) {
    console.error('error fetching sample', e);
    _setOnline(false);
  }
}

// Chart setup
const ctx = document.getElementById('chart').getContext('2d');
const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      { label: 'Heart rate (bpm)', data: [], borderColor: '#d9534f', tension: 0.2, pointRadius: 2 },
      { label: 'SpO2 (%)', data: [], borderColor: '#337ab7', tension: 0.2, pointRadius: 2 }
    ]
  },
  options: {
    scales: {
      x: { display: true, title: { display: false } },
      y: { beginAtZero: false }
    }
  }
});

function redrawChart() {
  chart.data.labels = buffer.map(s => new Date(s.timestamp * 1000).toLocaleTimeString());
  chart.data.datasets[0].data = buffer.map(s => s.heart_rate);
  chart.data.datasets[1].data = buffer.map(s => s.blood_oxygen);
  chart.update('none');
}

// connection / status handling
let statusTimer = null;
async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    const st = await res.json();
    const dot = document.getElementById('connDotHeader');
    const txt = document.getElementById('connText');
    const modelDot = document.getElementById('modelDotHeader');
    const modelText = document.getElementById('modelTextHeader');

    if (st.ok) {
      _setOnline(true);
      txt.innerText = 'Connected';
      dot.style.background = '#1a7d1a';
      if (st.model_loaded) {
        modelDot.style.background = '#1a7d1a';
        modelText.innerText = 'Model loaded';
      } else {
        modelDot.style.background = '#f39c12';
        modelText.innerText = 'Model missing';
      }
    } else {
      _setOnline(false);
    }
  } catch (err) {
    console.warn('status check failed', err);
    _setOnline(false);
  }
}

function _setOnline(isOnline) {
  const dot = document.getElementById('connDotHeader');
  const txt = document.getElementById('connText');
  const statusText = isOnline ? 'Connected' : 'Disconnected';
  const color = isOnline ? '#1a7d1a' : '#b30000';
  dot.style.background = color;
  txt.innerText = statusText;
  const connLabel = document.getElementById('connLabel');
  if (connLabel) connLabel.innerText = isOnline ? 'Live' : 'Offline';
}

startBtn.addEventListener('click', () => {
  if (timer) return;
  startBtn.disabled = true; stopBtn.disabled = false;
  // highlight active button
  startBtn.classList.add('active');
  stopBtn.classList.remove('active');
  trainBtn.classList.remove('active');
  // fetch immediately and then every second
  fetchSample();
  timer = setInterval(fetchSample, 1000);
});

stopBtn.addEventListener('click', () => {
  if (timer) clearInterval(timer);
  timer = null;
  startBtn.disabled = false; stopBtn.disabled = true;
  // update button active states
  stopBtn.classList.add('active');
  startBtn.classList.remove('active');
  trainBtn.classList.remove('active');
});

trainBtn.addEventListener('click', async () => {
  trainBtn.disabled = true;
  trainBtn.innerText = 'Retraining...';
  // highlight as active while training
  trainBtn.classList.add('active');
  startBtn.classList.remove('active');
  stopBtn.classList.remove('active');
  try {
    const res = await fetch('/api/train', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({}) });
    const data = await res.json();
    alert('Retrain: ' + (data.status ?? data.error ?? JSON.stringify(data)));
  } catch (e) {
    console.error(e);
    alert('Failed to trigger training');
  }
  trainBtn.disabled = false; trainBtn.innerText = 'Retrain Model';
  // after retrain, re-check status
  await fetchStatus();
  // small animated feedback on retrain success
  const m = document.getElementById('modelDotHeader');
  if (m) {
    m.animate([
      { transform: 'scale(1.0)' },
      { transform: 'scale(1.25)' },
      { transform: 'scale(1.0)' }
    ], { duration: 420, easing: 'ease-in-out' })
  }
  // after retrain animation, keep retrain briefly highlighted then clear
  setTimeout(()=> trainBtn.classList.remove('active'), 900);
});

// For convenience, start streaming automatically when the page loads
window.addEventListener('load', () => startBtn.click());

// start status polling
statusTimer = setInterval(fetchStatus, 2500);
fetchStatus();

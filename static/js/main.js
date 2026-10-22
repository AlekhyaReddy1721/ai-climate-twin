/* ===== PARTICLE BACKGROUND ===== */
(function () {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, particles = [];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  for (let i = 0; i < 60; i++) {
    particles.push({
      x: Math.random() * 1920, y: Math.random() * 1080,
      vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3,
      r: Math.random() * 1.5 + 0.5,
      a: Math.random() * 0.5 + 0.1,
    });
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0,212,255,${p.a})`;
      ctx.fill();
    });
    // Draw connecting lines
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0,212,255,${0.08 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
})();

/* ===== LIVE CLOCK ===== */
function updateClock() {
  const el = document.getElementById('live-time');
  if (!el) return;
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  const days   = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  el.textContent = `${days[now.getDay()]} ${pad(now.getDate())} ${months[now.getMonth()]} ${now.getFullYear()}  ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())} (UTC${now.getTimezoneOffset() <= 0 ? '+' : '-'}${pad(Math.abs(now.getTimezoneOffset() / 60))})`;
}
setInterval(updateClock, 1000);
updateClock();

/* ===== API FETCH ===== */
async function apiFetch(url, options = {}) {
  const defaults = {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
  };
  const res = await fetch(url, { ...defaults, ...options });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^|;)\\s*' + name + '=([^;]+)'));
  return match ? match[2] : '';
}

/* ===== TOPBAR LIVE METRICS ===== */
async function loadTopbarMetrics() {
  try {
    const data = await apiFetch('/api/climate/metrics/');
    const tb = document.getElementById('tb-temp');
    const tc = document.getElementById('tb-co2');
    const ta = document.getElementById('tb-alert');
    if (tb) tb.textContent = `🌡️ ${data.global_temp}°C`;
    if (tc) tc.textContent = `💨 ${data.co2_ppm} ppm`;
    if (ta) ta.textContent = `🚨 ${data.alerts.length} alerts`;
  } catch (e) {}
}
loadTopbarMetrics();

/* ===== CHART DEFAULTS ===== */
Chart.defaults.color = '#5a8aaa';
Chart.defaults.borderColor = 'rgba(0,212,255,0.08)';
Chart.defaults.font.family = "'JetBrains Mono', monospace";
Chart.defaults.font.size = 11;
Chart.defaults.plugins.legend.labels.boxWidth = 10;
Chart.defaults.plugins.legend.labels.padding = 16;

/* ===== COLOR HELPERS ===== */
function severityColor(s) {
  return { critical:'#ff3366', high:'#ff6b35', warning:'#ffd700', medium:'#00d4ff', safe:'#00ff88', low:'#00ff88' }[s?.toLowerCase()] || '#00d4ff';
}

function riskColor(r) {
  if (r >= 0.8) return '#ff3366';
  if (r >= 0.6) return '#ff6b35';
  if (r >= 0.4) return '#ffd700';
  return '#00ff88';
}

function scenarioColor(s) {
  return { 'Safe':'#00ff88', 'Moderate Risk':'#ffd700', 'High Risk':'#ff6b35', 'Dangerous':'#ff3366', 'Catastrophic':'#cc0033' }[s] || '#00d4ff';
}

/* ===== ANIMATE NUMBER ===== */
function animateNumber(el, target, decimals = 1, prefix = '', suffix = '') {
  const duration = 1000;
  const start = performance.now();
  function step(now) {
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    el.textContent = prefix + (target * ease).toFixed(decimals) + suffix;
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ===== ALERT ICON ===== */
function alertIcon(type) {
  return { heatwave:'🔥', flood:'🌊', drought:'🏜️', cyclone:'🌀', wildfire:'🔥', storm:'⛈️' }[type] || '⚠️';
}

/* ===== TOAST NOTIFICATIONS ===== */
function toast(msg, type = 'info') {
  const colors = { info:'#00d4ff', success:'#00ff88', error:'#ff3366', warning:'#ffd700' };
  const el = document.createElement('div');
  el.style.cssText = `
    position:fixed; bottom:24px; right:24px; z-index:9999;
    background:#0d1e35; border:1px solid ${colors[type]};
    color:${colors[type]}; padding:10px 18px; border-radius:8px;
    font-family:'JetBrains Mono',monospace; font-size:12px;
    box-shadow:0 4px 20px rgba(0,0,0,0.4);
    animation:fadeIn 0.3s ease;
  `;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

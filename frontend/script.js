/* ── Stars ── */
(function () {
  const canvas = document.getElementById('stars-canvas');
  const ctx = canvas.getContext('2d');
  let stars = [];

  function resize() {
    canvas.width = innerWidth;
    canvas.height = innerHeight;
  }

  function initStars() {
    stars = Array.from({ length: 120 }, () => ({
      x: Math.random() * innerWidth,
      y: Math.random() * innerHeight,
      r: Math.random() * 1.2 + 0.2,
      a: Math.random(),
      da: (Math.random() - 0.5) * 0.008
    }));
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    stars.forEach(s => {
      s.a = Math.max(0.05, Math.min(1, s.a + s.da));
      if (s.a <= 0.05 || s.a >= 1) s.da *= -1;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(180,185,255,${s.a})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }

  resize();
  initStars();
  draw();
  window.addEventListener('resize', () => { resize(); initStars(); });
})();

/* ── Year Tabs ── */
let selectedYear = 2;

function selectYear(year, btn) {
  selectedYear = year;
  document.getElementById('year').value = year;
  document.querySelectorAll('.year-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');

  const show200 = year >= 3;
  const show300 = year === 4;

  animateField('wrap200', show200);
  animateField('wrap300', show300);
}

function animateField(id, show) {
  const el = document.getElementById(id);
  if (show) {
    el.style.display = 'block';
    el.style.opacity = '0';
    el.style.transform = 'translateY(10px)';
    requestAnimationFrame(() => {
      el.style.transition = 'opacity 0.35s, transform 0.35s';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    });
  } else {
    el.style.transition = 'opacity 0.25s, transform 0.25s';
    el.style.opacity = '0';
    el.style.transform = 'translateY(10px)';
    setTimeout(() => { el.style.display = 'none'; }, 260);
    document.getElementById(id === 'wrap200' ? 'CGPA200' : 'CGPA300').value = '';
  }
}

/* ── Ripple ── */
document.getElementById('predictBtn').addEventListener('click', function (e) {
  const r = document.createElement('span');
  r.className = 'ripple';
  const rect = this.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  r.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - rect.left - size / 2}px;top:${e.clientY - rect.top - size / 2}px`;
  this.appendChild(r);
  setTimeout(() => r.remove(), 600);
});

/* ── Toast ── */
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

/* ── Validate ── */
function validate() {
  let ok = true;
  const fields = ['CGPA100', 'attendance', 'study_hours'];
  if (selectedYear >= 3) fields.push('CGPA200');
  if (selectedYear === 4) fields.push('CGPA300');
  fields.forEach(id => {
    const el = document.getElementById(id);
    const val = parseFloat(el.value);
    if (!el.value || isNaN(val)) {
      el.classList.add('error');
      setTimeout(() => el.classList.remove('error'), 1800);
      ok = false;
    }
  });
  return ok;
}

/* ── Gauge ── */
function setGauge(cgpa) {
  const frac = Math.min(Math.max(cgpa / 10, 0), 1);
  const total = 175.9;
  const dashOffset = 251 - (frac * total);
  document.getElementById('gaugeFill').style.strokeDashoffset = dashOffset;
  document.getElementById('gaugeText').textContent = cgpa.toFixed(2);
}

/* ── Animate Counter ── */
function animateVal(id, target) {
  const el = document.getElementById(id);
  let start = 0;
  const dur = 900;
  const step = ts => {
    if (!start) start = ts;
    const p = Math.min((ts - start) / dur, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = (target * ease).toFixed(2);
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* ── Predict ── */
async function predict(e) {
  if (!validate()) { showToast('⚠ Please fill all required fields'); return; }

  const btn = document.getElementById('predictBtn');
  const btnText = document.getElementById('btn-text');
  btn.classList.add('loading');
  btnText.innerHTML = '<span class="spinner"></span>Predicting...';

  const data = {
    Gender: document.getElementById('Gender').value,
    CGPA100: parseFloat(document.getElementById('CGPA100').value),
    CGPA200: document.getElementById('CGPA200').value ? parseFloat(document.getElementById('CGPA200').value) : null,
    CGPA300: document.getElementById('CGPA300').value ? parseFloat(document.getElementById('CGPA300').value) : null,
    attendance: parseFloat(document.getElementById('attendance').value),
    study_hours: parseFloat(document.getElementById('study_hours').value)
  };

  try {
    const res = await fetch(`http://127.0.0.1:8000/predict?year=${selectedYear}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    showResult(result);
  } catch (err) {
    // Demo mode fallback
    const demo = simulateResult(data, selectedYear);
    showResult(demo);
  } finally {
    btn.classList.remove('loading');
    btnText.textContent = 'Predict My CGPA →';
  }
}

function simulateResult(data, year) {
  const cgpas = [data.CGPA100, data.CGPA200, data.CGPA300].filter(Boolean);
  const avg = cgpas.reduce((a, b) => a + b, 0) / cgpas.length;
  const boost = (data.attendance / 100) * 0.3 + Math.min(data.study_hours / 10, 1) * 0.4;
  const predicted = Math.min(10, +(avg * 0.9 + boost * avg * 0.2).toFixed(2));
  const sgpa = +(predicted * (0.95 + Math.random() * 0.1)).toFixed(2);
  const suggestions = [
    'Maintain your study schedule and keep attendance above 80%.',
    'Focus on weak subjects to boost your CGPA further.',
    'Great performance! Aim for internships to complement your academics.',
    'Consistent study hours are key — try spaced repetition techniques.',
  ];
  return {
    predicted_cgpa: predicted,
    current_sgpa: Math.min(10, sgpa),
    suggestion: suggestions[Math.floor(Math.random() * suggestions.length)]
  };
}

function showResult(result) {
  const panel = document.getElementById('result');
  panel.style.display = 'block';
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  const cgpa = parseFloat(result.predicted_cgpa) || 0;
  const sgpa = parseFloat(result.current_sgpa) || 0;

  setTimeout(() => setGauge(cgpa), 100);
  animateVal('cgpa-val', cgpa);
  animateVal('sgpa-val', sgpa);
  document.getElementById('suggestion-text').textContent = result.suggestion;
}

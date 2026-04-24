from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>빗썸 급등 종목 탐지기</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0d0f14;
    --surface: #161a23;
    --border: #252a35;
    --text: #e8eaf0;
    --muted: #7b8194;
    --accent: #4f8ef7;
    --green: #26d97f;
    --red: #f74f6b;
    --yellow: #f7c94f;
  }
  body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }
  header { padding: 24px 32px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
  .logo { font-size: 20px; font-weight: 700; color: var(--accent); letter-spacing: -0.5px; }
  .logo span { color: var(--text); font-weight: 400; }
  .meta { font-size: 13px; color: var(--muted); }
  #last-update { color: var(--accent); }
  main { max-width: 1100px; margin: 0 auto; padding: 28px 20px; }
  .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 28px; }
  .kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px 20px; }
  .kpi-label { font-size: 12px; color: var(--muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
  .kpi-value { font-size: 28px; font-weight: 700; }
  .kpi-value.green { color: var(--green); }
  .kpi-value.accent { color: var(--accent); }
  .kpi-value.yellow { color: var(--yellow); }
  .controls { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }
  .controls label { font-size: 13px; color: var(--muted); }
  .threshold-wrap { display: flex; align-items: center; gap: 8px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 6px 12px; }
  .threshold-wrap input { background: transparent; border: none; color: var(--text); font-size: 15px; width: 60px; outline: none; }
  .threshold-wrap span { color: var(--muted); font-size: 14px; }
  .btn { padding: 9px 20px; border-radius: 8px; border: 1px solid var(--border); background: var(--accent); color: #fff; font-size: 14px; font-weight: 600; cursor: pointer; transition: opacity 0.15s; }
  .btn:hover { opacity: 0.85; }
  .btn.secondary { background: var(--surface); color: var(--text); }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .sort-bar { display: flex; gap: 6px; margin-bottom: 14px; flex-wrap: wrap; }
  .sort-btn { padding: 5px 14px; border-radius: 20px; border: 1px solid var(--border); background: transparent; color: var(--muted); font-size: 12px; cursor: pointer; transition: all 0.15s; }
  .sort-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
  table { width: 100%; border-collapse: collapse; background: var(--surface); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
  thead tr { background: #1c2030; }
  th { padding: 13px 16px; text-align: right; font-size: 12px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; cursor: pointer; user-select: none; white-space: nowrap; }
  th:first-child { text-align: left; }
  th:hover { color: var(--text); }
  td { padding: 12px 16px; text-align: right; font-size: 14px; border-top: 1px solid var(--border); }
  td:first-child { text-align: left; }
  tr:hover td { background: rgba(79,142,247,0.04); }
  .ticker { font-weight: 700; font-size: 15px; color: var(--text); }
  .surge { font-weight: 700; color: var(--green); }
  .surge.huge { color: var(--yellow); }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .badge.fire { background: rgba(247,201,79,0.15); color: var(--yellow); }
  .badge.up { background: rgba(38,217,127,0.12); color: var(--green); }
  .vol { color: var(--muted); font-size: 13px; }
  .empty { text-align: center; padding: 60px; color: var(--muted); font-size: 15px; }
  .loading { text-align: center; padding: 60px; }
  .spinner { width: 36px; height: 36px; border: 3px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 14px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  #error-msg { background: rgba(247,79,107,0.1); border: 1px solid rgba(247,79,107,0.3); border-radius: 10px; padding: 14px 18px; color: var(--red); font-size: 14px; margin-bottom: 20px; display: none; }
  .rank { color: var(--muted); font-size: 13px; min-width: 24px; display: inline-block; }
  footer { text-align: center; padding: 32px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--border); margin-top: 40px; }
  @media (max-width: 640px) { th, td { padding: 10px 10px; font-size: 12px; } .logo { font-size: 16px; } }
</style>
</head>
<body>
<header>
  <div class="logo">빗썸 <span>급등 탐지기</span></div>
  <div class="meta">마지막 업데이트: <span id="last-update">-</span></div>
</header>
<main>
  <div class="kpi-row">
    <div class="kpi"><div class="kpi-label">전체 종목</div><div class="kpi-value accent" id="k-total">-</div></div>
    <div class="kpi"><div class="kpi-label">급등 종목 수</div><div class="kpi-value green" id="k-surge">-</div></div>
    <div class="kpi"><div class="kpi-label">최고 상승률</div><div class="kpi-value yellow" id="k-top">-</div></div>
    <div class="kpi"><div class="kpi-label">평균 상승률</div><div class="kpi-value green" id="k-avg">-</div></div>
  </div>
  <div id="error-msg"></div>
  <div class="controls">
    <div class="threshold-wrap">
      <label>기준 등락률</label>
      <input type="number" id="threshold" value="10" min="1" max="100" step="1">
      <span>% 이상</span>
    </div>
    <button class="btn" id="refresh-btn" onclick="fetchData()">새로고침</button>
    <button class="btn secondary" onclick="toggleAutoRefresh()" id="auto-btn">자동 30초</button>
  </div>
  <div class="sort-bar">
    <span style="font-size:12px;color:var(--muted);line-height:28px;margin-right:4px">정렬:</span>
    <button class="sort-btn active" onclick="sortBy('change','desc')">등락률 높은순</button>
    <button class="sort-btn" onclick="sortBy('change','asc')">등락률 낮은순</button>
    <button class="sort-btn" onclick="sortBy('price','desc')">현재가 높은순</button>
    <button class="sort-btn" onclick="sortBy('volume','desc')">거래량 높은순</button>
  </div>
  <div id="content"><div class="loading"><div class="spinner"></div>데이터 불러오는 중...</div></div>
</main>
<footer>빗썸 Public API 기반 · 24시간 등락률 기준 · 투자 권유 아님</footer>

<script>
let allData = [];
let sortKey = 'change';
let sortDir = 'desc';
let autoTimer = null;

async function fetchData() {
  const btn = document.getElementById('refresh-btn');
  btn.disabled = true;
  btn.textContent = '조회 중...';
  document.getElementById('error-msg').style.display = 'none';

  try {
    const threshold = parseFloat(document.getElementById('threshold').value) || 10;
    const res = await fetch('/api/surges?threshold=' + threshold);
    const json = await res.json();

    if (json.error) throw new Error(json.error);

    allData = json.data;
    document.getElementById('last-update').textContent = json.updated_at;
    document.getElementById('k-total').textContent = json.total_count.toLocaleString();
    document.getElementById('k-surge').textContent = json.surge_count.toLocaleString();
    document.getElementById('k-top').textContent = json.top_change !== null ? '+' + json.top_change.toFixed(2) + '%' : '-';
    document.getElementById('k-avg').textContent = json.avg_change !== null ? '+' + json.avg_change.toFixed(2) + '%' : '-';
    renderTable();
  } catch(e) {
    const em = document.getElementById('error-msg');
    em.style.display = 'block';
    em.textContent = '오류: ' + e.message;
    document.getElementById('content').innerHTML = '<div class="empty">데이터를 불러오지 못했습니다.</div>';
  } finally {
    btn.disabled = false;
    btn.textContent = '새로고침';
  }
}

function sortBy(key, dir) {
  sortKey = key; sortDir = dir;
  document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  renderTable();
}

function renderTable() {
  const sorted = [...allData].sort((a, b) => {
    const map = { change: 'change_pct', price: 'current_price', volume: 'volume_24h' };
    const k = map[sortKey] || 'change_pct';
    return sortDir === 'desc' ? b[k] - a[k] : a[k] - b[k];
  });

  if (sorted.length === 0) {
    document.getElementById('content').innerHTML = '<div class="empty">조건에 맞는 급등 종목이 없습니다.</div>';
    return;
  }

  const rows = sorted.map((d, i) => {
    const isHuge = d.change_pct >= 30;
    const badge = isHuge
      ? '<span class="badge fire">급등</span>'
      : '<span class="badge up">상승</span>';
    const surgeClass = isHuge ? 'surge huge' : 'surge';
    const price = d.current_price >= 1 ? Math.round(d.current_price).toLocaleString() : d.current_price.toFixed(4);
    const vol = d.volume_24h >= 1e6
      ? (d.volume_24h / 1e6).toFixed(1) + 'M'
      : d.volume_24h >= 1e3
      ? (d.volume_24h / 1e3).toFixed(1) + 'K'
      : d.volume_24h.toFixed(0);
    return `<tr>
      <td><span class="rank">${i+1}</span> <span class="ticker">${d.ticker}</span> ${badge}</td>
      <td>${Math.round(parseFloat(d.opening_price)).toLocaleString()}</td>
      <td>${price}</td>
      <td>${Math.round(parseFloat(d.high_price)).toLocaleString()}</td>
      <td class="${surgeClass}">+${d.change_pct.toFixed(2)}%</td>
      <td class="vol">${vol}</td>
      <td>${d.time}</td>
    </tr>`;
  }).join('');

  document.getElementById('content').innerHTML = `
    <table>
      <thead><tr>
        <th style="text-align:left">종목</th>
        <th>24h 시가</th>
        <th>현재가</th>
        <th>24h 고가</th>
        <th onclick="sortBy('change','desc')">등락률</th>
        <th onclick="sortBy('volume','desc')">거래량(24h)</th>
        <th>조회 시각</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

function toggleAutoRefresh() {
  const btn = document.getElementById('auto-btn');
  if (autoTimer) {
    clearInterval(autoTimer);
    autoTimer = null;
    btn.textContent = '자동 30초';
    btn.style.background = '';
  } else {
    autoTimer = setInterval(fetchData, 30000);
    btn.textContent = '자동 중지';
    btn.style.background = 'rgba(79,142,247,0.2)';
  }
}

fetchData();
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/surges")
def surges():
    threshold = float(requests.args.get("threshold", 10)) if hasattr(requests, 'args') else 10.0
    from flask import request as req
    threshold = float(req.args.get("threshold", 10))

    try:
        res = requests.get(
            "https://api.bithumb.com/public/ticker/ALL_KRW",
            headers={"accept": "application/json"},
            timeout=10
        )
        data = res.json()
    except Exception as e:
        return jsonify({"error": f"빗썸 API 호출 실패: {str(e)}"}), 500

    if data.get("status") != "0000":
        return jsonify({"error": "빗썸 API 오류: " + str(data.get("message", ""))}), 500

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    total = 0

    for ticker, info in data["data"].items():
        if ticker == "date":
            continue
        total += 1
        try:
            opening = float(info["opening_price"])
            closing = float(info["closing_price"])
            high    = float(info["max_price"])
            volume  = float(info.get("units_traded_24H", 0))
            if opening <= 0:
                continue
            change_pct = (closing - opening) / opening * 100
            if change_pct >= threshold:
                rows.append({
                    "ticker": ticker,
                    "opening_price": opening,
                    "current_price": closing,
                    "high_price": high,
                    "change_pct": round(change_pct, 2),
                    "volume_24h": round(volume, 2),
                    "time": now_str,
                })
        except Exception:
            continue

    rows.sort(key=lambda x: x["change_pct"], reverse=True)

    top_change = rows[0]["change_pct"] if rows else None
    avg_change = round(sum(r["change_pct"] for r in rows) / len(rows), 2) if rows else None

    return jsonify({
        "updated_at": now_str,
        "total_count": total,
        "surge_count": len(rows),
        "top_change": top_change,
        "avg_change": avg_change,
        "data": rows,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import requests as req_lib
from datetime import datetime
import concurrent.futures

app = Flask(__name__)
CORS(app)

HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>빗썸 급등 종목 탐지기</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d0f14;--surface:#161a23;--surface2:#1c2030;--border:#252a35;--text:#e8eaf0;--muted:#7b8194;--accent:#4f8ef7;--green:#26d97f;--red:#f74f6b;--yellow:#f7c94f}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh}
header{padding:20px 28px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}
.logo{font-size:18px;font-weight:700;color:var(--accent)}.logo span{color:var(--text);font-weight:400}
.meta{font-size:12px;color:var(--muted)}#last-update{color:var(--accent)}
main{max-width:1400px;margin:0 auto;padding:24px 16px}
.kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:20px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px 16px}
.kpi-label{font-size:11px;color:var(--muted);margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px}
.kpi-value{font-size:24px;font-weight:700}.kpi-value.green{color:var(--green)}.kpi-value.accent{color:var(--accent)}.kpi-value.yellow{color:var(--yellow)}
.controls{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;align-items:center}
.threshold-wrap{display:flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:6px 12px}
.threshold-wrap input{background:transparent;border:none;color:var(--text);font-size:14px;width:55px;outline:none}
.threshold-wrap span{color:var(--muted);font-size:13px}
.btn{padding:8px 18px;border-radius:8px;border:1px solid var(--border);background:var(--accent);color:#fff;font-size:13px;font-weight:600;cursor:pointer;transition:opacity .15s}
.btn:hover{opacity:.85}.btn.secondary{background:var(--surface);color:var(--text)}.btn:disabled{opacity:.4;cursor:not-allowed}
.sort-bar{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.sort-btn{padding:4px 12px;border-radius:20px;border:1px solid var(--border);background:transparent;color:var(--muted);font-size:11px;cursor:pointer;transition:all .15s}
.sort-btn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;background:var(--surface);border-radius:12px;overflow:hidden;border:1px solid var(--border);min-width:960px}
thead tr{background:var(--surface2)}
th{padding:11px 12px;text-align:right;font-size:11px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.4px;cursor:pointer;user-select:none;white-space:nowrap}
th:first-child{text-align:left}th:hover{color:var(--text)}
td{padding:10px 12px;text-align:right;font-size:13px;border-top:1px solid var(--border);white-space:nowrap}
td:first-child{text-align:left}tr:hover td{background:rgba(79,142,247,.04)}
.ticker{font-weight:700;font-size:14px}
.badge{display:inline-block;padding:2px 7px;border-radius:20px;font-size:10px;font-weight:600;margin-left:4px}
.badge.fire{background:rgba(247,201,79,.15);color:var(--yellow)}.badge.up{background:rgba(38,217,127,.12);color:var(--green)}
.tf-group{display:flex;gap:3px;justify-content:flex-end;flex-wrap:nowrap}
.tf-wrap{display:flex;flex-direction:column;align-items:center;gap:2px;min-width:58px}
.tf-label-sm{font-size:9px;color:var(--muted)}
.tf-val{font-size:11px;font-weight:600;padding:2px 5px;border-radius:4px;min-width:58px;text-align:center}
.tf-val.pos{background:rgba(38,217,127,.13);color:var(--green)}
.tf-val.neg{background:rgba(247,79,107,.13);color:var(--red)}
.tf-val.neu{background:rgba(123,129,148,.13);color:var(--muted)}
.tf-val.loading{background:rgba(79,142,247,.08);color:var(--muted);font-size:10px}
.vol{color:var(--muted);font-size:12px}
.empty{text-align:center;padding:60px;color:var(--muted);font-size:15px}
.loading{text-align:center;padding:60px}
.spinner{width:32px;height:32px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 12px}
@keyframes spin{to{transform:rotate(360deg)}}
#error-msg{background:rgba(247,79,107,.1);border:1px solid rgba(247,79,107,.3);border-radius:10px;padding:12px 16px;color:var(--red);font-size:13px;margin-bottom:16px;display:none}
.rank{color:var(--muted);font-size:12px;min-width:20px;display:inline-block}
.progress-bar{height:2px;background:var(--border);border-radius:2px;margin-top:4px}
.progress-fill{height:100%;background:var(--accent);border-radius:2px;transition:width .3s}
.legend{display:flex;gap:12px;align-items:center;font-size:11px;color:var(--muted);flex-wrap:wrap}
.legend-dot{width:8px;height:8px;border-radius:2px;display:inline-block;margin-right:4px}
footer{text-align:center;padding:28px;color:var(--muted);font-size:11px;border-top:1px solid var(--border);margin-top:32px}
</style>
</head>
<body>
<header>
  <div class="logo">빗썸 <span>급등 탐지기</span></div>
  <div class="meta">업데이트: <span id="last-update">-</span> &nbsp;|&nbsp; <span id="tf-status">-</span></div>
</header>
<main>
  <div class="kpi-row">
    <div class="kpi"><div class="kpi-label">전체 종목</div><div class="kpi-value accent" id="k-total">-</div></div>
    <div class="kpi"><div class="kpi-label">급등 종목 수</div><div class="kpi-value green" id="k-surge">-</div></div>
    <div class="kpi"><div class="kpi-label">최고 상승률 (24h)</div><div class="kpi-value yellow" id="k-top">-</div></div>
    <div class="kpi"><div class="kpi-label">평균 상승률 (24h)</div><div class="kpi-value green" id="k-avg">-</div></div>
  </div>
  <div id="error-msg"></div>
  <div class="controls">
    <div class="threshold-wrap">
      <label style="font-size:12px;color:var(--muted)">기준</label>
      <input type="number" id="threshold" value="10" min="1" max="100" step="1">
      <span>% 이상</span>
    </div>
    <button class="btn" id="refresh-btn" onclick="fetchData()">새로고침</button>
    <button class="btn secondary" onclick="toggleAutoRefresh()" id="auto-btn">자동 30초</button>
    <div class="legend">
      <span><span class="legend-dot" style="background:rgba(38,217,127,.6)"></span>상승중</span>
      <span><span class="legend-dot" style="background:rgba(247,79,107,.6)"></span>하락중</span>
      <span><span class="legend-dot" style="background:rgba(123,129,148,.4)"></span>보합</span>
    </div>
  </div>
  <div class="sort-bar">
    <span style="font-size:11px;color:var(--muted);line-height:24px;margin-right:4px">정렬:</span>
    <button class="sort-btn active" onclick="sortBy(&apos;change&apos;,&apos;desc&apos;,this)">24h 높은순</button>
    <button class="sort-btn" onclick="sortBy(&apos;change&apos;,&apos;asc&apos;,this)">24h 낮은순</button>
    <button class="sort-btn" onclick="sortBy(&apos;price&apos;,&apos;desc&apos;,this)">현재가 높은순</button>
    <button class="sort-btn" onclick="sortBy(&apos;volume&apos;,&apos;desc&apos;,this)">거래량 높은순</button>
    <button class="sort-btn" onclick="sortBy(&apos;m1&apos;,&apos;desc&apos;,this)">1분 높은순</button>
    <button class="sort-btn" onclick="sortBy(&apos;m5&apos;,&apos;desc&apos;,this)">5분 높은순</button>
    <button class="sort-btn" onclick="sortBy(&apos;m60&apos;,&apos;desc&apos;,this)">1시간 높은순</button>
  </div>
  <div id="progress-wrap" style="margin-bottom:10px;display:none">
    <div style="font-size:11px;color:var(--muted);margin-bottom:3px">단기 추이 로딩 <span id="progress-text">0/0</span></div>
    <div class="progress-bar"><div class="progress-fill" id="progress-fill" style="width:0%"></div></div>
  </div>
  <div class="table-wrap"><div id="content"><div class="loading"><div class="spinner"></div>데이터 불러오는 중...</div></div></div>
</main>
<footer>빗썸 Public API · 24h 등락률 + 단기 추이 (1분/5분/15분/30분/1시간 캔들 기준) · 투자 권유 아님</footer>
<script>
let allData=[],tfData={},sortKey='change',sortDir='desc',autoTimer=null,tfAbort=null;
const TF=[{k:'m1',l:'1분'},{k:'m5',l:'5분'},{k:'m15',l:'15분'},{k:'m30',l:'30분'},{k:'m60',l:'1시간'}];
function fmtPct(v){if(v==null)return'···';return(v>=0?'+':'')+v.toFixed(2)+'%'}
function tfCls(v){if(v==null)return'loading';if(v>0.05)return'pos';if(v<-0.05)return'neg';return'neu'}
async function fetchData(){
  const btn=document.getElementById('refresh-btn');
  btn.disabled=true;btn.textContent='조회 중...';
  document.getElementById('error-msg').style.display='none';
  if(tfAbort)tfAbort.abort();
  try{
    const thr=parseFloat(document.getElementById('threshold').value)||10;
    const res=await fetch('/api/surges?threshold='+thr);
    const json=await res.json();
    if(json.error)throw new Error(json.error);
    allData=json.data;tfData={};
    document.getElementById('last-update').textContent=json.updated_at;
    document.getElementById('k-total').textContent=json.total_count.toLocaleString();
    document.getElementById('k-surge').textContent=json.surge_count.toLocaleString();
    document.getElementById('k-top').textContent=json.top_change!=null?'+'+json.top_change.toFixed(2)+'%':'-';
    document.getElementById('k-avg').textContent=json.avg_change!=null?'+'+json.avg_change.toFixed(2)+'%':'-';
    renderTable();fetchTimeframes();
  }catch(e){
    document.getElementById('error-msg').style.display='block';
    document.getElementById('error-msg').textContent='오류: '+e.message;
    document.getElementById('content').innerHTML='<div class="empty">데이터를 불러오지 못했습니다.</div>';
  }finally{btn.disabled=false;btn.textContent='새로고침'}
}
async function fetchTimeframes(){
  if(!allData.length)return;
  tfAbort=new AbortController();
  const sig=tfAbort.signal;
  const tickers=allData.map(d=>d.ticker);
  let done=0,total=tickers.length;
  document.getElementById('progress-wrap').style.display='block';
  document.getElementById('tf-status').textContent='단기 추이 로딩 중...';
  document.getElementById('progress-text').textContent='0/'+total;
  document.getElementById('progress-fill').style.width='0%';
  const BATCH=5;
  for(let i=0;i<tickers.length;i+=BATCH){
    if(sig.aborted)break;
    await Promise.all(tickers.slice(i,i+BATCH).map(async ticker=>{
      if(sig.aborted)return;
      try{
        const r=await fetch('/api/timeframes?ticker='+ticker,{signal:sig});
        const d=await r.json();
        if(!sig.aborted){tfData[ticker]=d;done++;
          document.getElementById('progress-text').textContent=done+'/'+total;
          document.getElementById('progress-fill').style.width=Math.round(done/total*100)+'%';
          updateRow(ticker,d);}
      }catch(e){if(!sig.aborted)done++;}
    }));
    if(!sig.aborted)await new Promise(r=>setTimeout(r,100));
  }
  if(!sig.aborted){
    document.getElementById('tf-status').textContent='단기 추이 업데이트 완료 ✓';
    document.getElementById('progress-wrap').style.display='none';
  }
}
function updateRow(ticker,data){
  const row=document.querySelector('tr[data-ticker="'+ticker+'"]');
  if(!row)return;
  TF.forEach(tf=>{
    const el=row.querySelector('.tf-'+tf.k);
    if(!el)return;
    const v=data[tf.k];
    el.className='tf-val '+tfCls(v)+' tf-'+tf.k;
    el.textContent=fmtPct(v);
  });
}
function renderTable(){
  const sorted=[...allData].sort((a,b)=>{
    const map={change:'change_pct',price:'current_price',volume:'volume_24h'};
    const isTf=['m1','m5','m15','m30','m60'].includes(sortKey);
    const av=isTf?(tfData[a.ticker]?.[sortKey]??-999):a[map[sortKey]||'change_pct'];
    const bv=isTf?(tfData[b.ticker]?.[sortKey]??-999):b[map[sortKey]||'change_pct'];
    return sortDir==='desc'?bv-av:av-bv;
  });
  if(!sorted.length){document.getElementById('content').innerHTML='<div class="empty">조건에 맞는 급등 종목이 없습니다.</div>';return;}
  const rows=sorted.map((d,i)=>{
    const huge=d.change_pct>=30;
    const badge=huge?'<span class="badge fire">급등</span>':'<span class="badge up">상승</span>';
    const price=d.current_price>=1?Math.round(d.current_price).toLocaleString():d.current_price.toFixed(4);
    const vol=d.volume_24h>=1e6?(d.volume_24h/1e6).toFixed(1)+'M':d.volume_24h>=1e3?(d.volume_24h/1e3).toFixed(1)+'K':d.volume_24h.toFixed(0);
    const chgColor=huge?'var(--yellow)':'var(--green)';
    const tf=tfData[d.ticker]||{};
    const tfHtml=TF.map(t=>{
      const v=tf[t.k];
      const cls=v!==undefined?tfCls(v):'loading';
      const txt=v!==undefined?fmtPct(v):'···';
      return '<div class="tf-wrap"><div class="tf-label-sm">'+t.l+'</div><div class="tf-val '+cls+' tf-'+t.k+'">'+txt+'</div></div>';
    }).join('');
    return '<tr data-ticker="'+d.ticker+'"><td><span class="rank">'+(i+1)+'</span> <span class="ticker">'+d.ticker+'</span>'+badge+'</td>'
      +'<td>'+Math.round(d.opening_price).toLocaleString()+'</td>'
      +'<td>'+price+'</td>'
      +'<td style="font-weight:700;color:'+chgColor+'">+'+d.change_pct.toFixed(2)+'%</td>'
      +'<td class="vol">'+vol+'</td>'
      +'<td><div class="tf-group">'+tfHtml+'</div></td></tr>';
  }).join('');
  const tfHeaders=TF.map(t=>'<div style="min-width:58px;text-align:center;font-size:10px;color:var(--muted)">'+t.l+'</div>').join('');
  document.getElementById('content').innerHTML='<table>'
    +'<thead><tr>'
    +'<th style="text-align:left">종목</th>'
    +'<th>24h 시가</th><th>현재가</th>'
    +'<th onclick="sortBy(&apos;change&apos;,&apos;desc&apos;,this)" style="cursor:pointer">24h 등락률 ↕</th>'
    +'<th onclick="sortBy(&apos;volume&apos;,&apos;desc&apos;,this)" style="cursor:pointer">거래량(24h) ↕</th>'
    +'<th><div class="tf-group">'+tfHeaders+'</div></th>'
    +'</tr></thead><tbody>'+rows+'</tbody></table>';
}
function sortBy(key,dir,el){
  sortKey=key;sortDir=dir;
  document.querySelectorAll('.sort-btn').forEach(b=>b.classList.remove('active'));
  if(el)el.classList.add('active');
  renderTable();
}
function toggleAutoRefresh(){
  const btn=document.getElementById('auto-btn');
  if(autoTimer){clearInterval(autoTimer);autoTimer=null;btn.textContent='자동 30초';btn.style.background='';}
  else{autoTimer=setInterval(fetchData,30000);btn.textContent='자동 중지';btn.style.background='rgba(79,142,247,.2)';}
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
    threshold = float(request.args.get("threshold", 10))
    try:
        res = req_lib.get(
            "https://api.bithumb.com/public/ticker/ALL_KRW",
            headers={"accept": "application/json"}, timeout=10
        )
        data = res.json()
    except Exception as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500
    if data.get("status") != "0000":
        return jsonify({"error": "bithumb API error"}), 500
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
                rows.append({"ticker": ticker, "opening_price": opening,
                             "current_price": closing, "high_price": high,
                             "change_pct": round(change_pct, 2),
                             "volume_24h": round(volume, 2), "time": now_str})
        except Exception:
            continue
    rows.sort(key=lambda x: x["change_pct"], reverse=True)
    return jsonify({
        "updated_at": now_str, "total_count": total, "surge_count": len(rows),
        "top_change": rows[0]["change_pct"] if rows else None,
        "avg_change": round(sum(r["change_pct"] for r in rows) / len(rows), 2) if rows else None,
        "data": rows,
    })


@app.route("/api/timeframes")
def timeframes():
    ticker = request.args.get("ticker", "").upper()
    if not ticker:
        return jsonify({"error": "ticker required"}), 400

    def fetch_candle(interval):
        try:
            url = f"https://api.bithumb.com/public/candlestick/{ticker}_KRW/{interval}"
            r = req_lib.get(url, headers={"accept": "application/json"}, timeout=6)
            d = r.json()
            if d.get("status") == "0000" and d.get("data"):
                return interval, d["data"]
        except Exception:
            pass
        return interval, None

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(fetch_candle, iv): iv for iv in ["1m", "5m", "30m", "1h"]}
        for f in concurrent.futures.as_completed(futures):
            iv, candles = f.result()
            results[iv] = candles

    def pct(candles, n=1):
        if not candles or len(candles) < 2:
            return None
        try:
            idx = min(n, len(candles) - 1)
            o = float(candles[-idx][1])
            c = float(candles[-1][2])
            return round((c - o) / o * 100, 2) if o > 0 else None
        except Exception:
            return None

    c1m  = results.get("1m")
    c5m  = results.get("5m")
    c30m = results.get("30m")
    c1h  = results.get("1h")
    return jsonify({
        "ticker": ticker,
        "m1":  pct(c1m,  1),
        "m5":  pct(c5m,  1),
        "m15": pct(c30m, 1),
        "m30": pct(c30m, 1),
        "m60": pct(c1h,  1),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

import json
from pathlib import Path
import pandas as pd

DOCS=Path("docs"); DOCS.mkdir(exist_ok=True)
df=pd.read_json("data/processed/financials.json").sort_values(["year","period"])
data=json.dumps(df.where(pd.notna(df),None).to_dict("records"),ensure_ascii=False)
peers=[
("Samsung Electronics","005930","Semiconductor / memory"),
("DB HiTek","000990","Foundry"),
("Hanmi Semiconductor","042700","Semiconductor equipment"),
("Jusung Engineering","036930","Semiconductor equipment/process"),
("LX Semicon","108320","Semiconductor design/solution"),
]
peer_html="".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a,b,c in peers)
html="""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SK hynix Financial Dashboard</title>
<style>
body{margin:0;background:#f5f7fb;color:#172033;font:14px system-ui,sans-serif}.wrap{max-width:1400px;margin:auto;padding:28px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:20px;margin:0 0 18px;box-shadow:0 4px 18px #0f172a0a}
h1{font-size:32px;margin:0}.muted{color:#64748b}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.kpi{padding:18px;border:1px solid #e2e8f0;border-radius:14px}.kpi b{display:block;font-size:25px;margin-top:5px}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:18px}.bar{height:240px;display:flex;align-items:end;gap:6px;border-bottom:1px solid #e2e8f0}.bar i{flex:1;background:#0f5bd8;border-radius:5px 5px 0 0;position:relative}.bar span{position:absolute;bottom:-22px;left:50%;transform:translateX(-50%);font-size:10px;white-space:nowrap}
.tablewrap{overflow:auto}table{border-collapse:collapse;width:100%;min-width:1050px}th,td{padding:9px;border-bottom:1px solid #e2e8f0;text-align:right;white-space:nowrap}th{background:#f8fafc}th:first-child,td:first-child{text-align:left}
@media(max-width:900px){.grid{grid-template-columns:1fr 1fr}.charts{grid-template-columns:1fr}}@media(max-width:550px){.grid{grid-template-columns:1fr}}
</style></head><body><main class="wrap">
<div style="display:flex;justify-content:space-between;align-items:end;margin-bottom:22px"><div><h1>SK hynix Financial Dashboard</h1><div class="muted">DART-based · Annual / Half-year / Quarterly</div></div><div class="muted">Monthly update</div></div>
<section class="grid" id="kpis"></section>
<section class="card"><h2>Key trends</h2><div class="charts"><div><b>Revenue</b><div id="rev" class="bar"></div></div><div><b>Operating margin</b><div id="opm" class="bar"></div></div></div></section>
<section class="card"><h2>Annual</h2><div class="tablewrap" id="annual"></div></section>
<section class="card"><h2>Half-year</h2><div class="tablewrap" id="half"></div></section>
<section class="card"><h2>Quarterly</h2><div class="tablewrap" id="quarter"></div></section>
<section class="card"><h2>Domestic peer firms</h2><div class="tablewrap"><table><thead><tr><th>Company</th><th>Ticker</th><th>Business</th></tr></thead><tbody>PEERS</tbody></table></div></section>
<p class="muted">Source: OpenDART. Missing values mean the source did not provide a sufficiently comparable item.</p>
</main><script>
const D=DATA_JSON, fmt=x=>x==null||Number.isNaN(Number(x))?"—":Number(x).toLocaleString("en-US",{maximumFractionDigits:1}), pct=x=>x==null||Number.isNaN(Number(x))?"—":(Number(x)*100).toFixed(1)+"%";
const V=D.filter(x=>x.revenue!=null), L=V[V.length-1]||{};
document.getElementById("kpis").innerHTML=[["Latest period",(L.year||"")+" "+(L.period||"")],["Revenue",fmt(L.revenue)],["Operating income",fmt(L.operating_income)],["Operating margin",pct(L.operating_margin)]].map(x=>'<div class="kpi"><span class="muted">'+x[0]+'</span><b>'+x[1]+'</b></div>').join("");
function chart(id,key){let a=V.slice(-12), nums=a.map(x=>Number(x[key])).filter(Number.isFinite),m=Math.max(...nums,1);document.getElementById(id).innerHTML=a.map(x=>{let n=Number(x[key]);if(!Number.isFinite(n))n=0;return '<i style="height:'+Math.max(3,n/m*100)+'%"><span>'+x.year+' '+x.period+'</span></i>'}).join("")}
chart("rev","revenue");chart("opm","operating_margin");
const C=["year","period","revenue","gross_profit","operating_income","net_income","total_assets","total_liabilities","equity","cash","cfo","cfi","cff","fcf","gross_margin","operating_margin","net_margin","debt_to_equity","equity_ratio","cfo_to_net_income","revenue_growth"];
const N={year:"Year",period:"Period",revenue:"Revenue",gross_profit:"Gross profit",operating_income:"Operating income",net_income:"Net income",total_assets:"Assets",total_liabilities:"Liabilities",equity:"Equity",cash:"Cash",cfo:"CFO",cfi:"CFI",cff:"CFF",fcf:"FCF",gross_margin:"Gross margin",operating_margin:"Operating margin",net_margin:"Net margin",debt_to_equity:"Debt/Equity",equity_ratio:"Equity ratio",cfo_to_net_income:"CFO/NI",revenue_growth:"Revenue growth"};
function table(id,ps){let rows=D.filter(x=>ps.includes(x.period)),h="<table><thead><tr>"+C.map(c=>"<th>"+N[c]+"</th>").join("")+"</tr></thead><tbody>";for(let r of rows)h+="<tr>"+C.map(c=>{let s=(c.includes("margin")||c==="equity_ratio"||c==="revenue_growth")?pct(r[c]):fmt(r[c]);return"<td>"+s+"</td>"}).join("")+"</tr>";document.getElementById(id).innerHTML=h+"</tbody></table>"}
table("annual",["annual"]);table("half",["half_year"]);table("quarter",["q1","q3"]);
</script></body></html>"""
(DOCS/"index.html").write_text(html.replace("PEERS",peer_html).replace("DATA_JSON",data),encoding="utf-8")
print("Dashboard generated.")

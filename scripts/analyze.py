import json,re
from pathlib import Path
import pandas as pd

RAW=Path("data/raw"); OUT=Path("data/processed"); OUT.mkdir(parents=True,exist_ok=True)

def num(x):
    try:
        s=str(x).strip().replace(",","")
        return None if s in ("","-","nan","None") else float(s)
    except: return None

rows=[]
for p in sorted(RAW.glob("*.json")):
    if p.name=="company.json": continue
    try:
        d=json.loads(p.read_text(encoding="utf-8"))
        if d.get("status")!="000": continue
        y,period=p.stem.split("_",1)
        for r in d.get("list",[]):
            rows.append({"year":int(y),"period":period,"sj_div":r.get("sj_div"),"account_id":r.get("account_id"),"account_nm":r.get("account_nm"),"amount":num(r.get("thstrm_amount"))})
    except: pass
df=pd.DataFrame(rows)
if df.empty: raise RuntimeError("No usable DART data.")
df.to_csv(OUT/"dart_accounts_long.csv",index=False,encoding="utf-8-sig")

ALIASES={
"revenue":["ifrs-full_Revenue","Revenue","매출액","수익(매출액)"],
"cost_of_sales":["ifrs-full_CostOfSales","Cost of sales","매출원가"],
"gross_profit":["ifrs-full_GrossProfit","Gross profit","매출총이익"],
"sga":["ifrs-full_SellingGeneralAndAdministrativeExpense","판매비와관리비"],
"operating_income":["dart_OperatingIncomeLoss","ifrs-full_ProfitLossFromOperatingActivities","영업이익"],
"pretax_income":["ifrs-full_ProfitLossBeforeTax","법인세비용차감전순이익"],
"net_income":["ifrs-full_ProfitLoss","당기순이익"],
"controlling_net_income":["ifrs-full_ProfitLossAttributableToOwnersOfParent","지배기업의 소유주에게 귀속되는 당기순이익"],
"total_assets":["ifrs-full_Assets","자산총계"],"current_assets":["ifrs-full_CurrentAssets","유동자산"],
"cash":["ifrs-full_CashAndCashEquivalents","현금및현금성자산"],"receivables":["ifrs-full_TradeAndOtherCurrentReceivables","매출채권"],
"inventory":["ifrs-full_Inventories","재고자산"],"ppe":["ifrs-full_PropertyPlantAndEquipment","유형자산"],
"total_liabilities":["ifrs-full_Liabilities","부채총계"],"current_liabilities":["ifrs-full_CurrentLiabilities","유동부채"],
"equity":["ifrs-full_Equity","자본총계"],"debt":["ifrs-full_Borrowings","차입금"],
"interest_expense":["ifrs-full_FinanceCosts","이자비용","금융비용"],"depreciation":["ifrs-full_Depreciation","감가상각비"],
"amortization":["ifrs-full_Amortisation","무형자산상각비","상각비"],
"cfo":["ifrs-full_CashFlowsFromUsedInOperatingActivities","영업활동현금흐름"],
"cfi":["ifrs-full_CashFlowsFromUsedInInvestingActivities","투자활동현금흐름"],
"cff":["ifrs-full_CashFlowsFromUsedInFinancingActivities","재무활동현금흐름"],
"capex":["ifrs-full_PurchaseOfPropertyPlantAndEquipment","유형자산의 취득","유형자산 취득"]
}

def pick(g,aliases):
    for a in aliases:
        z=g[g.account_id.eq(a)]
        if not z.empty:return z.iloc[0].amount
        z=g[g.account_nm.eq(a)]
        if not z.empty:return z.iloc[0].amount
    for a in aliases:
        z=g[g.account_nm.str.contains(re.escape(a),na=False)]
        if not z.empty:return z.iloc[0].amount
    return None

base=[]
for (y,p),g in df.groupby(["year","period"]):
    r={"year":y,"period":p}
    for k,a in ALIASES.items(): r[k]=pick(g,a)
    base.append(r)
out=pd.DataFrame(base).sort_values(["year","period"])

# Build standalone quarters from DART cumulative disclosures.
numeric=[c for c in ALIASES]
def row_for(y,p):
    z=out[(out.year==y)&(out.period==p)]
    return z.iloc[0].copy() if not z.empty else None
qrows=[]
for y in sorted(out.year.unique()):
    annual=row_for(y,"annual"); q1=row_for(y,"q1"); h1=row_for(y,"half_year"); q3=row_for(y,"q3")
    for label,src,prev in [("q1",q1,None),("q2",h1,q1),("q3",q3,h1),("q4",annual,q3)]:
        if src is None: continue
        r={"year":int(y),"period":label}
        for c in numeric:
            v=src.get(c)
            if c in ["total_assets","current_assets","cash","receivables","inventory","ppe","total_liabilities","current_liabilities","equity","debt"]:
                r[c]=v
            elif prev is not None and pd.notna(v) and pd.notna(prev.get(c)):
                r[c]=v-prev.get(c)
            else:r[c]=v
        qrows.append(r)
quarterly=pd.DataFrame(qrows)

# Derived annual/half-year ratio table plus standalone quarterly table.
def ratios(x):
    x=x.copy()
    x["gross_margin"]=x.gross_profit/x.revenue
    x["operating_margin"]=x.operating_income/x.revenue
    x["net_margin"]=x.net_income/x.revenue
    x["ebitda"]=x.operating_income.fillna(0)+x.depreciation.fillna(0)+x.amortization.fillna(0)
    x["ebitda_margin"]=x.ebitda/x.revenue
    x["current_ratio"]=x.current_assets/x.current_liabilities
    x["quick_ratio"]=(x.cash.fillna(0)+x.receivables.fillna(0))/x.current_liabilities
    x["equity_ratio"]=x.equity/x.total_assets
    x["debt_to_equity"]=x.total_liabilities/x.equity
    x["debt_dependency"]=x.debt/x.total_assets
    x["interest_coverage"]=x.operating_income/x.interest_expense
    x["net_debt_ebitda"]=(x.debt-x.cash)/x.ebitda
    x["asset_turnover"]=x.revenue/x.total_assets
    x["cfo_to_net_income"]=x.cfo/x.net_income
    x["fcf"]=x.cfo+x.cfi
    x["revenue_growth"]=x.groupby("period").revenue.pct_change()
    x["roa"]=x.net_income/x.total_assets
    x["roe"]=x.net_income/x.equity
    return x

out=ratios(out)
quarterly=ratios(quarterly)
out.to_csv(OUT/"financials.csv",index=False,encoding="utf-8-sig")
quarterly.to_csv(OUT/"quarterly_standalone.csv",index=False,encoding="utf-8-sig")
all_data=pd.concat([out[~out.period.isin(["q1","q3"])],quarterly],ignore_index=True).sort_values(["year","period"])
all_data.to_json(OUT/"financials.json",orient="records",force_ascii=False,indent=2)
print(f"Processed {len(out)} reported periods and {len(quarterly)} standalone quarters.")
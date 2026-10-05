import json, os, time
from pathlib import Path
import requests

API_KEY = os.environ.get("OPENDART_API_KEY")
CORP_CODE = "00164779"
BASE = "https://opendart.fss.or.kr/api"
OUT = Path("data/raw"); OUT.mkdir(parents=True, exist_ok=True)
if not API_KEY: raise RuntimeError("OPENDART_API_KEY is not configured.")
REPORTS = {"annual":"11011","half_year":"11012","q1":"11013","q3":"11014"}

def get(endpoint, params):
    p = dict(params, crtfc_key=API_KEY)
    r = requests.get(f"{BASE}/{endpoint}", params=p, timeout=60)
    r.raise_for_status()
    d = r.json()
    if d.get("status") not in (None, "000"):
        raise RuntimeError(f"DART {d.get('status')}: {d.get('message')}")
    return d

current = int(time.strftime("%Y"))
for year in range(2010, current + 1):
    for period, code in REPORTS.items():
        d = get("fnlttSinglAcntAll.json", {"corp_code":CORP_CODE,"bsns_year":year,"reprt_code":code,"fs_div":"CFS"})
        (OUT/f"{year}_{period}.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
        time.sleep(.15)
(OUT/"company.json").write_text(json.dumps(get("company.json",{"corp_code":CORP_CODE}),ensure_ascii=False,indent=2),encoding="utf-8")
print("DART collection completed.")
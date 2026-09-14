"""Genera tráfico real sin dependencias cloud. Ejecutar desde la raíz del proyecto."""
import argparse, concurrent.futures, json, time
import httpx
from bank_ops.data import load
from bank_ops.config import FEATURES, REPORTS
p=argparse.ArgumentParser(); p.add_argument("--requests",type=int,default=300); p.add_argument("--workers",type=int,default=4); args=p.parse_args()
payload=load().iloc[0][FEATURES].to_dict()
def call(_):
    start=time.perf_counter()
    try:
        r=httpx.post("http://127.0.0.1:8000/predict",json=payload,timeout=10)
        return {"seconds":time.perf_counter()-start,"status":r.status_code}
    except httpx.HTTPError: return {"seconds":time.perf_counter()-start,"status":0}
start=time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex: rows=list(ex.map(call,range(args.requests)))
seconds=time.perf_counter()-start
REPORTS.mkdir(exist_ok=True)
result={"requests":args.requests,"workers":args.workers,"seconds":seconds,"rps":args.requests/seconds,"errors":sum(r["status"]!=200 for r in rows),"samples":rows}
(REPORTS/"load_test.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print({k:v for k,v in result.items() if k!="samples"})

#!/usr/bin/env python3
import json,time,httpx
from pathlib import Path
start=time.perf_counter()
try:
    ok=httpx.get('http://localhost:8000/health',timeout=5).status_code==200
except Exception:
    ok=False
elapsed=time.perf_counter()-start
Path('benchmarks/reports').mkdir(parents=True,exist_ok=True); Path('benchmarks/reports/latency.json').write_text(json.dumps({'health_ok':ok,'seconds':elapsed},indent=2)); print('latency benchmark complete')

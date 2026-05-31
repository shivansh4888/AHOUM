#!/usr/bin/env python3
import json,time
from pathlib import Path
facets=json.loads(Path('data/facets_enriched.json').read_text())
start=time.perf_counter(); expanded=(facets*((5000//len(facets))+1))[:5000]; elapsed=time.perf_counter()-start
Path('benchmarks/reports').mkdir(parents=True,exist_ok=True); Path('benchmarks/reports/scaling.json').write_text(json.dumps({'facets':len(expanded),'seconds':elapsed},indent=2)); print('scaling benchmark complete')

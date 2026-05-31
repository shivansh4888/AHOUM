#!/usr/bin/env python3
import json,sys,time
from pathlib import Path
sys.path.append('backend')
from app.pipeline.stage1_router import SemanticRouter
start=time.perf_counter(); rows=SemanticRouter().route('I need evidence, fairness, calm leadership, and a rollback plan.',{}); elapsed=time.perf_counter()-start
Path('benchmarks/reports').mkdir(parents=True,exist_ok=True); Path('benchmarks/reports/routing.json').write_text(json.dumps({'returned':len(rows),'seconds':elapsed},indent=2)); print('routing benchmark complete')

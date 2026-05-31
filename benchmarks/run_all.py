#!/usr/bin/env python3
import json,time,resource
from pathlib import Path
Path('benchmarks/reports').mkdir(parents=True,exist_ok=True); Path('benchmarks/reports/summary.json').write_text(json.dumps({'timestamp':time.time(),'maxrss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},indent=2)); print('benchmark reports written')

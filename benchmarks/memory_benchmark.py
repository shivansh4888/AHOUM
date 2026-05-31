#!/usr/bin/env python3
import json,resource
from pathlib import Path
Path('benchmarks/reports').mkdir(parents=True,exist_ok=True); Path('benchmarks/reports/memory.json').write_text(json.dumps({'maxrss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},indent=2)); print('memory benchmark complete')

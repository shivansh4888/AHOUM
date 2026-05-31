import json, logging
from functools import lru_cache
from pathlib import Path
from app.core.config import get_settings
log=logging.getLogger(__name__)
@lru_cache
def load_facets()->list[dict]:
    candidates=[Path(get_settings().data_dir)/'facets_enriched.json', Path(__file__).resolve().parents[3]/'data'/'facets_enriched.json']
    for p in candidates:
        if p.exists(): return json.loads(p.read_text(encoding='utf-8'))
    log.warning('facet registry not found'); return []
def get_facet(fid:str)->dict|None: return next((f for f in load_facets() if f['facet_id']==fid),None)
def filter_facets(search:str|None=None,domain:str|None=None,observable:bool|None=None)->list[dict]:
    rows=load_facets()
    if search: rows=[f for f in rows if search.lower() in (f['facet_name']+' '+f['description']).lower()]
    if domain: rows=[f for f in rows if f['domain']==domain]
    if observable is not None: rows=[f for f in rows if bool(f['observable_in_text']) is observable]
    return rows
def add_facet(facet:dict)->dict:
    rows=[dict(f) for f in load_facets()]
    name=facet['facet_name'].strip()
    row={
        'facet_id':_next_custom_id(rows),
        'facet_raw':name,
        'facet_name':name,
        'category':facet.get('category') or 'Custom',
        'domain':facet['domain'].strip().upper(),
        'description':facet['description'].strip(),
        'anchor_low':facet.get('anchor_low') or f'Clear evidence opposing or lacking {name.lower()}.',
        'anchor_high':facet.get('anchor_high') or f'Clear evidence expressing strong {name.lower()}.',
        'linguistic_markers':[m.strip().lower() for m in facet.get('linguistic_markers',[]) if m.strip()],
        'evaluation_difficulty':facet.get('evaluation_difficulty','medium'),
        'requires_longitudinal':bool(facet.get('requires_longitudinal',False)),
        'observable_in_text':bool(facet.get('observable_in_text',True)),
        'is_active':bool(facet.get('is_active',True)),
        'correlated_facets':[],
        'inverse_facets':[],
    }
    rows.append(row)
    p=_registry_path()
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    load_facets.cache_clear()
    return row
def _registry_path()->Path:
    configured=Path(get_settings().data_dir)/'facets_enriched.json'
    repo=Path(__file__).resolve().parents[3]/'data'/'facets_enriched.json'
    return configured if configured.exists() or not repo.exists() else repo
def _next_custom_id(rows:list[dict])->str:
    nums=[]
    for f in rows:
        fid=str(f.get('facet_id',''))
        if fid.startswith('CUSTOM_') and fid[7:].isdigit(): nums.append(int(fid[7:]))
    return f'CUSTOM_{(max(nums) if nums else 0)+1:04d}'

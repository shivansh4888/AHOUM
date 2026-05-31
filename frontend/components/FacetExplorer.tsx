"use client";
import { useEffect,useState } from 'react';
import { PlusCircle } from 'lucide-react';
import { api } from '@/lib/api';

const domains=['PERS','COGS','EMOT','SOCL','LANG','ETHI','SPRT','PHYS','BEHV','LEAD','PSYC'];

export function FacetExplorer(){
  const [q,setQ]=useState('');
  const [domain,setDomain]=useState('');
  const [rows,setRows]=useState<any[]>([]);
  const [saving,setSaving]=useState(false);
  const [error,setError]=useState('');
  const [form,setForm]=useState({facet_name:'',domain:'BEHV',description:'',linguistic_markers:''});
  const load=()=>api<any[]>(`/api/facets?search=${encodeURIComponent(q)}&domain=${domain}`).then(setRows).catch(()=>setRows([]));
  useEffect(()=>{load()},[q,domain]);
  async function createFacet(e:React.FormEvent){
    e.preventDefault();
    setSaving(true);
    setError('');
    try{
      const created=await api<any>('/api/facets',{method:'POST',body:JSON.stringify({
        ...form,
        linguistic_markers:form.linguistic_markers.split(',').map(x=>x.trim()).filter(Boolean),
      })});
      setRows(v=>[created,...v]);
      setForm({facet_name:'',domain:'BEHV',description:'',linguistic_markers:''});
    }catch(err:any){
      setError(err.message || 'Could not add facet');
    }finally{
      setSaving(false);
    }
  }
  return <div className="space-y-6">
    <form onSubmit={createFacet} className="panel p-5">
      <div className="mb-4 flex items-center gap-2 font-semibold"><PlusCircle size={17} className="text-signal"/>Add Facet</div>
      <div className="grid gap-3 md:grid-cols-[1fr_160px]">
        <input required placeholder="Facet name" value={form.facet_name} onChange={e=>setForm({...form,facet_name:e.target.value})}/>
        <select value={form.domain} onChange={e=>setForm({...form,domain:e.target.value})}>{domains.map(d=><option key={d}>{d}</option>)}</select>
      </div>
      <textarea required className="mt-3 min-h-24" placeholder="Description" value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/>
      <div className="mt-3 grid gap-3 md:grid-cols-[1fr_auto]">
        <input placeholder="Markers, comma separated" value={form.linguistic_markers} onChange={e=>setForm({...form,linguistic_markers:e.target.value})}/>
        <button className="btn btn-primary" disabled={saving} type="submit">{saving?'Adding':'Add facet'}</button>
      </div>
      {error&&<div className="mt-3 rounded-md border border-rose/20 bg-red-50 px-3 py-2 text-sm text-rose">{error}</div>}
    </form>
    <div>
      <div className="mb-5 grid gap-3 md:grid-cols-2">
        <input placeholder="Search facets" value={q} onChange={e=>setQ(e.target.value)}/>
        <select value={domain} onChange={e=>setDomain(e.target.value)}><option value="">All domains</option>{domains.map(d=><option key={d}>{d}</option>)}</select>
      </div>
      <div className="grid gap-4 md:grid-cols-2">{rows.map(f=><article className="panel p-5" key={f.facet_id}>
        <div className="font-mono text-xs text-muted">{f.domain} / {f.facet_id}</div>
        <h3 className="mt-2 font-semibold">{f.facet_name}</h3>
        <p className="mt-2 text-sm leading-6 text-muted">{f.description}</p>
      </article>)}</div>
    </div>
  </div>
}

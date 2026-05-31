"use client";
import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AlertTriangle, BrainCircuit, Gauge, ScanLine, ShieldCheck } from 'lucide-react';
import { Shell } from '@/components/Shell';
import { ConversationEditor } from '@/components/ConversationEditor';
import { ConversationUploader } from '@/components/ConversationUploader';
import { api, Turn } from '@/lib/api';

export default function Evaluate(){
  const [turns,setTurns]=useState<Turn[]>([{speaker:'user',text:'I want to resolve this conflict fairly and use evidence before deciding.'},{speaker:'assistant',text:'What evidence do you already have, and what assumptions should we check?'}]);
  const [error,setError]=useState('');
  const [submitting,setSubmitting]=useState(false);
  const router=useRouter();
  const words=useMemo(()=>turns.reduce((n,t)=>n+t.text.split(/\s+/).filter(Boolean).length,0),[turns]);
  async function submit(){setError('');setSubmitting(true);try{const r=await api<{job_id:string}>('/api/evaluate',{method:'POST',body:JSON.stringify({title:'Dashboard evaluation',turns:turns.filter(t=>t.text.trim())})});router.push(`/results/${r.job_id}`)}catch(e){setError(e instanceof Error?e.message:'Evaluation request failed')}finally{setSubmitting(false)}}
  return <Shell>
    <section className="mb-8">
      <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <div>
          <h1 className="text-[32px] font-semibold tracking-normal">Conversation Evaluation</h1>
          <p className="mt-3 max-w-3xl text-lg leading-7 text-muted">Analyze dialogue quality across 300 evaluation facets.</p>
        </div>
        <div className="grid grid-cols-3 gap-3 text-center">
          <Metric icon={BrainCircuit} label="Turns" value={turns.length}/>
          <Metric icon={Gauge} label="Words" value={words}/>
          <Metric icon={ShieldCheck} label="Facets" value="300"/>
        </div>
      </div>
    </section>
    <div className="grid gap-6 xl:grid-cols-[300px_minmax(0,1fr)_340px]">
      <aside className="space-y-4">
        <PanelTitle icon={ScanLine} title="Upload"/>
        <ConversationUploader onLoad={v=>setTurns(v)}/>
      </aside>
      <section className="panel p-5 sm:p-6">
        <PanelTitle icon={BrainCircuit} title="Conversation Builder"/>
        <div className="mt-5"><ConversationEditor turns={turns} setTurns={setTurns}/></div>
      </section>
      <aside className="space-y-4">
        <PanelTitle icon={Gauge} title="Evaluation Summary"/>
        <div className="panel p-5">
          <div className="space-y-4">
            {['Fairness','Safety','Empathy','Reasoning'].map((x)=><div key={x} className="flex items-center justify-between border-b border-line pb-3 text-sm last:border-b-0 last:pb-0 dark:border-neutral-800"><span className="font-medium">{x}</span><span className="text-muted">Waiting</span></div>)}
          </div>
          {error&&<div className="mt-5 flex gap-2 rounded-md border border-rose/30 bg-rose/5 p-3 text-sm text-rose"><AlertTriangle size={16} className="shrink-0"/>{error}</div>}
          <button className="btn btn-primary mt-6 w-full py-3" onClick={submit} disabled={submitting}>{submitting?'Running...':'Run Evaluation'}</button>
          {submitting&&<div className="mt-4 h-1.5 overflow-hidden rounded-full bg-neutral-100 dark:bg-neutral-800"><div className="h-full w-1/2 rounded-full bg-signal"/></div>}
        </div>
      </aside>
    </div>
  </Shell>
}

function Metric({icon:Icon,label,value}:{icon:any;label:string;value:any}){return <div className="panel p-4"><Icon className="mx-auto text-muted" size={18}/><div className="mt-2 font-mono text-2xl font-semibold">{value}</div><div className="text-xs text-muted">{label}</div></div>}
function PanelTitle({icon:Icon,title}:{icon:any;title:string}){return <div className="flex items-center gap-2 text-sm font-semibold text-ink dark:text-neutral-100"><Icon size={16} className="text-muted"/>{title}</div>}

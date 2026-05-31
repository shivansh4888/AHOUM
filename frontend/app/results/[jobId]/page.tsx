"use client";
import { useEffect,useMemo,useState } from 'react';
import { AlertTriangle, BarChart3, CheckCircle2, FileJson, Gauge, Lightbulb, Radar, ShieldCheck } from 'lucide-react';
import { Shell } from '@/components/Shell';
import { EvaluationProgress } from '@/components/EvaluationProgress';
import { ScoreHeatmap } from '@/components/ScoreHeatmap';
import { FacetScoreCard } from '@/components/FacetScoreCard';
import { FacetRadarChart } from '@/components/FacetRadarChart';
import { DomainOverview } from '@/components/DomainOverview';
import { ConsistencyAlerts } from '@/components/ConsistencyAlerts';
import { ExportButton } from '@/components/ExportButton';
import { api } from '@/lib/api';

export default function Results({params}:{params:{jobId:string}}){
  const [data,setData]=useState<any>();
  const [tab,setTab]=useState('heatmap');
  useEffect(()=>{api(`/api/results/${params.jobId}`).then(setData).catch(()=>null);const id=setInterval(()=>api(`/api/results/${params.jobId}`).then(setData).catch(()=>null),2500);return()=>clearInterval(id)},[params.jobId]);
  const rawScores:any[]=data?.turn_results?.flatMap((t:any)=>t.facet_scores)??[];
  const scores:any[]=useMemo(()=>aggregateScores(rawScores),[rawScores]);
  const alerts:any[]=data?.turn_results?.flatMap((t:any)=>t.consistency_alerts)??[];
  const overall=useMemo(()=>scores.length?Number((scores.reduce((n:number,s:any)=>n+scoreForOverall(s),0)/scores.length).toFixed(2)):0,[scores]);
  const overallWidth=scoreWidth(overall);
  const radar=useMemo(()=>{const grouped=scores.reduce((m:Map<string,{domain:string;score:number;count:number}>,s:any)=>{const row=m.get(s.domain)??{domain:s.domain,score:0,count:0};row.score+=scoreForOverall(s);row.count++;m.set(s.domain,row);return m},new Map<string,{domain:string;score:number;count:number}>());return Array.from(grouped.values()).map(x=>({domain:x.domain,score:Number((x.score/x.count).toFixed(2))}))},[scores]);
  return <Shell>
    <div className="flex flex-wrap items-center justify-between gap-4">
      <div><div className="text-sm text-muted">Evaluation Results</div><h1 className="mt-2 text-[32px] font-semibold">Conversation Quality Report</h1></div>
      {data&&<ExportButton data={data} name={`${params.jobId}.json`}/>}
    </div>
    <div className="mt-8 grid gap-6 xl:grid-cols-[320px_1fr]">
      <aside className="space-y-6">
        <div className="panel p-6">
          <div className="text-sm text-muted">Overall Score</div>
          <div className="mt-3 flex items-end gap-3">
            <div className="font-mono text-5xl font-semibold">{scores.length?overall:'--'}</div>
            <div className="mb-2 text-sm font-medium text-success">{overall>=1?'Strong':overall>=0?'Mixed':'Needs review'}</div>
          </div>
          <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-neutral-100 dark:bg-neutral-800"><div className="h-full rounded-full bg-signal" style={{width:`${overallWidth}%`}}/></div>
          <div className="mt-5 flex items-center gap-2 text-sm text-muted"><ShieldCheck size={15}/>{data?.status??'loading'}</div>
        </div>
        <EvaluationProgress jobId={params.jobId}/>
        <div className="panel p-5">
          <div className="flex items-center gap-2 font-semibold"><Lightbulb size={17} className="text-amber"/>Key Insights</div>
          <div className="mt-4 space-y-2 text-sm text-muted">
            <Insight icon={CheckCircle2} text={scores.some((s:any)=>s.score>0)?'Positive behavioral signals detected':'Awaiting score signals'}/>
            <Insight icon={CheckCircle2} text={`${scores.length || 0} facet scores generated`}/>
            <Insight icon={alerts.length?AlertTriangle:CheckCircle2} text={alerts.length?`${alerts.length} consistency alert detected`:'No consistency alerts detected'}/>
          </div>
        </div>
      </aside>
      <section className="min-w-0">
        <div className="mb-5 flex flex-wrap gap-2">{[['heatmap',BarChart3],['overview',Gauge],['details',Radar],['raw',FileJson]].map(([t,Icon]:any)=><button className={`btn capitalize ${tab===t?'border-signal bg-blue-50 text-signal dark:bg-blue-950/20':''}`} key={t} onClick={()=>setTab(t)}><Icon size={16}/>{t}</button>)}</div>
        {tab==='overview'&&<div className="grid gap-5 xl:grid-cols-2"><div className="panel p-5"><h2 className="mb-4 text-lg font-semibold">Domain Performance</h2><DomainOverview scores={scores}/></div><div className="panel p-5"><h2 className="mb-4 text-lg font-semibold">Facet Radar</h2><FacetRadarChart data={radar}/></div><div className="panel p-5 xl:col-span-2"><ConsistencyAlerts alerts={alerts}/></div></div>}
        {tab==='heatmap'&&(scores.length?<ScoreHeatmap scores={scores}/>:<EmptyResults data={data}/>)}
        {tab==='details'&&(scores.length?<div className="grid gap-3 md:grid-cols-2">{scores.map((s:any,i:number)=><FacetScoreCard key={i} score={s}/>)}</div>:<EmptyResults data={data}/>)}
        {tab==='raw'&&<pre className="panel max-h-[70vh] overflow-auto p-4 text-xs text-muted">{JSON.stringify(data,null,2)}</pre>}
      </section>
    </div>
  </Shell>
}

function Insight({icon:Icon,text}:{icon:any;text:string}){return <div className="flex items-center gap-2 rounded-md border border-line px-3 py-2 dark:border-neutral-800"><Icon size={15} className="text-success"/>{text}</div>}
function EmptyResults({data}:{data:any}){return <div className="panel p-6 text-sm text-muted"><div className="font-semibold text-ink dark:text-neutral-100">{data?.status==='failed'?'Evaluation failed':'Evaluation is still running'}</div><div className="mt-2">{data?.error ?? 'No facet scores have been written yet. This page will keep polling for results.'}</div></div>}
function scoreForOverall(score:any){return Number(score.quality_score ?? score.display_score ?? score.score ?? 0)}
function scoreWidth(score:number){return Math.round(((Math.max(-2,Math.min(2,score))+2)/4)*100)}
function aggregateScores(scores:any[]){
  const grouped=new Map<string,any[]>();
  for(const score of scores){const key=score.facet_id || score.facet_name; grouped.set(key,[...(grouped.get(key)??[]),score])}
  return Array.from(grouped.values()).map(rows=>{
    const first=rows[0];
    const display=Number((rows.reduce((n,s)=>n+Number(s.display_score ?? s.score ?? 0),0)/rows.length).toFixed(2));
    const quality=Number((rows.reduce((n,s)=>n+scoreForOverall(s),0)/rows.length).toFixed(2));
    return {...first,display_score:display,quality_score:quality,score:display,reasoning:bestReason(rows),turn_count:rows.length};
  }).sort((a,b)=>Number(b.quality_score)-Number(a.quality_score));
}
function bestReason(rows:any[]){return rows.find(r=>String(r.reasoning||'').toLowerCase().includes('evidence'))?.reasoning ?? rows[0]?.reasoning ?? ''}

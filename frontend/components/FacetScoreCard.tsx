"use client";

export function FacetScoreCard({score}:{score:any}){
  const value=Math.round(Number(score.display_score ?? score.score ?? 0));
  const positive=score.score_kind === 'risk' ? value <= 0 : value >= 0;
  const width=scoreWidth(value);
  return <article className="panel p-4">
    <div className="flex items-start justify-between gap-3">
      <div><h3 className="font-semibold">{score.facet_name}</h3><div className="mt-1 text-xs text-muted">{score.domain}</div></div>
      <span className={`font-mono text-2xl font-semibold ${positive?'text-success':'text-rose'}`}>{value}</span>
    </div>
    <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-neutral-100 dark:bg-neutral-800"><div className={`h-full rounded-full ${positive?'bg-success':'bg-rose'}`} style={{width:`${width}%`}}/></div>
    <p className="mt-3 text-sm leading-6 text-muted">{score.reasoning}</p>
    <div className="mt-4 flex items-center justify-between text-xs text-muted"><span>Confidence</span><span className="font-mono">{Math.round((score.confidence??0)*100)}%</span></div>
  </article>
}

function scoreWidth(score:number){return Math.round(((Math.max(-2,Math.min(2,score))+2)/4)*100)}

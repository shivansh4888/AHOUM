import { Shell } from '@/components/Shell';
import Link from 'next/link';
import { ArrowRight, BrainCircuit, CheckCircle2, Radar, ShieldCheck } from 'lucide-react';

export default function Home(){
  return <Shell>
    <section className="mx-auto max-w-6xl py-8">
      <div className="max-w-3xl">
        <h1 className="text-[32px] font-semibold tracking-normal">Conversation Evaluation</h1>
        <p className="mt-3 text-lg leading-7 text-muted">Analyze dialogue quality across 300 evaluation facets.</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link className="btn btn-primary" href="/evaluate">Run Evaluation<ArrowRight size={16}/></Link>
          <Link className="btn" href="/facets">Explore facets</Link>
        </div>
      </div>
      <div className="mt-10 grid gap-5 lg:grid-cols-[1fr_380px]">
        <div className="panel p-6">
          <div className="mb-5 flex items-center justify-between border-b border-line pb-4 dark:border-neutral-800">
            <h2 className="text-lg font-semibold">Evaluation summary</h2>
            <span className="text-sm text-muted">Sample report</span>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <DemoCard icon={ShieldCheck} title="Safety" value="94" tone="text-success"/>
            <DemoCard icon={BrainCircuit} title="Reasoning" value="89" tone="text-signal"/>
            <DemoCard icon={Radar} title="Bias Risk" value="12" tone="text-amber"/>
            <DemoCard icon={CheckCircle2} title="Trustworthiness" value="91" tone="text-success"/>
          </div>
        </div>
        <div className="panel p-6">
          <h2 className="text-lg font-semibold">Key insights</h2>
          <div className="mt-5 space-y-4 text-sm text-muted">
            <div>Strong evidence-based reasoning</div>
            <div>Low toxicity and high collaboration signal</div>
            <div>Could provide more supporting evidence</div>
          </div>
        </div>
      </div>
    </section>
  </Shell>
}

function DemoCard({icon:Icon,title,value,tone}:{icon:any;title:string;value:string;tone:string}){
  return <div className="rounded-lg border border-line bg-surface p-4 dark:border-neutral-800 dark:bg-neutral-900">
    <div className="flex items-center justify-between">
      <Icon className={tone} size={18}/>
      <span className={`font-mono text-3xl font-semibold ${tone}`}>{value}</span>
    </div>
    <div className="mt-4 text-sm text-muted">{title}</div>
    <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-neutral-100 dark:bg-neutral-800">
      <div className="h-full rounded-full bg-signal" style={{width:`${value}%`}}/>
    </div>
  </div>
}

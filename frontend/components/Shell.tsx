'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BarChart3, BrainCircuit, Clock3, MessageSquareText, Settings, ShieldCheck } from 'lucide-react';

const nav=[
  {href:'/evaluate',label:'Evaluate',icon:BrainCircuit},
  {href:'/facets',label:'Facets',icon:BarChart3},
  {href:'/conversations',label:'Conversations',icon:MessageSquareText},
  {href:'#history',label:'History',icon:Clock3},
  {href:'#settings',label:'Settings',icon:Settings}
];

export function Shell({children}:{children:React.ReactNode}){
  const pathname=usePathname();
  return <main className="min-h-screen">
    <div className="mx-auto grid min-h-screen max-w-[1680px] lg:grid-cols-[264px_1fr]">
      <aside className="hidden border-r border-line bg-sidebar px-5 py-6 dark:border-neutral-800 dark:bg-neutral-950 lg:block">
        <Link href="/" className="flex items-center gap-3 px-2">
          <span className="grid h-9 w-9 place-items-center rounded-md border border-line bg-surface text-signal dark:border-neutral-800 dark:bg-neutral-900"><ShieldCheck size={18}/></span>
          <span><span className="block text-[15px] font-semibold">ConvEval-300</span><span className="text-xs text-muted">Evaluation platform</span></span>
        </Link>
        <nav className="mt-9 space-y-1">
          {nav.map(item=>{const Icon=item.icon;const active=pathname===item.href;return <Link key={item.href} href={item.href} className={`relative flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition ${active?'bg-white font-medium text-ink dark:bg-neutral-900 dark:text-neutral-100':'text-muted hover:bg-white/70 hover:text-ink dark:hover:bg-neutral-900 dark:hover:text-neutral-100'}`}>
            {active&&<span className="absolute left-0 top-2 h-5 w-0.5 rounded-full bg-signal"/>}
            <Icon size={17}/>{item.label}
          </Link>})}
        </nav>
        <div className="mt-10 border-t border-line pt-5 text-xs text-muted dark:border-neutral-800">
          <div className="font-medium text-ink dark:text-neutral-200">Recent evaluations</div>
          <div className="mt-3 space-y-2">
            <div>Evidence-based decision review</div>
            <div>Empathy and safety scan</div>
            <div>Bias and trust audit</div>
          </div>
        </div>
      </aside>
      <section className="min-w-0">
        <header className="sticky top-0 z-20 border-b border-line bg-background/95 backdrop-blur lg:hidden dark:border-neutral-800 dark:bg-neutral-950/95">
          <div className="flex items-center justify-between px-5 py-4">
            <Link className="text-base font-semibold" href="/">ConvEval-300</Link>
            <div className="flex gap-2">{nav.slice(0,3).map(item=>{const Icon=item.icon;return <Link aria-label={item.label} className="btn px-3 py-2" href={item.href} key={item.href}><Icon size={17}/></Link>})}</div>
          </div>
        </header>
        <div className="px-5 py-8 sm:px-8 lg:px-10 xl:px-12">{children}</div>
        <nav className="fixed inset-x-3 bottom-3 z-30 grid grid-cols-3 rounded-lg border border-line bg-surface p-1 lg:hidden">
          {nav.slice(0,3).map(item=>{const Icon=item.icon;const active=pathname===item.href;return <Link key={item.href} href={item.href} className={`flex flex-col items-center gap-1 rounded-md px-2 py-2 text-[11px] ${active?'bg-sidebar text-ink':'text-muted'}`}><Icon size={17}/>{item.label}</Link>})}
        </nav>
      </section>
    </div>
  </main>
}

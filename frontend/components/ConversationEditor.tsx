"use client";
import { Bot, Plus, Trash2, UserRound } from 'lucide-react';
import { Turn } from '@/lib/api';

export function ConversationEditor({turns,setTurns}:{turns:Turn[];setTurns:(t:Turn[])=>void}){
  return <div className="space-y-4">
      {turns.map((t,i)=>{const isAssistant=t.speaker.toLowerCase().includes('assistant')||t.speaker.toLowerCase().includes('ai');const Icon=isAssistant?Bot:UserRound;return <div className={`rounded-lg border bg-surface p-4 dark:bg-neutral-900 ${isAssistant?'border-l-signal':'border-l-muted'} border-l-2`} key={i}>
        <div className="mb-3 flex items-center gap-3 border-b border-line pb-3 dark:border-neutral-800">
          <span className="grid h-8 w-8 place-items-center rounded-md border border-line bg-sidebar text-muted dark:border-neutral-800 dark:bg-neutral-950"><Icon size={16}/></span>
          <input aria-label="Speaker" value={t.speaker} onChange={e=>setTurns(turns.map((x,j)=>j===i?{...x,speaker:e.target.value}:x))}/>
          <button aria-label="Delete turn" className="btn shrink-0 px-3" onClick={()=>setTurns(turns.filter((_,j)=>j!==i))}><Trash2 size={16}/></button>
        </div>
        <textarea aria-label="Message content" rows={4} value={t.text} placeholder="Paste or write a conversation turn..." onChange={e=>setTurns(turns.map((x,j)=>j===i?{...x,text:e.target.value}:x))}/>
      </div>})}
    <div className="flex flex-wrap gap-3">
      <button className="btn" onClick={()=>setTurns([...turns,{speaker:'user',text:''}])}><Plus size={16}/>User turn</button>
      <button className="btn" onClick={()=>setTurns([...turns,{speaker:'assistant',text:''}])}><Plus size={16}/>Assistant turn</button>
    </div>
  </div>
}

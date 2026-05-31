"use client";
import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { CheckCircle2, FileJson, UploadCloud } from 'lucide-react';

export function ConversationUploader({onLoad}:{onLoad:(v:any)=>void}){
  const [name,setName]=useState('');
  const [error,setError]=useState('');
  const {getRootProps,getInputProps,isDragActive}=useDropzone({accept:{'application/json':['.json'],'text/plain':['.txt'],'text/csv':['.csv']},multiple:false,onDrop:async files=>{
    const f=files[0]; if(!f) return;
    setError(''); setName(f.name);
    try{
      const text=await f.text();
      if(f.name.endsWith('.json')) onLoad(normalizeTurns(JSON.parse(text)));
      else onLoad(text.split(/\n+/).filter(Boolean).map((line,i)=>({speaker:i%2?'assistant':'user',text:line.trim()})));
    }catch{setError('Could not parse that file. Use JSON with turns, TXT, or CSV text rows.')}
  }});
  return <div {...getRootProps()} className={`cursor-pointer rounded-lg border border-dashed bg-surface transition dark:bg-neutral-900 ${isDragActive?'border-signal bg-blue-50 dark:bg-blue-950/20':'border-line hover:border-neutral-400 dark:border-neutral-800 dark:hover:border-neutral-600'}`}>
    <input {...getInputProps()}/>
    <div className="p-6">
      <div className="flex items-center gap-4">
        <span className="grid h-11 w-11 place-items-center rounded-lg border border-line bg-sidebar text-muted dark:border-neutral-800 dark:bg-neutral-950"><UploadCloud size={22}/></span>
        <div>
          <div className="font-semibold">{isDragActive?'Drop conversation':'Upload conversation'}</div>
          <div className="mt-1 text-sm text-muted">Drag and drop JSON, CSV or TXT, or browse files.</div>
        </div>
      </div>
      {name&&<div className="mt-4 flex items-center gap-2 rounded-md border border-success/20 bg-success/5 px-3 py-2 text-sm text-success"><CheckCircle2 size={16}/><FileJson size={16}/>{name}</div>}
      {error&&<div className="mt-4 rounded-md border border-rose/20 bg-rose/5 px-3 py-2 text-sm text-rose">{error}</div>}
    </div>
  </div>
}

function normalizeTurns(value:any){
  const rows=Array.isArray(value) ? value : value?.turns;
  const turns=Array.isArray(rows) && rows.every(isTurn) ? rows : Array.isArray(value) && value[0]?.turns;
  if(!Array.isArray(turns)) throw new Error('missing turns');
  const normalized=turns.filter(isTurn).map((t:any)=>({speaker:String(t.speaker),text:String(t.text)}));
  if(!normalized.length) throw new Error('empty turns');
  return normalized;
}

function isTurn(value:any){
  return value && typeof value.speaker === 'string' && typeof value.text === 'string';
}

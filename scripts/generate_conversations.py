#!/usr/bin/env python3
import json
from pathlib import Path
cats=['Risk Taking','Conflict Resolution','Emotional Disclosure','Technical Reasoning','Ethics','Spirituality','Leadership','Distress','Enthusiasm','Contradictory Signals']
txt={'Risk Taking':'I know the rollout is uncertain, but I want a guarded experiment and clear rollback criteria.','Conflict Resolution':'I hear the frustration; let us separate facts from assumptions and agree on repair.','Emotional Disclosure':'I felt anxious after the meeting and need to say that directly.','Technical Reasoning':'The metric moved because the sample changed; we need a control group.','Ethics':'Hiding cancellation would improve conversion, but it is manipulative and unfair.','Spirituality':'This matters because service and humility give the work meaning.','Leadership':'I will own the decision, delegate analysis, and include quieter teammates.','Distress':'I am overwhelmed and sleeping badly, but I can ask for help today.','Enthusiasm':'This prototype is exciting and I have energy to polish it.','Contradictory Signals':'I want transparency, but do not tell the customer about the outage yet.'}
def main():
    out=Path('conversations'); out.mkdir(exist_ok=True); rows=[]
    for i in range(50):
        c=cats[i%len(cats)]; conv={'id':f'sample-{i+1:03d}','title':f'{c} scenario {i+1}','turns':[{'speaker':'user','text':txt[c]},{'speaker':'assistant','text':'What outcome should we optimize for next?'}],'ground_truth_facets':[c.lower().replace(' ','_')],'expected_scores':{'representative':2 if c not in ['Distress','Contradictory Signals'] else -1},'tags':[c,'synthetic']}; rows.append(conv); (out/f'{conv["id"]}.json').write_text(json.dumps(conv,indent=2))
    Path('data').mkdir(exist_ok=True); Path('data/sample_conversations.json').write_text(json.dumps(rows,indent=2)); print('generated 50 conversations')
if __name__=='__main__': main()

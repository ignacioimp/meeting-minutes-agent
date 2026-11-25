"""Local, deterministic minutes generator for explicitly tagged meeting notes."""
import argparse,json,re
from datetime import date
from pathlib import Path

TAGS={'TITLE','DATE','ATTENDEES','SUMMARY','DECISION','ACTION','OPEN','RISK'}
TAG=re.compile(r'^([A-Z]+):\s*(.*)$')

def parse(text):
    result={'title':None,'date':None,'attendees':None,'summary':[],'decisions':[],'actions':[],'open_questions':[],'risks':[],'unclassified':[],'warnings':[]}
    for i,raw in enumerate(text.splitlines(),1):
        if not raw.strip(): continue
        m=TAG.match(raw.strip()); evidence={'line':i,'source':raw}
        if not m or m[1] not in TAGS:
            result['unclassified'].append(evidence); continue
        tag,value=m[1],m[2].strip()
        if not value:
            result['warnings'].append(f'Line {i}: empty {tag}'); result['unclassified'].append(evidence); continue
        if tag in ('TITLE','DATE','ATTENDEES'):
            key=tag.lower()
            if result[key] is not None:
                result['warnings'].append(f'Line {i}: repeated {tag}; first retained'); result['unclassified'].append(evidence); continue
            if tag=='DATE':
                try: date.fromisoformat(value)
                except ValueError: result['warnings'].append(f'Line {i}: date must be ISO YYYY-MM-DD'); result['unclassified'].append(evidence); continue
            result[key]={'value':value,**evidence}; continue
        if tag=='ACTION':
            chunks=[p.strip() for p in value.split('|')]; description=chunks[0]; fields={}; valid=bool(description)
            for chunk in chunks[1:]:
                k,sep,v=chunk.partition('='); k=k.strip().lower(); v=v.strip()
                if not sep or k not in ('owner','due') or k in fields or not v: valid=False; break
                fields[k]=v
            if not valid:
                result['warnings'].append(f'Line {i}: malformed action; review manually'); result['unclassified'].append(evidence); continue
            due=fields.get('due'); owner=fields.get('owner')
            if due:
                try: due=date.fromisoformat(due).isoformat()
                except ValueError: result['warnings'].append(f'Line {i}: invalid action due date; review manually'); due=None
            result['actions'].append({'description':description,'owner':owner,'due':due,**evidence}); continue
        key={'SUMMARY':'summary','DECISION':'decisions','OPEN':'open_questions','RISK':'risks'}[tag]
        result[key].append({'text':value,**evidence})
    return result

def md(value):
    # Escape Markdown syntax and raw HTML from local meeting notes.
    value=str(value).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    return re.sub(r'([\\`*_{}\[\]()#+.!|~-])',r'\\\1',value)

def render(result):
    def meta(key): return md(result[key]['value']) if result[key] else 'Not recorded'
    lines=['# '+(meta('title') if result['title'] else 'Meeting minutes'),'','**Date:** '+meta('date')+'  ','**Attendees:** '+meta('attendees'),'']
    for key,title in [('summary','Executive summary'),('decisions','Decisions'),('actions','Action items'),('open_questions','Open questions'),('risks','Risks'),('unclassified','Unclassified notes — review required')]:
        lines += ['## '+title,'']
        if not result[key]: lines+=['Not recorded.','']; continue
        for item in result[key]:
            if key=='actions': value=md(item['description'])+' — Owner: '+(md(item['owner']) if item['owner'] else 'Unassigned')+'; Due: '+(md(item['due']) if item['due'] else 'Not specified')
            else: value=md(item.get('text',item['source']))
            lines.append(f'- {value} (source line {item["line"]})')
        lines.append('')
    if result['warnings']: lines+=['## Review warnings','']+['- '+md(w) for w in result['warnings']]+['']
    lines+=['---','Draft for human review. Explicit tags are preserved; no commitments are inferred.','']
    return '\n'.join(lines)

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('notes',type=Path); p.add_argument('--format',choices=['markdown','json'],default='markdown'); a=p.parse_args()
    try:
        r=parse(a.notes.read_text(encoding='utf-8')); print(json.dumps(r,indent=2,ensure_ascii=False) if a.format=='json' else render(r))
    except (OSError,ValueError) as e: p.exit(2,f'Invalid input: {e}\n')
if __name__=='__main__': main()

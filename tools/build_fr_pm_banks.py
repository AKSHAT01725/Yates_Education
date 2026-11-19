#!/usr/bin/env python3
"""Build student-practice JSON from page-preserving FR/PM extraction text.
Keeps source wording; records answer availability separately; does not mark uncertain answers verified.
"""
import json, re, argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'question-banks'

def blocks_by_source(text):
    matches=list(re.finditer(r'(?m)^#{10,}\n([^\n]+)\n#{10,}\s*\n',text))
    out={}
    for i,m in enumerate(matches):
        name=m.group(1).strip()
        end=matches[i+1].start() if i+1<len(matches) else len(text)
        out[name]=text[m.end():end]
    return out

def clean_lines(s):
    return [x.rstrip() for x in s.replace('\r','').split('\n')]

def locate_section(lines, section):
    for i,l in enumerate(lines):
        if l.strip().upper()==f'SECTION {section}': return i
    return -1

def candidate_starts(lines, lo, hi, section, answer_mode=False):
    starts=[]
    for i in range(max(0,lo), min(hi,len(lines))):
        t=lines[i].strip()
        if not re.fullmatch(r'\d{1,2}',t): continue
        n=int(t)
        if section=='A' and not 1<=n<=15: continue
        if section=='B' and not 16<=n<=30: continue
        if section=='C' and n not in {31,32}: continue
        j=i+1
        while j<len(lines) and not lines[j].strip(): j+=1
        if j>=len(lines): continue
        nxt=lines[j].strip()
        if re.fullmatch(r'\d+(?:\.\d+)?',nxt): continue
        if nxt.upper().startswith(('SECTION ','ALL ','BOTH ','EACH QUESTION','KAPLAN','FR:','PM:','FR —','PM —')): continue
        if nxt in {'MOCK B QUESTIONS','MOCK D QUESTIONS','PROGRESS TEST QUESTIONS','CONSOLIDATION TEST QUESTIONS'}: continue
        if answer_mode:
            prev=lines[i-1].strip() if i else ''
            score=0
            if re.fullmatch(r'[A-E](?:\s*,\s*[A-E])*',nxt): score=5
            elif re.match(r'^[\$£€]|^\(?-?\d',nxt) or nxt.lower() in {'item','recoverable amount','terp','property, plant and equipment'}: score=4
            elif not prev or prev in {'KAPLAN PUBLISHING','SECTION A','SECTION B','SECTION C'} or prev.startswith(('FR ANSWER PAPER','PM ANSWER PAPER')) or not set(prev)<=set('–—- '): score=1
            if score==0: continue
            starts.append((i,n,score))
        else:
            starts.append((i,n,1))
    if answer_mode:
        best={}
        for pos,n,score in starts:
            if n not in best or score>best[n][1]: best[n]=(pos,score)
        return [(v[0],n) for n,v in sorted(best.items(),key=lambda x:x[1][0])]
    seen=set(); unique=[]
    for pos,n,_ in starts:
        if n not in seen:
            seen.add(n); unique.append((pos,n))
    return unique

def strip_page_noise(s):
    out=[]
    for l in s.splitlines():
        t=l.strip()
        if t=='==============================================================================': continue
        if re.match(r'^(FR|PM) (QUESTION|ANSWER) PAPER — SOURCE PDF PAGE \d+ OF \d+$',t): continue
        if t in {'KAPLAN PUBLISHING','MOCK B QUESTIONS','MOCK D QUESTIONS','PROGRESS TEST QUESTIONS','CONSOLIDATION TEST QUESTIONS'}: continue
        if re.fullmatch(r'\d{1,3}',t) and len(out)>0 and out[-1].strip()=='': continue
        out.append(l)
    return '\n'.join(out).strip()

def parse_answer_blocks(answer_text):
    lines=clean_lines(answer_text)
    result={}
    for sec in ['A','B','C']:
        si=locate_section(lines,sec)
        if si<0: continue
        end=next((j for j in range(si+1,len(lines)) if lines[j].strip().upper()==f'SECTION {"B" if sec=="A" else "C" if sec=="B" else "END"}'),len(lines))
        lo=si+1
        starts=candidate_starts(lines,lo,end,sec,answer_mode=(sec in {'A','B'}))
        for k,(pos,n) in enumerate(starts):
            nxt=starts[k+1][0] if k+1<len(starts) else end
            raw_lines=lines[pos+1:nxt]
            answer_pages=sorted({nearest_page(lines,pos)} | {int(x) for x in re.findall(r'SOURCE PDF PAGE (\d+) OF', '\n'.join(raw_lines), re.I)})
            raw='\n'.join(raw_lines).strip()
            raw=strip_page_noise(raw)
            # Answer key letter is the first standalone A-D after the number.
            letter=None
            for x in raw.splitlines():
                if x.strip() in {'A','B','C','D','E'}:
                    letter=x.strip(); break
            result[(sec,n)]={'text':raw,'correctOption':letter,'pages':answer_pages}
    return result

def option_parse(raw):
    lines=raw.splitlines()
    # Look for the last A/B/C/D run; option labels are standalone lines.
    labels=[]
    for i,l in enumerate(lines):
        if l.strip() in {'A','B','C','D'}:
            labels.append((i,l.strip()))
    best=None
    for k in range(len(labels)-3):
        seq=labels[k:k+4]
        if [x[1] for x in seq]==['A','B','C','D']:
            best=seq
    if not best: return raw.strip(), []
    opts=[]
    for j,(idx,letter) in enumerate(best):
        stop=best[j+1][0] if j<3 else len(lines)
        val='\n'.join(lines[idx+1:stop]).strip()
        opts.append({'key':letter,'text':val})
    prompt='\n'.join(lines[:best[0][0]]).strip()
    return prompt,opts

def nearest_page(lines, pos):
    for j in range(pos, max(-1,pos-80), -1):
        m=re.search(r'SOURCE PDF PAGE (\d+) OF', lines[j], re.I)
        if m: return int(m.group(1))
    return 1

def parse_paper(qtext, atext, subject, paper_name, question_file):
    lines=clean_lines(qtext)
    answers=parse_answer_blocks(atext) if atext else {}
    questions=[]
    for sec in ['A','B','C']:
        si=locate_section(lines,sec)
        if si<0: continue
        # End at next section heading
        nextsec={'A':'B','B':'C','C':None}[sec]
        end=next((j for j in range(si+1,len(lines)) if nextsec and lines[j].strip().upper()==f'SECTION {nextsec}'),len(lines))
        starts=candidate_starts(lines,si+1,end,sec)
        for k,(pos,n) in enumerate(starts):
            nxt=starts[k+1][0] if k+1<len(starts) else end
            raw=strip_page_noise('\n'.join(lines[pos+1:nxt]))
            prompt,opts=option_parse(raw) if sec in {'A','B'} else (raw,[])
            ans=answers.get((sec,n),{})
            # Attach shared Section B scenario text to every question in its stated range.
            context=''; context_pages=[]
            if sec=='B':
                preceding='\n'.join(lines[si+1:pos])
                markers=list(re.finditer(r'(?im)The following scenario relates to questions?\s*(\d+)\s*[–-]\s*(\d+)\.?', preceding))
                if markers:
                    mm=markers[-1]; loq,hiq=int(mm.group(1)),int(mm.group(2))
                    if loq<=n<=hiq:
                        context_raw=preceding[mm.end():]; context=strip_page_noise(context_raw)
                        context_pages=sorted({int(x) for x in re.findall(r'SOURCE PDF PAGE (\d+) OF', context_raw, re.I)} | {nearest_page(lines,si+1+len(preceding[:mm.start()].splitlines()))})
                elif n==16:
                    # Some supplied papers begin Section B with the scenario directly, without a label.
                    context=strip_page_noise(preceding)
                    context_pages=sorted({int(x) for x in re.findall(r'SOURCE PDF PAGE (\d+) OF', preceding, re.I)} | {nearest_page(lines,si+1)})
            qtype='mcq' if opts else ('written' if sec=='C' else ('numeric' if ans.get('text') else 'written'))
            qid=f'{subject.lower()}-{re.sub("[^a-z0-9]+","-",paper_name.lower()).strip("-")}-{sec.lower()}-{n}'
            qpage=nearest_page(lines,pos)
            question_pages=sorted(set([qpage]+context_pages+[int(x) for x in re.findall(r'SOURCE PDF PAGE (\d+) OF', '\n'.join(lines[pos+1:nxt]), re.I)]))
            question_text=prompt if opts else raw
            options=[o['text'] for o in opts]
            qtype_schema='single' if qtype=='mcq' else ('numeric' if qtype=='numeric' else 'written')
            answer_obj=({'correctOption':ans.get('correctOption'),'modelAnswer':ans.get('text','')} if ans.get('text') else None)
            questions.append({
                'id':qid,'subject':subject,'paper':paper_name,'section':sec,
                'number':n,'originalQuestionNumber':n,'marks':2 if sec in {'A','B'} else 0,
                'type':qtype,'questionType':qtype_schema,'scenarioContext':context,
                'content':{'questionText':question_text,'options':options},
                'prompt':question_text,'options':opts,
                'correctOption':ans.get('correctOption'),
                'modelAnswer':ans.get('text',''),
                'answer':answer_obj,'explanation':ans.get('text') or None,
                'answerAvailable':bool(ans.get('text')),
                'verificationStatus':'extracted_unverified',
                'verification':{'status':'needs_review' if ans.get('text') else 'missing_answer','reviewer':None,'reviewedAt':None,'notes':'Transcribed from supplied question/answer paper; academic verification pending.'},
                'source':{'file':question_file,'questionFile':question_file,'answerFile':None,'questionPages':question_pages,'answerPages':ans.get('pages',[]),'section':sec,'questionNumber':n}
            })
    return questions

def build(subject, txtpath):
    text=Path(txtpath).read_text(encoding='utf-8',errors='replace')
    src=blocks_by_source(text)
    qnames=[n for n in src if 'Questions' in n]
    allq=[]
    for qname in qnames:
        prefix=qname.replace('Questions','Answers')
        aname=next((n for n in src if n.lower().startswith('marking guide:') and prefix.split(' - ')[0].lower() in n.lower() and (prefix.split(' - ')[-1].replace('.pdf','').lower() in n.lower())),None)
        # Exact pair by shared stem is more reliable than broad search.
        stem=re.sub(r'Questions','Answers',qname,flags=re.I).strip().replace('.pdf','').lower()
        aname=next((n for n in src if n.lower().startswith('marking guide:') and stem in n.lower()),None)
        paper=re.sub(r'\s*-\s*Questions\s*',' ',qname,flags=re.I).replace('.pdf','').strip()
        qs=parse_paper(src[qname],src.get(aname,'') if aname else '',subject,paper,qname)
        for q in qs:
            q['source']['answerFile']=aname; q['answerSource']=aname
        allq.extend(qs)
    return {'schemaVersion':1,'subject':subject,'subjectName':'Financial Reporting' if subject=='FR' else 'Performance Management','importStatus':'extracted','published':False,'verificationStatus':'needs_admin_review','questions':allq}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--fr',required=True); ap.add_argument('--pm',required=True); args=ap.parse_args()
    for sub,path in [('FR',args.fr),('PM',args.pm)]:
        bank=build(sub,path); out=DATA/f'{sub.lower()}.json'; out.write_text(json.dumps(bank,ensure_ascii=False,indent=2),encoding='utf-8')
        from collections import Counter
        print(sub,'questions',len(bank['questions']),'sections',dict(Counter(q['section'] for q in bank['questions'])),'mcq',sum(q['type']=='mcq' for q in bank['questions']),'answer key',sum(bool(q['correctOption']) for q in bank['questions']))

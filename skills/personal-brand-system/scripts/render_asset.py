"""Resolve explicit canonical text placeholders; not a semantic fact checker."""
from pathlib import Path
import argparse,json,re,hashlib

def validate_register(data):
    seen=set()
    for kind in ('claims','language'):
        for r in data.get(kind,[]):
            required={'id','exact_text','source','approval_status','disclosure'} | ({'evidence_status','interpretation_limits'} if kind=='claims' else {'version'})
            if not required.issubset(r) or any(not str(r[k]).strip() for k in required): raise ValueError('Incomplete canonical record')
            if (kind,r['id']) in seen: raise ValueError('Duplicate canonical ID')
            seen.add((kind,r['id']))
            if r['approval_status'] not in {'unreviewed','accepted-for-reuse','public-approved'}: raise ValueError('Invalid approval status')
            if kind=='claims' and r['evidence_status'] not in {'verified','user-reported','illustrative','work-in-progress'}: raise ValueError('Invalid evidence status')
    return data

def render(text,data):
    validate_register(data);deps=[]
    def replace(m):
        kind='claims' if m[1]=='claim' else 'language'
        record=next((r for r in data.get(kind,[]) if r['id']==m[2]),None)
        if not record: raise ValueError('Unknown canonical ID: '+m[2])
        if record['approval_status']=='unreviewed': raise ValueError('Canonical wording needs review: '+m[2])
        deps.append({'kind':kind,'id':record['id'],'version':record.get('version'),'text_sha256':hashlib.sha256(record['exact_text'].encode()).hexdigest(),'evidence_status':record.get('evidence_status')})
        return record['exact_text']
    output=re.sub(r'\{\{(claim|language):([A-Za-z0-9_-]+)\}\}',replace,text)
    if '{{claim:' in output or '{{language:' in output: raise ValueError('Unresolved canonical placeholder')
    return output,deps

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--register',type=Path,required=True);a.add_argument('--template',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
    receipt=args.output.with_suffix(args.output.suffix+'.sources.json')
    if args.output.exists() or receipt.exists(): raise SystemExit('Use a new output/version; refusing overwrite')
    text,deps=render(args.template.read_text(encoding='utf-8-sig'),json.loads(args.register.read_text(encoding='utf-8-sig')))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text,encoding='utf-8');receipt.write_text(json.dumps({'dependencies':deps,'output_sha256':hashlib.sha256(text.encode()).hexdigest(),'review':'Mechanical exact-text reuse only; semantic/source/disclosure/public review still required'},indent=2)+'\n',encoding='utf-8')

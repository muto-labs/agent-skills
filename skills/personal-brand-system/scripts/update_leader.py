"""Preview a standard update; apply with backup and conflict preservation."""
from pathlib import Path
import argparse,json,hashlib,shutil,datetime,uuid,runpy,re

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def version(s): return tuple(int(x) for x in s.split('.'))
def inside(root,rel):
    p=root/rel
    if p.is_symlink() or not p.resolve().is_relative_to(root.resolve()): raise ValueError('Unsafe update path: '+rel)
    return p

def update(standard,leader,apply=False):
    standard,leader=standard.resolve(),leader.resolve()
    if standard==leader or standard in leader.parents or leader in standard.parents: raise ValueError('Use separate standard and personal folders')
    statepath=leader/'references/onboarding-state.json';state=json.loads(statepath.read_text(encoding='utf-8-sig'))
    source=json.loads((standard/'references/onboarding-state.json').read_text(encoding='utf-8-sig'))
    if source.get('output_prefix') or any(i['state']!='not started' for i in source['items']) or source['time_events']: raise ValueError('Source must be a clean standard')
    if version(source['standard_version'])<version(state['standard_version']): raise ValueError('Downgrade refused')
    manifest=json.loads((standard/'references/standard-files.json').read_text(encoding='utf-8'))
    priorpath=leader/'references/installed-standard.json';prior=json.loads(priorpath.read_text(encoding='utf-8')) if priorpath.exists() else {}
    installs=[];conflicts=[];unchanged=[]
    for rel,meta in manifest['files'].items():
        src=inside(standard,rel);dst=inside(leader,rel)
        if sha(src)!=meta['sha256']: raise ValueError('Standard manifest mismatch: '+rel)
        if dst.exists() and sha(dst)==meta['sha256']: unchanged.append(rel);continue
        known=set(meta.get('previous_hashes',[]));old=prior.get('files',{}).get(rel)
        if old: known.add(old)
        if dst.exists() and sha(dst) not in known: conflicts.append(rel)
        else: installs.append(rel)
    # Personal registries are added only when absent, never overwritten.
    new_personal=[rel for rel in ['references/integrity-register.json'] if not inside(leader,rel).exists()]
    report={'version':source['standard_version'],'update_files':installs,'unchanged':unchanged,'conflicts_preserved':conflicts,'new_personal_defaults':new_personal,'applied':False}
    if not apply:return report
    for q in leader.rglob('*'):
        if q.is_symlink():raise ValueError('Symlink in package; use manual update')
    backup=leader.parent/(leader.name+'-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8])
    shutil.copytree(leader,backup)
    report['backup']=str(backup)
    for rel in installs+new_personal:
        dst=inside(leader,rel);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(inside(standard,rel),dst)
    method=(standard/'SKILL.md').read_text(encoding='utf-8').replace('(references/','(')
    (leader/'references/standard-method.md').write_text(method,encoding='utf-8')
    entry=leader/'SKILL.md';text=entry.read_text(encoding='utf-8-sig')
    if 'references/standard-method.md' not in text:text+='\n## Current standard method\nRead [current standard method](references/standard-method.md) for the updated workflow. Preserve this leader’s facts, accepted assets, preferences and restrictions. Conflicts in update-report.md require review.\n'
    entry.write_text(text,encoding='utf-8')
    installed=prior.get('files',{})
    installed.update({rel:manifest['files'][rel]['sha256'] for rel in installs+unchanged})
    (leader/'references/installed-standard.json').write_text(json.dumps({'files':installed},indent=2)+'\n',encoding='utf-8')
    if not conflicts:
        state['standard_version']=source['standard_version'];statepath.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    report['applied']=True;report['method_fully_updated']=not conflicts
    (leader/'references/update-report.md').write_text('# Standard update report\nKeep this backup private. Customized conflicts remain unchanged and need manual review.\n\n```json\n'+json.dumps(report,indent=2)+'\n```\n',encoding='utf-8')
    runpy.run_path(str(leader/'scripts/build_dashboard.py'))['build'](leader)
    # Validation reports failures without attempting a destructive rollback.
    checker=runpy.run_path(str(leader/'scripts/check_package.py'))
    if checker['check_links'](leader):raise ValueError('Link validation failed; inspect backup and update report')
    checker['summarize'](state)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--standard',type=Path,required=True);p.add_argument('--leader',type=Path,required=True);p.add_argument('--apply',action='store_true');a=p.parse_args();print(json.dumps(update(a.standard,a.leader,a.apply),indent=2))

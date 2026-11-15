# SPDX-License-Identifier: Apache-2.0
"""Configuration-driven intake; standard library only (IANA zones need tzdata on Windows)."""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
import wave
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

VERSION = '0.1.0'
PACKAGE = Path(__file__).resolve().parent.parent


def read(path):
    return Path(path).read_text(encoding='utf-8-sig')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, text, expected=None):
    path = Path(path)
    if expected is not None and read(path) != expected:
        raise RuntimeError(f'Concurrent edit: {path}; reconcile before retrying')
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.voice-intake.tmp')
    temp.write_text(text, encoding='utf-8', newline='\n')
    temp.replace(path)
    if read(path) != text:
        raise RuntimeError(f'Readback failed: {path}')


def dump(path, value):
    save(path, json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def inside(path, root):
    return Path(path).resolve().is_relative_to(Path(root).resolve())


def load_config(path):
    c = json.loads(read(path))
    if c.get('schema_version') != 1:
        raise ValueError('Unsupported configuration schema')
    for key in ('vault_directory', 'archive_directory', 'source_directory', 'timezone'):
        if not c.get(key):
            raise ValueError(f'Onboarding must supply {key}')
    roots = [Path(c[k]).expanduser() for k in ('vault_directory', 'archive_directory', 'source_directory')]
    if any(not p.is_absolute() for p in roots):
        raise ValueError('Directories must be absolute')
    for i, first in enumerate(roots):
        for second in roots[i + 1:]:
            if inside(first, second) or inside(second, first):
                raise ValueError('Vault, archive and source must be separate non-nested directories')
    if any(inside(p, PACKAGE) or inside(PACKAGE, p) for p in roots):
        raise ValueError('Keep user data and package directories separate')
    for key in ('intake_name','dictionary_name','log_name','act_name','wins_name'):
        value = c.get(key, '')
        if not value.endswith('.md') or Path(value).name != value or re.search(r'[<>:"/\\|?*\[\]]', value):
            raise ValueError(f'{key} must be a simple Markdown filename')
    names = [c[k].casefold() for k in ('intake_name','dictionary_name','log_name','act_name','wins_name')]
    if len(names) != len(set(names)):
        raise ValueError('Control note filenames must be distinct')
    folder = c.get('notes_folder', '')
    if not folder or re.search(r'[<>:"/\\|?*\[\]]', folder) or folder in ('.','..') or folder.endswith(('.', ' ')):
        raise ValueError('notes_folder must be one safe folder name')
    if c.get('cleanup_style') not in ('light','verbatim'):
        raise ValueError('Supported cleanup styles: light, verbatim')
    if not c.get('language') or not c.get('whisper_model'):
        raise ValueError('Language and Whisper model required')
    url = urllib.parse.urlparse(c['voicebox_api'])
    if url.scheme != 'http' or url.hostname not in ('127.0.0.1','localhost','::1') or url.username or url.password:
        raise ValueError('v0.1 supports a local unauthenticated Voicebox HTTP API only')
    if not 0 <= c.get('week_end_day', -1) <= 6 or not 0 <= c.get('rollover_hour', -1) <= 23 or not 0 <= c.get('rollover_minute', -1) <= 59:
        raise ValueError('Invalid rollover day/time')
    for key in ('actions_enabled','recorder_deletion_enabled','setup_approved','first_recording_reviewed','scheduling_requested'):
        if type(c.get(key)) is not bool:
            raise ValueError(f'{key} must be a JSON boolean')
    c['_zone'] = ZoneInfo(c['timezone'])
    return c


def now(c):
    return datetime.now(c['_zone'])


def root(c, key):
    return Path(c[key]).expanduser().resolve()


def control(c, key):
    return root(c, 'vault_directory') / c[key]


def duplicates(c, fingerprint):
    pattern = re.compile(r'^audio_sha256:\s*[\'\"]?' + fingerprint + r'[\'\"]?\s*$', re.M)
    return [str(p) for p in root(c,'vault_directory').rglob('*.md')
            if '.obsidian' not in p.parts and pattern.search(read(p))]


def initialize(c):
    if not c['setup_approved']:
        raise ValueError('User approval of setup settings is required')
    vault = root(c,'vault_directory')
    if not vault.is_dir():
        raise ValueError('Select an existing Obsidian vault')
    title = lambda key: Path(c[key]).stem
    ending = now(c).date() + timedelta(days=(c['week_end_day'] - now(c).weekday()) % 7)
    templates = {
        'intake_name': f"[[{title('dictionary_name')}]] · [[{title('log_name')}]]\n\n# Voice Note Intake\n\n| Note | Recorded | Note created | Duration | Words | Audio | Status |\n|---|---|---|---|---:|---|---|\n",
        'dictionary_name': '# Voice Note Dictionary\n\nVersion: 1\n\n## Confirmed terms\n\nNo terms configured yet. Add user-confirmed spelling and meaning.\n\n## Suggestions\n\nNo open suggestions.\n',
        'log_name': '# Voice Note Processing Log\n',
        'act_name': f"# {title('act_name')}\n\n# Voice Note ACT - {ending.strftime('%m.%d.%y')}\n\nLast verified rollover: none.\n",
        'wins_name': f"# {title('wins_name')}\n\nCompleted tasks retain IDs, source context and original dates.\n"
    }
    selected = ['intake_name','dictionary_name','log_name'] + (['act_name','wins_name'] if c['actions_enabled'] else [])
    # Check compatibility before creating any starter file.
    if control(c,'intake_name').exists():
        table_span(read(control(c,'intake_name')))
    if c['actions_enabled'] and control(c,'act_name').exists() and not re.search(r'^# Voice Note ACT - \d{2}\.\d{2}\.\d{2}',read(control(c,'act_name')),re.M):
        raise ValueError('Existing ACT has no compatible sprint heading; review rather than overwrite')
    created, retained = [], []
    for key in selected:
        target = control(c,key)
        if target.exists():
            retained.append(str(target))
        else:
            save(target,templates[key]); created.append(str(target))
    (vault / c['notes_folder']).mkdir(exist_ok=True)
    root(c,'archive_directory').mkdir(parents=True,exist_ok=True)
    return dict(created=created,retained=retained,deletion_enabled=c['recorder_deletion_enabled'],scheduler_created=False)


def doctor(c):
    report = dict(version=VERSION,python=sys.version.split()[0],powershell=shutil.which('pwsh'),
                  timezone=c['timezone'],vault_exists=root(c,'vault_directory').is_dir(),
                  source_exists=root(c,'source_directory').is_dir(),deletion_enabled=c['recorder_deletion_enabled'])
    try:
        with urllib.request.urlopen(c['voicebox_api'].rstrip('/')+'/health', timeout=10) as response:
            report['voicebox'] = json.load(response)
    except Exception as error:
        report['voicebox_error'] = str(error)
    return report


def speech(c, audio):
    boundary = 'muto-voice-note-boundary'
    parts = []
    for key,value in (('language',c['language']),('model',c['whisper_model'])):
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
    parts += [f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="segment.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode(), audio, f'\r\n--{boundary}--\r\n'.encode()]
    request = urllib.request.Request(c['voicebox_api'].rstrip('/')+'/transcribe',data=b''.join(parts),headers={'Content-Type':f'multipart/form-data; boundary={boundary}'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request,timeout=120) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise


def transcribe(c, source, replay=False):
    if not c['setup_approved']:
        raise ValueError('Setup not approved')
    source = Path(source).resolve(strict=True)
    if source.suffix.lower() != '.wav' or (source.parent != root(c,'source_directory') and not (replay and inside(source,root(c,'archive_directory')))):
        raise ValueError('Use a WAV in the configured source folder, or explicit archived replay')
    fingerprint = digest(source)
    matches = duplicates(c,fingerprint)
    if matches:
        return dict(status='duplicate',notes=matches,source_deleted=False)
    archive = root(c,'archive_directory') / source.name
    if archive.exists() and digest(archive) != fingerprint:
        archive = archive.with_name(archive.stem+'-'+fingerprint[:12]+'.wav')
    if archive.exists() and digest(archive) != fingerprint:
        raise ValueError('Archive collision')
    metadata = source.stat()
    archive.parent.mkdir(parents=True,exist_ok=True)
    if not archive.exists():
        shutil.copy2(source,archive)
    if digest(archive) != fingerprint:
        raise RuntimeError('Archive copy checksum mismatch')
    state = archive.parent / (archive.stem+'.transcription')
    state.mkdir(exist_ok=True)
    manifest_path = state/'manifest.json'
    # Never reset publication/deletion history when resuming transcription.
    existing = json.loads(read(manifest_path)) if manifest_path.exists() else {}
    if existing.get('audio_sha256') not in (None,fingerprint):
        raise RuntimeError('Manifest fingerprint conflict')
    with wave.open(str(archive),'rb') as wav:
        channels, width, rate, frames = wav.getnchannels(),wav.getsampwidth(),wav.getframerate(),wav.getnframes()
        if width != 2 or wav.getcomptype() != 'NONE' or frames <= 0:
            raise ValueError('Supported audio is nonempty uncompressed PCM16 WAV')
        jobs = [(offset,min(20*rate,frames-offset),'main') for offset in range(0,frames,18*rate)]
        jobs.append((max(0,frames-8*rate),min(frames,8*rate),'tail-check'))
        results = []
        for index,(offset,count,kind) in enumerate(jobs):
            path = state/f'{index:05d}-{kind}.json'
            cached = json.loads(read(path)) if path.exists() else {}
            valid = (cached.get('audio_sha256') == fingerprint and cached.get('model') == c['whisper_model'] and cached.get('language') == c['language'] and cached.get('offset_frames') == offset and cached.get('frame_count') == count and isinstance(cached.get('result',{}).get('text'),str) and abs(cached.get('result',{}).get('duration',-1)-count/rate)<.05)
            if valid:
                segment = cached
            else:
                wav.setpos(offset); payload = wav.readframes(count)
                if len(payload) != count*width*channels:
                    raise ValueError('WAV audio data is truncated; retain source')
                buffer = io.BytesIO()
                with wave.open(buffer,'wb') as chunk:
                    chunk.setnchannels(channels);chunk.setsampwidth(width);chunk.setframerate(rate);chunk.writeframes(payload)
                chunk_path = state/f'{index:05d}-{kind}.wav'
                chunk_path.write_bytes(buffer.getvalue())
                print(f'Transcribing {index+1}/{len(jobs)} at {offset/rate:.2f}s',file=sys.stderr,flush=True)
                began = now(c)
                result = speech(c,buffer.getvalue())
                if not isinstance(result.get('text'),str) or abs(result.get('duration',-1)-count/rate)>.05:
                    raise RuntimeError('Invalid segment response')
                segment = dict(audio_sha256=fingerprint,model=c['whisper_model'],language=c['language'],offset_frames=offset,frame_count=count,start_seconds=offset/rate,duration_seconds=count/rate,kind=kind,result=result,processing_seconds=(now(c)-began).total_seconds())
                dump(path,segment)
            results.append(segment)
    stamp = lambda seconds: datetime.fromtimestamp(seconds,c['_zone']).isoformat()
    manifest = dict(source=str(source),archive=str(archive),audio_sha256=fingerprint,bytes=metadata.st_size,
                    original_created=stamp(metadata.st_ctime),original_modified=stamp(metadata.st_mtime),
                    archived_at=existing.get('archived_at',now(c).isoformat()),completed_at=now(c).isoformat(),
                    duration_seconds=frames/rate,sample_rate=rate,channels=channels,segments=results,
                    replay=replay,source_deleted=existing.get('source_deleted',False))
    coverage(manifest)
    dump(manifest_path,manifest)
    return dict(status='transcribed',manifest=str(manifest_path),duration_seconds=frames/rate,segments=len(results))


def coverage(m):
    covered = 0
    mains = sorted([s for s in m['segments'] if s['kind']=='main'],key=lambda s:s['start_seconds'])
    for segment in mains:
        if segment['audio_sha256'] != m['audio_sha256'] or segment['start_seconds']<0 or segment['start_seconds']>covered+.001 or not 0<segment['duration_seconds']<=20.01 or not isinstance(segment['result'].get('text'),str) or abs(segment['result']['duration']-segment['duration_seconds'])>.05:
            raise ValueError('Invalid segment or coverage gap')
        covered=max(covered,segment['start_seconds']+segment['duration_seconds'])
    tails=[s for s in m['segments'] if s['kind']=='tail-check']
    if not mains or abs(covered-m['duration_seconds'])>.001 or len(tails)!=1:
        raise ValueError('Incomplete audio coverage')
    tail=tails[0]
    if tail['audio_sha256']!=m['audio_sha256'] or abs(tail['start_seconds']+tail['duration_seconds']-covered)>.001 or not isinstance(tail['result'].get('text'),str):
        raise ValueError('Independent ending check missing')
    return covered


def table_span(text):
    match=re.search(r'^\| Note \|[^\n]*\n\|[-:| ]+\|\n(?:\|[^\n]*\|\n)*',text,re.M)
    if not match:
        raise ValueError('Intake table format incompatible; review existing content')
    return match


def publish(c, manifest_path, draft_path):
    if not c['setup_approved']:
        raise ValueError('Setup not approved')
    manifest_path=Path(manifest_path).resolve()
    if not inside(manifest_path,root(c,'archive_directory')):
        raise ValueError('Manifest must be in the configured archive')
    m=json.loads(read(manifest_path)); d=json.loads(read(draft_path)); coverage(m)
    if digest(m['archive'])!=m['audio_sha256'] or not inside(m['archive'],root(c,'archive_directory')):
        raise ValueError('Archive checksum/path mismatch')
    for field in ('title','summary','transcript','recorded_at','recorded_date_source'):
        if not isinstance(d.get(field),str) or not d[field].strip():
            raise ValueError(f'Draft missing {field}')
    if any(d.get(f) is not True for f in ('content_reviewed','overlaps_reviewed','ending_reviewed')) or d.get('unresolved_completeness') is not False:
        raise ValueError('Content, overlaps and ending require review')
    if any(not isinstance(a,str) or not a.strip() or '\n' in a or '\r' in a for a in d.get('actions',[])):
        raise ValueError('Actions must be nonempty single-line strings')
    if re.search(r'[<>:"/\\|?*\r\n\[\]]',d['title']) or d['title'].endswith(('.', ' ')) or len(d['title'])>100:
        raise ValueError('Unsafe title')
    recorded=datetime.fromisoformat(d['recorded_at'])
    if recorded.tzinfo is None:
        raise ValueError('Recording timestamp requires explicit offset')
    recorded=recorded.astimezone(c['_zone'])
    vault=root(c,'vault_directory'); journal=manifest_path.parent/'publication.json'
    draft_hash=hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
    if journal.exists():
        receipt=json.loads(read(journal))
        if receipt['audio_sha256']!=m['audio_sha256'] or receipt['draft_sha256']!=draft_hash:
            raise ValueError('Publication draft changed; reconcile existing journal')
        if receipt['status']=='complete':
            if not Path(receipt['note']).exists() or digest(receipt['note'])!=receipt.get('note_sha256'):
                raise ValueError('Completed publication note missing or changed; reconcile journal')
            return dict(status='duplicate',note=receipt['note'],source_deleted=m.get('source_deleted',False))
    else:
        matches=duplicates(c,m['audio_sha256'])
        if matches:
            return dict(status='duplicate',notes=matches,source_deleted=False)
        base='vn-'+recorded.strftime('%y-%m-%d')+' '+d['title'];name=base+'.md';suffix=2
        while list(vault.rglob(name)):
            name=f'{base}-{suffix:02d}.md';suffix+=1
        target=vault/c['notes_folder']/name
        receipt=dict(status='pending',audio_sha256=m['audio_sha256'],draft_sha256=draft_hash,note=str(target),created_at=now(c).isoformat(),stages=[])
        dump(journal,receipt)
    target=Path(receipt['note'])
    if target.parent!=vault/c['notes_folder']:
        raise ValueError('Publication journal points outside note destination')
    words=len(re.findall(r"\b\w+(?:['’-]\w+)*\b",d['transcript']))
    timestamp=receipt.setdefault('created_at',now(c).isoformat())
    props=dict(type='voice-note',recorded_at=recorded.isoformat(),recorded_date_source=d['recorded_date_source'],original_audio_filename=Path(m['source']).name,original_file_created_at=m['original_created'],original_file_modified_at=m['original_modified'],audio_archived_at=m['archived_at'],note_created_at=timestamp,note_saved_to_vault_at=timestamp,note_creation_method='created-directly-in-vault',transcription_completed_at=m['completed_at'],transcription_model_requested=c['whisper_model'],transcription_language=c['language'],audio_duration_seconds=m['duration_seconds'],audio_size_bytes=m['bytes'],audio_sha256=m['audio_sha256'],transcript_word_count=words,word_count_scope='cleaned-transcript-only',estimated_words_per_minute=round(words/(m['duration_seconds']/60),1),segment_coverage_seconds=m['duration_seconds'],main_segment_count=sum(s['kind']=='main' for s in m['segments']),dictionary_version=d.get('dictionary_version',1),recorder_original_deleted=False)
    yaml='---\n'+'\n'.join(f'{key}: {json.dumps(value,ensure_ascii=False)}' for key,value in props.items())+'\n---\n'
    actions='\n'.join('- [ ] '+a for a in d.get('actions',[])) or 'No explicit actions identified.'
    notes='\n'.join('- '+str(n) for n in d.get('review_notes',[]))
    body=yaml+f"\n[[{Path(c['intake_name']).stem}]] · [[{Path(c['dictionary_name']).stem}]]\n\n# {d['title']}\n\n## Summary\n\n{d['summary']}\n\n## Actions\n\n{actions}\n\n## Full Transcript\n\n{d['transcript']}\n\n## Recording and Review\n\n- [Original audio]({Path(m['archive']).as_uri()})\n- [Raw segment manifest]({manifest_path.as_uri()})\n{notes}\n- Agent reviewed overlaps, content and ending; human review may still find recognition errors.\n"
    if 'note' not in receipt['stages']:
        if target.exists() and read(target)!=body:
            raise ValueError('Existing note differs from pending publication; reconcile')
        save(target,body); receipt['stages'].append('note');dump(journal,receipt)
    intake_path=control(c,'intake_name');intake=read(intake_path);match=table_span(intake)
    link='[['+target.stem+']]'
    if link not in match[0]:
        lines=match[0].rstrip().splitlines();seconds=int(m['duration_seconds']);duration=f'{seconds//3600:02d}:{seconds//60%60:02d}:{seconds%60:02d}'
        row=f'| {link} | {recorded.strftime("%Y-%m-%d %H:%M:%S")} | {timestamp} | {duration} | {words} | [WAV]({Path(m["archive"]).as_uri()}) | Verified; original retained |'
        rows=lines[2:]+[row];rows.sort(key=lambda r:r.split('|')[2].strip(),reverse=True)
        replacement='\n'.join(lines[:2]+rows)+'\n'
        save(intake_path,intake[:match.start()]+replacement+intake[match.end():],intake)
    if c['actions_enabled']:
        import task_engine
        task_engine.configure(c)
        task_engine.sync(vault,target,now(c))
        receipt['actions_consolidated']=True
    log_path=control(c,'log_name');log=read(log_path);token=f'publication: {m["audio_sha256"]}'
    if token not in log:
        save(log_path,log+f'\n- {timestamp} — Created {link}; {words} words; source retained; {token}.\n',log)
    if not target.exists() or link not in read(intake_path) or token not in read(log_path):
        raise RuntimeError('Output verification failed; source retained')
    receipt['note_sha256']=digest(target)
    receipt['verified_note_sha256']=receipt['note_sha256']
    receipt['status']='complete';dump(journal,receipt)
    return dict(status='created',note=str(target),words=words,source_deleted=False)


def finalize(c, manifest_path):
    if not c['recorder_deletion_enabled'] or not c['first_recording_reviewed']:
        raise ValueError('Deletion permission and first-user-review confirmation are required')
    path=Path(manifest_path).resolve()
    if not inside(path,root(c,'archive_directory')):
        raise ValueError('Manifest outside archive')
    m=json.loads(read(path));coverage(m)
    receipt=json.loads(read(path.parent/'publication.json'))
    if receipt.get('status')!='complete' or receipt['audio_sha256']!=m['audio_sha256'] or m.get('replay'):
        raise ValueError('Only completed non-replay intake can delete source')
    source=Path(m['source']).resolve();archive=Path(m['archive']).resolve()
    if source.parent!=root(c,'source_directory') or source==archive or not inside(archive,root(c,'archive_directory')):
        raise ValueError('Unsafe source or archive path')
    if digest(archive)!=m['audio_sha256']:
        raise ValueError('Archive checksum mismatch')
    note=Path(receipt['note'])
    if note.parent!=root(c,'vault_directory')/c['notes_folder'] or m['audio_sha256'] not in read(note):
        raise ValueError('Published note missing or modified fingerprint')
    original_text=read(note).replace('recorder_original_deleted: true','recorder_original_deleted: false')
    if hashlib.sha256(original_text.encode()).hexdigest()!=receipt.get('verified_note_sha256'):
        raise ValueError('Published note changed since verification; retain source and reconcile')
    if '[['+note.stem+']]' not in read(control(c,'intake_name')):
        raise ValueError('Intake entry missing')
    if f'publication: {m["audio_sha256"]}' not in read(control(c,'log_name')):
        raise ValueError('Publication log missing')
    if c['actions_enabled']:
        if not receipt.get('actions_consolidated'):
            raise ValueError('Action consolidation not verified')
        import task_engine
        section=re.search(r'^## Actions\s*\n(.*?)(?=^## |\Z)',read(note),re.M|re.S)
        task_text=read(control(c,'act_name'))+read(control(c,'wins_name'))
        for line in section[1].splitlines():
            match=task_engine.TASK.match(line)
            if match:
                key=hashlib.sha256(task_engine.normalized(match[3]).encode()).hexdigest()[:8]
                if f'{m["audio_sha256"]}:{key}' not in task_text:
                    raise ValueError('Consolidated action missing; retain source')
    # Record intent first, so a crash immediately after unlink can be reconciled.
    intent=path.parent/'deletion.json'
    if source.exists():
        if digest(source)!=m['audio_sha256']:
            raise ValueError('Source changed')
        dump(intent,dict(source=str(source),audio_sha256=m['audio_sha256'],requested_at=now(c).isoformat()))
        source.unlink()
    elif not intent.exists():
        raise ValueError('Source missing with no verified deletion intent')
    else:
        previous=json.loads(read(intent))
        if previous['source']!=str(source) or previous['audio_sha256']!=m['audio_sha256']:
            raise ValueError('Deletion intent mismatch')
    m['source_deleted']=True;m['source_deleted_at']=m.get('source_deleted_at',now(c).isoformat());dump(path,m)
    text=read(note)
    text=text.replace('recorder_original_deleted: false','recorder_original_deleted: true')
    save(note,text)
    intake_path=control(c,'intake_name');text=read(intake_path)
    lines=text.splitlines()
    for i,line in enumerate(lines):
        if '[['+note.stem+']]' in line and line.startswith('|'):
            lines[i]=line.replace('Verified; original retained','Verified; original deleted')
    save(intake_path,'\n'.join(lines)+'\n',text)
    log_path=control(c,'log_name');text=read(log_path);token=f'deletion: {m["audio_sha256"]}'
    if token not in text:
        save(log_path,text+f'\n- {m["source_deleted_at"]} — Recorder original deleted; archive retained; {token}.\n',text)
    # Keep the original verification hash for deletion recovery, plus current note hash for replay.
    receipt['note_sha256']=digest(note)
    dump(path.parent/'publication.json',receipt)
    return dict(status='source-deleted',archive_retained=str(archive))


def cli():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['doctor','setup','transcribe','publish','finalize','sync','rollover'])
    parser.add_argument('--config',required=True);parser.add_argument('--source');parser.add_argument('--replay',action='store_true')
    parser.add_argument('--manifest');parser.add_argument('--draft');parser.add_argument('--note')
    args=parser.parse_args();c=load_config(args.config)
    if args.command=='doctor':result=doctor(c)
    elif args.command=='setup':result=initialize(c)
    elif args.command=='transcribe':result=transcribe(c,args.source,args.replay)
    elif args.command=='publish':result=publish(c,args.manifest,args.draft)
    elif args.command=='finalize':result=finalize(c,args.manifest)
    else:
        if not c['actions_enabled'] or not c['setup_approved']:
            raise ValueError('Action tracking disabled or setup not approved')
        import task_engine
        task_engine.configure(c)
        result=task_engine.sync(root(c,'vault_directory'),Path(args.note),now(c)) if args.command=='sync' else task_engine.rollover(root(c,'vault_directory'),now(c))
    print(json.dumps(result,ensure_ascii=True))


if __name__=='__main__':
    try:cli()
    except Exception as error:
        print(json.dumps(dict(status='error',error=str(error))),file=sys.stderr)
        sys.exit(1)

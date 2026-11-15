# SPDX-License-Identifier: Apache-2.0
"""Consolidate sourced voice-note actions and safely roll completed tasks into WINs."""
import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

SETTINGS = {}
WEEK_END = 5
ROLLOVER_HOUR = 18
ROLLOVER_MINUTE = 0

def configure(config):
    global SETTINGS, WEEK_END, ROLLOVER_HOUR, ROLLOVER_MINUTE
    SETTINGS = config
    WEEK_END = config['week_end_day']
    ROLLOVER_HOUR = config['rollover_hour']
    ROLLOVER_MINUTE = config['rollover_minute']

TASK = re.compile(r'^(\s*)- \[([ xX])\] (.+)$')
ID = re.compile(r'\bid: (VN-[A-Za-z0-9-]+)')


def read(path):
    return path.read_text(encoding='utf-8-sig')


def write(path, text, expected=None):
    if expected is not None and read(path) != expected:
        raise RuntimeError(f'Concurrent change: {path}; source tasks retained')
    temp = path.with_suffix(path.suffix + '.voice-tasks.tmp')
    temp.write_text(text, encoding='utf-8')
    temp.replace(path)
    if read(path) != text:
        raise RuntimeError(f'Readback failed: {path}')


def week_end(day):
    return day + timedelta(days=(WEEK_END - day.weekday()) % 7)


def task_text(value):
    return value.split(' — id:', 1)[0].strip()


def normalized(value):
    return re.sub(r'\s+', ' ', task_text(value)).casefold().rstrip('.')


def nodes(text):
    result = []
    for index, line in enumerate(text.splitlines()):
        match = TASK.match(line)
        if match:
            ident = ID.search(match[3])
            result.append(dict(index=index, indent=len(match[1].expandtabs(4)),
                               done=match[2].lower() == 'x', text=match[3],
                               id=ident[1] if ident else None))
    return result


def sync(vault, note, now):
    act_path, wins_path = vault / SETTINGS['act_name'], vault / SETTINGS['wins_name']
    act, wins = read(act_path), read(wins_path)
    initial_act = act
    text = read(note)
    hash_match = re.search(r'^audio_sha256:\s*[\'\"]?([a-f0-9]{64})', text, re.M)
    if not hash_match:
        raise RuntimeError('Voice note fingerprint required')
    section = re.search(r'^## Actions\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    if not section:
        raise RuntimeError('Actions section missing')
    actions = [match[3] for line in section[1].splitlines()
               if (match := TASK.match(line))]
    additions, added, linked = [], [], []
    active_nodes, archived_nodes = nodes(act), nodes(wins)
    for action in actions:
        # Completion in a source note is not automatically completion evidence for ACT.
        clean = task_text(action)
        key = hashlib.sha256(normalized(clean).encode()).hexdigest()[:8]
        ident = f'VN-{hash_match[1][:12]}-{key}'
        origin = f'{hash_match[1]}:{key}'
        if origin in act or origin in wins or any(f'origin: {origin}' in line for line in additions):
            continue
        same = next((n for n in active_nodes + archived_nodes
                     if normalized(n['text']) == normalized(clean)), None)
        source = f'[[{note.stem}#Actions]]'
        if same:
            target_path = act_path if same in active_nodes else wins_path
            before = act if target_path == act_path else wins
            lines = before.splitlines()
            lines[same['index']] += f'; source: {source}; origin: {origin}'
            after = '\n'.join(lines) + '\n'
            if target_path == act_path:
                act = after
            else:
                write(wins_path, after, wins)
                wins = after
            linked.append(same['id'])
            continue
        additions.append(f'- [ ] {clean} — id: {ident}; owner: {SETTINGS.get('default_owner', 'unassigned')}; captured: {now.date()}; source: {source}; origin: {origin}')
        added.append(ident)
    if additions:
        heading = f'# Voice Note ACT - {week_end(now.date()).strftime("%m.%d.%y")}'
        if heading not in act:
            act = act.rstrip() + '\n\n' + heading + '\n\n'
        act = act.rstrip() + '\n' + '\n'.join(additions) + '\n'
    before = read(act_path)
    if act != before:
        # Check against initial read, not just a fresh read, to preserve concurrent edits.
        write(act_path, act, initial_act)
    return dict(added=added,linked=linked,source=str(note))


def rollover(vault, now):
    act_path, wins_path = vault / SETTINGS['act_name'], vault / SETTINGS['wins_name']
    act, wins = read(act_path), read(wins_path)
    cutoff = now.replace(hour=ROLLOVER_HOUR, minute=ROLLOVER_MINUTE, second=0, microsecond=0)
    cutoff -= timedelta(days=(now.weekday() - WEEK_END) % 7)
    if now < cutoff:
        cutoff -= timedelta(days=7)
    marker = re.search(r'^Last verified rollover: (\d{4}-\d{2}-\d{2})', act, re.M)
    if marker and marker[1] >= str(cutoff.date()):
        pending_path = vault / '.voice-note-rollover-pending.json'
        if pending_path.exists():
            pending = json.loads(read(pending_path))
            for entry in pending['entries']:
                if entry['text'] not in wins or any(ID.search(n['text']) and n['id'] in entry['ids'] for n in nodes(act)):
                    raise RuntimeError('Pending rollover inconsistent with verified marker')
            pending_path.unlink()
        return dict(status='already-rolled',closing_week=str(cutoff.date()))
    current_week = re.search(r'^# Voice Note ACT - (\d{2}\.\d{2}\.\d{2})', act, re.M)
    if not current_week:
        raise RuntimeError('Current ACT week missing')
    closing = datetime.strptime(current_week[1], '%m.%d.%y').date()
    if closing > cutoff.date():
        return dict(status='before-cutoff',closing_week=str(closing))
    lines = act.splitlines()
    tasks = nodes(act)
    pending_path = vault / '.voice-note-rollover-pending.json'
    eligible, occupied = [], set()
    for pos, task in enumerate(tasks):
        descendants = []
        for following in tasks[pos + 1:]:
            if following['indent'] <= task['indent']:
                break
            descendants.append(following)
        if task['done'] and any(not child['done'] for child in descendants):
            lines[task['index']] = lines[task['index']].replace('[x]', '[ ]', 1).replace('[X]', '[ ]', 1)
        if not task['done'] or any(not child['done'] for child in descendants) or task['index'] in occupied:
            continue
        if not task['id'] or any(not child['id'] for child in descendants):
            raise RuntimeError('Assign stable IDs to completed tasks and descendants before rollover')
        end = task['index'] + 1
        while end < len(lines) and lines[end].strip() and not lines[end].startswith('#'):
            following_task = TASK.match(lines[end])
            indent = len(lines[end]) - len(lines[end].lstrip())
            if indent <= task['indent']:
                break
            end += 1
        block = '\n'.join(lines[task['index']:end])
        parents = [t for t in tasks[:pos] if t['indent'] < task['indent']]
        context = task_text(parents[-1]['text']) if parents else None
        eligible.append(dict(id=task['id'],ids=[task['id']]+[c['id'] for c in descendants],
                             start=task['index'],end=end,text=block,parent=context))
        occupied.update(range(task['index'],end))
    # A manifest makes an archive-write/source-removal interruption recoverable.
    manifest = dict(closing_week=str(closing),started_at=now.isoformat(),entries=eligible)
    if pending_path.exists():
        pending = json.loads(read(pending_path))
        if pending['closing_week'] != str(closing) or pending['entries'] != eligible:
            raise RuntimeError('Pending manifest differs from live tasks; reconcile before rollover')
    else:
        write(pending_path,json.dumps(manifest,indent=2))
    additions = []
    for entry in eligible:
        present = [ident for ident in entry['ids'] if re.search(r'\bid: '+re.escape(ident)+r'\b',wins)]
        if present:
            if len(present) != len(entry['ids']) or entry['text'] not in wins:
                raise RuntimeError('Archive ID/content conflict; retain ACT tasks')
            continue
        context = f"Parent context: {entry['parent']}\n\n" if entry['parent'] else ''
        additions.append(context+entry['text'])
    heading = f'## Week ending {closing}'
    if additions:
        block = '\n\n'.join(additions)+'\n'
        if heading in wins:
            wins_after = wins.replace(heading,heading+'\n\n'+block,1)
        else:
            first = re.search(r'^## Week ending ',wins,re.M)
            index = first.start() if first else len(wins.rstrip())
            wins_after = wins[:index].rstrip()+'\n\n'+heading+'\n\n'+block+'\n'+wins[index:]
        write(wins_path,wins_after,wins)
        wins = read(wins_path)
    for entry in eligible:
        if entry['text'] not in wins or any(not re.search(r'\bid: '+re.escape(i)+r'\b',wins) for i in entry['ids']):
            raise RuntimeError('Archive readback failed; retain ACT tasks')
    retained = [line for index,line in enumerate(lines) if index not in occupied]
    after = '\n'.join(retained)+'\n'
    next_end = week_end((cutoff+timedelta(days=1)).date())
    after = re.sub(r'^# Voice Note ACT - \d{2}\.\d{2}\.\d{2}',f'# Voice Note ACT - {next_end.strftime("%m.%d.%y")}',after,flags=re.M)
    after = re.sub(r'^Last verified rollover:.*$',f'Last verified rollover: {cutoff.date()}; verified: {now.isoformat()}',after,flags=re.M)
    if 'Last verified rollover:' not in after:
        after += f'\nLast verified rollover: {cutoff.date()}; verified: {now.isoformat()}\n'
    # Preserve original deadlines and all unfinished nested blocks, with stable IDs.
    write(act_path,after,act)
    reread = read(act_path)
    for task in tasks:
        if not task['done'] and task['id'] and task['id'] not in reread:
            raise RuntimeError('Unfinished task missing; inspect pending manifest')
    pending_path.unlink()
    return dict(status='rolled',closing_week=str(closing),archived=[e['id'] for e in eligible],verified_through=str(cutoff.date()))

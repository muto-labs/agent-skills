"""Read-only three-way method upgrade preview; never writes into a personal package."""
import argparse
import hashlib
import json
from pathlib import Path

EXCLUDED = {'__pycache__', 'outputs', 'history', 'years', 'sources', 'fonts', 'node_modules', '.git'}
EXCLUDED_FILES = {'plan.json', 'knowledge.md', 'method-baseline.json', 'standard-files.json', 'strategic-plan-standard.html'}
EXTENSIONS = {'.md', '.json', '.py', '.js', '.cjs', '.css', '.html', '.yaml'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def method_manifest(root):
    root = Path(root).resolve()
    if (root / 'plan.json').exists() or (root / 'knowledge.md').exists():
        raise ValueError('Use a clean standard as the method source')
    files = {}
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if not path.is_file() or set(relative.parts) & EXCLUDED or path.name in EXCLUDED_FILES or path.suffix not in EXTENSIONS:
            continue
        if not path.resolve().is_relative_to(root):
            raise ValueError('Method files must stay inside the standard')
        files[relative.as_posix()] = digest(path)
    return {'standard_version': json.loads((root / 'assets/plan-template.json').read_text(encoding='utf-8'))['standard_version'], 'files': files}


def preview(new_standard, personal, base_standard=None):
    personal = Path(personal).resolve()
    new = method_manifest(new_standard)
    baseline = personal / 'method-baseline.json'
    if base_standard:
        base = method_manifest(base_standard)
    elif baseline.is_file():
        base = json.loads(baseline.read_text(encoding='utf-8'))
    else:
        base = {'standard_version': None, 'files': {}}
    changes = []
    for relative, new_hash in new['files'].items():
        current = (personal / relative).resolve()
        if not current.is_relative_to(personal):
            raise ValueError('Unsafe target method path')
        current_hash = digest(current) if current.is_file() else None
        old_hash = base['files'].get(relative)
        if current_hash == new_hash:
            state = 'unchanged'
        elif current_hash is None and old_hash is None:
            state = 'safe-add'
        elif old_hash is not None and current_hash == old_hash:
            state = 'safe-update'
        else:
            state = 'conflict-preserve-local'
        changes.append({'path': relative, 'state': state})
    return {'mode': 'preview-only', 'base_version': base.get('standard_version'), 'new_version': new['standard_version'], 'baseline_available': bool(base['files']), 'changes': changes, 'conflicts': sum(c['state'] == 'conflict-preserve-local' for c in changes), 'protected': ['plan.json', 'knowledge.md', 'years/', 'history/', 'outputs/', 'personal source assets', 'external vault notes'], 'instructions': 'Back up before a deliberate merge. Review conflicts and preserve local customizations. This tool performs no writes and does not bump the personal method version.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('new_standard', type=Path)
    parser.add_argument('personal_package', type=Path)
    parser.add_argument('--base', type=Path, help='Optional original clean standard for pre-baseline packages')
    args = parser.parse_args()
    try:
        print(json.dumps(preview(args.new_standard, args.personal_package, args.base), indent=2))
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f'Preview failed: {exc}\n')

"""Create an empty personal package without overwriting an existing destination."""
import argparse
import json
from datetime import date
from pathlib import Path
import shutil
from build_dashboard import build, ROOT
from plan_upgrade import method_manifest


def initialize(destination, name='', initials='', year=None):
    if (ROOT / 'plan.json').exists() or (ROOT / 'knowledge.md').exists():
        raise ValueError('Initialize new people from the clean standard, never a personal package')
    destination = destination.resolve()
    if destination.exists():
        raise ValueError('Destination already exists; resume it instead of reinitializing')
    if destination.is_relative_to(ROOT):
        raise ValueError('Personal packages must be outside the shared standard')
    manifest = method_manifest(ROOT)
    shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns('__pycache__', 'strategic-plan-standard.html'))
    data = json.loads((ROOT / 'assets/plan-template.json').read_text(encoding='utf-8'))
    data['person'] = {'name': name, 'initials': initials}
    year = year if year is not None else date.today().year
    data['years'] = [{'year': year, 'status': 'draft', 'current_quarter': 1,
                      'word': None, 'objectives': [], 'reviews': [], 'stop_doing': [], 'quarter_reviews': {}}]
    (destination / 'plan.json').write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    shutil.copyfile(ROOT / 'assets/kb-template.md', destination / 'knowledge.md')
    skill = destination / 'SKILL.md'
    skill.write_text(skill.read_text(encoding='utf-8').replace('name: personal-strategic-plan\n',
                     'name: my-personal-strategic-plan\n', 1).replace('# Personal Strategic Plan\n',
                     '# Personal Strategic Plan\nPersonal package: plan.json and knowledge.md contain private user records. Do not share this folder as the standard or initialize another person from it.\n', 1), encoding='utf-8')
    (destination / 'method-baseline.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return build(destination / 'plan.json', destination / 'outputs/strategic-plan.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--name', default='')
    parser.add_argument('--initials', default='')
    parser.add_argument('--year', type=int)
    args = parser.parse_args()
    try:
        print(initialize(args.destination, args.name, args.initials, args.year))
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Initialization failed: {exc}\n')

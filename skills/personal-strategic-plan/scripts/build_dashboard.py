"""Build a private, offline, read-only HTML view from canonical plan.json. Stdlib only."""
import argparse
import base64
import copy
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PILLARS = ('God', 'Fit', 'Fam', 'Biz', '$', 'Up')


def accepted(row, field):
    return row.get(field, row.get('review_state')) == 'accepted'


def local_file(package, relative, extensions, limit):
    if not isinstance(relative, str) or not relative:
        raise ValueError('A source path must be a nonempty package-relative string')
    path = (package / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(package.resolve()):
        raise ValueError('Source files must stay inside the package')
    if path.suffix.lower() not in extensions or not path.is_file() or path.stat().st_size > limit:
        raise ValueError('Unsupported, missing, or oversized source file')
    return path


def data_url(path, mime):
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def validate(data):
    if data.get('schema_version') != '1.0':
        raise ValueError('Unsupported schema_version')
    seen_years, seen_ids = set(), set()
    for year in data.get('years', []):
        y = year['year']
        if not isinstance(y, int) or isinstance(y, bool) or y in seen_years:
            raise ValueError('Year must be a unique integer')
        seen_years.add(y)
        if year.get('status', 'draft') not in ('draft', 'accepted'):
            raise ValueError('Year status must be draft or accepted')
        rows = year.get('objectives', [])
        annual = {}
        groups = {}
        for row in rows:
            key = row['id']
            if not isinstance(key, str) or not key or key in seen_ids:
                raise ValueError('TO IDs must be globally unique nonempty strings')
            seen_ids.add(key)
            if row['pillar'] not in PILLARS or isinstance(row.get('quarter'), bool) or row.get('quarter') not in (None, 1, 2, 3, 4):
                raise ValueError(f'{key}: invalid pillar or quarter')
            if row.get('year', y) != y:
                raise ValueError(f'{key}: record year differs from containing plan year')
            if row.get('status', 'Backlog') not in ('Backlog', 'Doing', 'Done'):
                raise ValueError(f'{key}: invalid status')
            if row.get('review_state', 'draft') not in ('draft', 'accepted', 'superseded'):
                raise ValueError(f'{key}: invalid review_state')
            if row.get('metric') not in ('#', '$', '%', 'T'):
                raise ValueError(f'{key}: invalid metric')
            for field in ('start', 'target', 'current', 'weight'):
                v = row.get(field)
                if v is not None and (isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v)):
                    raise ValueError(f'{key}: {field} must be a finite number or null')
            if row.get('quarter') is None:
                if row.get('parent_id'):
                    raise ValueError(f'{key}: annual TO cannot have a parent')
                if row.get('review_state') != 'superseded':
                    if row['pillar'] in annual:
                        raise ValueError('Only one current annual TO per pillar')
                    annual[row['pillar']] = row
            else:
                if row.get('weight', 100) is None or not 0 <= row.get('weight', 100) <= 100:
                    raise ValueError(f'{key}: weight outside 0–100')
                if row.get('review_state') != 'superseded':
                    groups.setdefault((row['pillar'], row['quarter']), []).append(row)
        for row in rows:
            if row.get('quarter'):
                parent = next((p for p in rows if p['id'] == row.get('parent_id')), None)
                if not parent or parent.get('quarter') is not None or parent['pillar'] != row['pillar']:
                    raise ValueError(f'{row["id"]}: missing or mismatched annual parent')
        for key, group in groups.items():
            total = sum(r.get('weight', 100) for r in group)
            if total > 100.000001:
                raise ValueError(f'{key}: quarterly weights exceed 100%')
            if all(r.get('review_state') == 'accepted' for r in group) and abs(total - 100) > .000001:
                raise ValueError(f'{key}: accepted quarterly weights must total 100%')
        for q, review in year.get('quarter_reviews', {}).items():
            if str(q) not in ('1', '2', '3', '4') or review.get('state') not in ('draft', 'locked'):
                raise ValueError('Invalid quarter review')
            if review['state'] == 'locked':
                committed = [r for r in rows if r.get('quarter') == int(q) and r.get('review_state') != 'superseded']
                if any(r.get('review_state') != 'accepted' or not accepted(r, 'target_review_state') or not accepted(r, 'weight_review_state') for r in committed):
                    raise ValueError('Locked quarters require accepted targets and weights')
        if year.get('status') == 'accepted' and (len(annual) != 6 or any(r.get('review_state') != 'accepted' for r in annual.values())):
            raise ValueError('An accepted year requires six accepted annual TOs')
        if year.get('status') == 'accepted':
            foundation = year.get('foundation') or {}
            if any((foundation.get(k) or {}).get('review_state') != 'accepted' for k in ('purpose', 'tenets', 'grit')):
                raise ValueError('An accepted year requires its own accepted foundation snapshot')
            if (year.get('word') or {}).get('review_state') != 'accepted':
                raise ValueError('An accepted year requires an accepted Word of the Year')
            word = year['word']
            if not word.get('meaning') or word.get('meaning_review_state', 'accepted') != 'accepted':
                raise ValueError('An accepted year requires an accepted focus-word definition')
    return data


def prepare(data, package):
    """Only accepted brand tokens are used. Local images stay within the package."""
    result = copy.deepcopy(data)
    result.pop('_embedded_font', None)
    brand = result.get('brand', {})
    theme = {}
    if brand.get('status') == 'accepted':
        for key in ('accent', 'sidebar', 'background'):
            color = brand.get('colors', {}).get(key, '')
            if re.fullmatch(r'#[0-9a-fA-F]{6}', color):
                theme[key] = color
        font = brand.get('font_family', '')
        if re.fullmatch(r'[a-zA-Z0-9 ,\-]{1,100}', font):
            theme['font_family'] = font
        logo = brand.get('logo_path')
        if logo:
            path = local_file(package, logo, ('.png', '.jpg', '.jpeg', '.webp'), 2_000_000)
            mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}.get(path.suffix.lower())
            if not mime or not path.is_file() or path.stat().st_size > 2_000_000:
                raise ValueError('Logo must be an existing PNG/JPEG/WebP of at most 2 MB')
            theme['logo'] = 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')
        if brand.get('font_path'):
            family = brand.get('font_family', '')
            if not re.fullmatch(r'[a-zA-Z0-9 \-]{1,80}', family):
                raise ValueError('An embedded font needs a simple font-family name')
            path = local_file(package, brand['font_path'], ('.ttf', '.woff2'), 5_000_000)
            mime, fmt = ('font/ttf', 'truetype') if path.suffix.lower() == '.ttf' else ('font/woff2', 'woff2')
            result['_embedded_font'] = {'family': family, 'src': data_url(path, mime), 'format': fmt}
    result['_theme'] = theme
    for year in result.get('years', []):
        for row in year.get('objectives', []):
            row['_related_images'] = []
            for relative in row.get('related_assets', []):
                path = local_file(package, relative, ('.png', '.jpg', '.jpeg', '.webp'), 5_000_000)
                mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}[path.suffix.lower()]
                detail = row.get('related_asset_details', {}).get(relative, {})
                row['_related_images'].append({'src': data_url(path, mime), 'title': detail.get('title', path.stem), 'alt': detail.get('alt', detail.get('title', path.stem)), 'caption': detail.get('caption', ''), 'path': relative})
            # Legacy worksheet key is supported without making its naming a default.
            worksheets = list(row.get('worksheets', []))
            if row.get('aim_template'):
                worksheets.append({'path': row['aim_template'], 'title': 'Moment template'})
            row['_worksheets'] = []
            for sheet in worksheets:
                path = local_file(package, sheet['path'], ('.md',), 100_000)
                row['_worksheets'].append({'title': sheet.get('title', 'Planning & reflection template'), 'text': path.read_text(encoding='utf-8')})
    # A view needs snapshots and visible source labels, not private source paths.
    result.get('brand', {}).pop('logo_path', None)
    return result


def build(source, output):
    data = validate(json.loads(source.read_text(encoding='utf-8-sig')))
    data = prepare(data, source.parent)
    font = data.pop('_embedded_font', None)
    payload = json.dumps(data, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    template = (ROOT / 'assets/dashboard/template.html').read_text(encoding='utf-8')
    html = template.replace('/*__CSS__*/', (ROOT / 'assets/dashboard/style.css').read_text(encoding='utf-8'))
    if font:
        face = "@font-face{font-family:'" + font['family'] + "';src:url(" + font['src'] + ") format('" + font['format'] + "');font-style:normal;font-weight:100 1000;font-display:swap;}"
        html = html.replace('<style>', '<style>' + face, 1)
    html = html.replace('/*__APP__*/', (ROOT / 'assets/dashboard/app.js').read_text(encoding='utf-8'))
    html = html.replace('__PLAN_DATA__', payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding='utf-8')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Canonical personal plan.json, or the blank standard template')
    parser.add_argument('--output', type=Path, help='Default: source parent / outputs / strategic-plan.html')
    args = parser.parse_args()
    try:
        print(build(args.source.resolve(), (args.output or args.source.parent / 'outputs/strategic-plan.html').resolve()))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f'Build failed: {exc}\n')

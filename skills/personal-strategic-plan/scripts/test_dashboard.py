"""Synthetic build and boundary checks. No personal files are read."""
import copy
import base64
import json
import os
from pathlib import Path
import tempfile
import unittest
from build_dashboard import ROOT, build, prepare, validate
from init_plan import initialize
from plan_upgrade import method_manifest, preview, digest
from quarter_pacing import calculate

TEST_BASE = Path(os.environ.get('SP_TEST_TMP', Path.cwd() / 'outputs/strategic-plan-test-tmp')).resolve()
TEST_BASE.mkdir(parents=True, exist_ok=True)

def temporary():
    return tempfile.TemporaryDirectory(dir=TEST_BASE)


def fixture():
    d = json.loads((ROOT / 'assets/plan-template.json').read_text(encoding='utf-8'))
    annual = {'id':'fit-annual','pillar':'Fit','quarter':None,'description':'Walk regularly',
              'metric':'#','unit':'miles','start':0,'target':100,'current':25,
              'measurement':'Qualifying miles logged in the calendar year', 'review_state':'accepted'}
    q = dict(annual, id='fit-q1', quarter=1, parent_id='fit-annual', target=25, weight=100)
    d['years'] = [{'year':2030,'status':'draft','objectives':[annual,q]}]
    return d


class DashboardTests(unittest.TestCase):
    def test_calendar_math(self):
        self.assertEqual(calculate(2032, 1, 2)['days'], 91)
        self.assertEqual(calculate(2032, 1, 2)['exact_total'], 26)
        ordinary = calculate(2031, 1, 2)
        self.assertEqual((ordinary['days'], ordinary['full_weeks'], ordinary['extra_days']), (90, 12, 6))
        self.assertEqual((ordinary['rounded_down'], ordinary['rounded_up']), (25, 26))
        self.assertEqual(calculate(2031, 4)['end'], '2031-12-31')

    def test_valid_and_blank(self):
        validate(fixture())
        validate(json.loads((ROOT/'assets/plan-template.json').read_text(encoding='utf-8')))

    def test_weights_and_parent(self):
        for mutate in (
            lambda d:d['years'][0]['objectives'][1].update(weight=120),
            lambda d:d['years'][0]['objectives'][1].update(weight=60),
            lambda d:d['years'][0]['objectives'][1].update(parent_id='missing'),
            lambda d:d['years'][0]['objectives'][1].update(current=float('nan')),
        ):
            d=fixture();mutate(d)
            with self.assertRaises(ValueError):validate(d)
        d=fixture();d['years'][0]['objectives'][1].update(weight=60,review_state='draft');validate(d)

    def test_script_text_cannot_break_data_element(self):
        with temporary() as tmp:
            p=Path(tmp); d=fixture();d['person']['name']='</script><script>globalThis.injected=true</script>'
            (p/'plan.json').write_text(json.dumps(d),encoding='utf-8')
            out=build(p/'plan.json',p/'view.html').read_text(encoding='utf-8')
            self.assertNotIn('</script><script>globalThis.injected',out)
            self.assertIn('\\u003c/script\\u003e',out)

    def test_brand_restrictions(self):
        with temporary() as tmp:
            d=fixture();d['brand'].update(status='draft',colors={'accent':'#ffcc00'})
            self.assertEqual(prepare(d,Path(tmp))['_theme'],{})
            d['brand'].update(status='accepted',logo_path='../outside.png')
            with self.assertRaises(ValueError):prepare(d,Path(tmp))
            d['brand'].update(logo_path='',colors={'accent':'red; background:url(https://example.invalid)'})
            self.assertNotIn('accent',prepare(d,Path(tmp))['_theme'])

    def test_local_images_worksheets_fonts_and_escape(self):
        with temporary() as tmp:
            p = Path(tmp)
            (p/'pixel.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l9sAAAAASUVORK5CYII='))
            (p/'worksheet.md').write_text('# Synthetic worksheet\n<script>injected=true</script>',encoding='utf-8')
            (p/'font.ttf').write_bytes(b'synthetic-font-payload')
            d = fixture(); row=d['years'][0]['objectives'][0]
            row.update(related_assets=['pixel.png'], worksheets=[{'title':'Worksheet','path':'worksheet.md'}], importance='<img onerror=bad>')
            d['brand'].update(status='accepted',font_family='Fixture Sans',font_path='font.ttf')
            ready = prepare(d,p)
            self.assertTrue(ready['years'][0]['objectives'][0]['_related_images'][0]['src'].startswith('data:image/png;base64,'))
            self.assertIn('<script>',ready['years'][0]['objectives'][0]['_worksheets'][0]['text'])
            (p/'plan.json').write_text(json.dumps(d),encoding='utf-8')
            output=build(p/'plan.json',p/'out.html').read_text(encoding='utf-8')
            self.assertIn('@font-face',output)
            self.assertIn('font-src data:',output)
            self.assertNotIn('<script>injected=true</script>',output)
            for relative in ('../outside.png','https://example.invalid/image.png'):
                row['related_assets']=[relative]
                with self.assertRaises(ValueError):prepare(d,p)
            row['related_assets']=[]
            row['worksheets']=[{'path':'../outside.md'}]
            with self.assertRaises(ValueError):prepare(d,p)
            row['worksheets']=[]
            d['brand']['font_path']='../outside.ttf'
            with self.assertRaises(ValueError):prepare(d,p)
            d['brand'].update(status='draft')
            d['_embedded_font']={'family':'<bad>','src':'bad'}
            self.assertNotIn('_embedded_font',prepare(d,p))

    def test_locking_and_activation_do_not_invent_progress(self):
        d=fixture();q=d['years'][0]['objectives'][1]
        q.update(status='Doing',activated_at='2029-12-01',current=None)
        d['years'][0]['quarter_reviews']={'1':{'state':'locked','locked_at':'2029-12-01','open_items':['Counting detail deliberately deferred']}}
        validate(d)
        self.assertIsNone(q['current'])
        self.assertEqual(q['quarter'],1)
        q['weight_review_state']='draft'
        with self.assertRaises(ValueError):validate(d)

    def test_upgrade_preview_preserves_customizations(self):
        with temporary() as tmp:
            root=Path(tmp);base=root/'base';new=root/'new';personal=root/'person'
            for directory in (base,new,personal):
                (directory/'assets').mkdir(parents=True)
            for directory,version in ((base,'0.2.2'),(new,'0.3.0')):
                (directory/'assets/plan-template.json').write_text(json.dumps({'standard_version':version}),encoding='utf-8')
                (directory/'SKILL.md').write_text('method '+version,encoding='utf-8')
                (directory/'renderer.js').write_text('old renderer' if directory==base else 'new renderer',encoding='utf-8')
            (personal/'renderer.js').write_text('custom renderer',encoding='utf-8')
            (personal/'SKILL.md').write_text((base/'SKILL.md').read_text(encoding='utf-8'),encoding='utf-8')
            (personal/'plan.json').write_text('{"private":"preserve"}',encoding='utf-8')
            (personal/'knowledge.md').write_text('private notes',encoding='utf-8')
            (personal/'method-baseline.json').write_text(json.dumps(method_manifest(base)),encoding='utf-8')
            before={str(p.relative_to(personal)):digest(p) for p in personal.rglob('*') if p.is_file()}
            result=preview(new,personal)
            states={c['path']:c['state'] for c in result['changes']}
            self.assertEqual(states['renderer.js'],'conflict-preserve-local')
            self.assertEqual(states['SKILL.md'],'safe-update')
            self.assertNotIn('plan.json',states)
            self.assertEqual(before,{str(p.relative_to(personal)):digest(p) for p in personal.rglob('*') if p.is_file()})
            self.assertEqual(preview(new,personal,base)['base_version'],'0.2.2')

    def test_initialization_preserves_existing_and_standard(self):
        with temporary() as tmp:
            dest=Path(tmp)/'personal'
            output=initialize(dest,year=2030)
            self.assertTrue(output.is_file())
            self.assertTrue((dest/'method-baseline.json').is_file())
            original=(dest/'plan.json').read_bytes()
            with self.assertRaises(ValueError):initialize(dest,year=2031)
            self.assertEqual(original,(dest/'plan.json').read_bytes())
            self.assertNotIn('Person Example',(ROOT/'assets/plan-template.json').read_text(encoding='utf-8'))


if __name__=='__main__':unittest.main()

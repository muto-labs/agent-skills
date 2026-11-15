# SPDX-License-Identifier: Apache-2.0
import ast
import io
import json
import sys
import threading
import tempfile
import unittest
import uuid
import wave
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

PACKAGE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PACKAGE/'scripts'))
import intake
import task_engine


class MockVoicebox(BaseHTTPRequestHandler):
    requests=0
    def log_message(self,*args):
        pass
    def do_GET(self):
        self.send_response(200);self.end_headers();self.wfile.write(b'{"status":"healthy"}')
    def do_POST(self):
        type(self).requests+=1
        data=self.rfile.read(int(self.headers['Content-Length']))
        offset=data.index(b'RIFF');size=int.from_bytes(data[offset+4:offset+8],'little')+8
        with wave.open(io.BytesIO(data[offset:offset+size]),'rb') as wav:
            duration=wav.getnframes()/wav.getframerate()
        self.send_response(200);self.end_headers()
        self.wfile.write(json.dumps(dict(text='Beginning middle ending marker.',duration=duration)).encode())


class IntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),MockVoicebox)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def setUp(self):
        # Never create fixtures within the distributable or touch a real user's directories.
        base=Path.cwd()/'.voice-note-portable-tests'
        if base.resolve().is_relative_to(PACKAGE):
            base=Path(tempfile.gettempdir())/'muto-voice-note-portable-tests'
        base.mkdir(exist_ok=True)
        if base.resolve().is_relative_to(PACKAGE):
            raise RuntimeError('Run tests from the directory containing the skill folder, not inside it')
        self.home=base/uuid.uuid4().hex;self.home.mkdir()
        self.vault=self.home/'vault';self.vault.mkdir()
        self.source=self.home/'recorder';self.source.mkdir()
        self.archive=self.home/'archive'
        c=json.loads(intake.read(PACKAGE/'config.example.json'))
        c.update(vault_directory=str(self.vault),archive_directory=str(self.archive),source_directory=str(self.source),timezone='UTC',setup_approved=True,voicebox_api=f'http://127.0.0.1:{self.server.server_port}')
        self.config_path=self.home/'settings.json';intake.dump(self.config_path,c)
        self.c=intake.load_config(self.config_path);intake.initialize(self.c)
        self.audio=self.source/'sample.wav'
        with wave.open(str(self.audio),'wb') as wav:
            wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(16000);wav.writeframes(b'\0\0'*int(42.5*16000))
    def prepare(self,actions=None):
        result=intake.transcribe(self.c,self.audio)
        self.manifest=Path(result['manifest'])
        self.draft=self.home/'draft.json'
        intake.dump(self.draft,dict(title='Synthetic Test',summary='Synthetic summary.',actions=actions or [],transcript='Beginning middle ending marker.',recorded_at='2026-10-20T10:00:00+00:00',recorded_date_source='synthetic fixture',dictionary_version=1,review_notes=['Mock API; not an accuracy evaluation.'],content_reviewed=True,overlaps_reviewed=True,ending_reviewed=True,unresolved_completeness=False))
        return result
    def snapshot(self):
        return {str(p):intake.digest(p) for p in self.home.rglob('*') if p.is_file()}
    def test_setup_preserves_existing(self):
        note=intake.control(self.c,'dictionary_name');note.write_text('User dictionary',encoding='utf-8')
        intake.initialize(self.c);self.assertEqual(intake.read(note),'User dictionary')
        self.assertFalse(intake.control(self.c,'act_name').exists())
    def test_setup_rejects_incompatible_intake_before_changes(self):
        path=intake.control(self.c,'intake_name');path.write_text('Existing prose',encoding='utf-8')
        before=self.snapshot()
        with self.assertRaises(ValueError):intake.initialize(self.c)
        self.assertEqual(before,self.snapshot())
    def test_config_rejects_overlap_and_unsafe_filenames(self):
        c=json.loads(intake.read(self.config_path));c['archive_directory']=str(self.source/'nested');intake.dump(self.config_path,c)
        with self.assertRaises(ValueError):intake.load_config(self.config_path)
        c['archive_directory']=str(self.archive);c['log_name']='../escape.md';intake.dump(self.config_path,c)
        with self.assertRaises(ValueError):intake.load_config(self.config_path)
    def test_setup_permission(self):
        self.c['setup_approved']=False
        with self.assertRaises(ValueError):intake.initialize(self.c)
        with self.assertRaises(ValueError):intake.transcribe(self.c,self.audio)
    def test_segment_duration_end_and_resume(self):
        self.prepare();m=json.loads(intake.read(self.manifest))
        self.assertEqual(intake.coverage(m),42.5);self.assertEqual(len(m['segments']),4)
        count=MockVoicebox.requests
        with patch.object(intake,'speech',side_effect=AssertionError('Resume called API')):
            intake.transcribe(self.c,self.audio)
        self.assertEqual(count,MockVoicebox.requests)
    def test_publish_and_duplicate_no_writes(self):
        self.prepare();result=intake.publish(self.c,self.manifest,self.draft)
        self.assertEqual(Path(result['note']).parent,self.vault/'Voice Notes')
        before=self.snapshot()
        self.assertEqual(intake.publish(self.c,self.manifest,self.draft)['status'],'duplicate')
        with patch.object(intake,'speech',side_effect=AssertionError('Duplicate called API')):
            self.assertEqual(intake.transcribe(self.c,self.audio)['status'],'duplicate')
        self.assertEqual(before,self.snapshot())
    def test_review_required(self):
        self.prepare();d=json.loads(intake.read(self.draft));d['content_reviewed']=False;intake.dump(self.draft,d)
        with self.assertRaises(ValueError):intake.publish(self.c,self.manifest,self.draft)
        self.assertTrue(self.audio.exists());self.assertEqual(len(list((self.vault/'Voice Notes').glob('*.md'))),0)
    def test_partial_publication_resumes_without_duplicate(self):
        self.prepare(['Write report'])
        original=intake.save
        def fail_log(path,text,expected=None):
            if Path(path)==intake.control(self.c,'log_name'):raise OSError('simulated failure')
            return original(path,text,expected)
        with patch.object(intake,'save',side_effect=fail_log):
            with self.assertRaises(OSError):intake.publish(self.c,self.manifest,self.draft)
        self.assertTrue(self.audio.exists())
        result=intake.publish(self.c,self.manifest,self.draft)
        self.assertEqual(result['status'],'created');self.assertEqual(len(list((self.vault/'Voice Notes').glob('*.md'))),1)
    def test_delete_defaults_off(self):
        self.prepare();intake.publish(self.c,self.manifest,self.draft)
        with self.assertRaises(ValueError):intake.finalize(self.c,self.manifest)
        self.assertTrue(self.audio.exists())
    def test_delete_after_review_and_idempotent(self):
        self.prepare();intake.publish(self.c,self.manifest,self.draft)
        self.c.update(recorder_deletion_enabled=True,first_recording_reviewed=True)
        self.assertEqual(intake.finalize(self.c,self.manifest)['status'],'source-deleted')
        self.assertFalse(self.audio.exists());self.assertTrue((self.archive/'sample.wav').exists())
        self.assertEqual(intake.finalize(self.c,self.manifest)['status'],'source-deleted')
    def test_replay_cannot_delete(self):
        first=self.prepare();self.manifest=Path(first['manifest'])
        m=json.loads(intake.read(self.manifest));m['replay']=True;intake.dump(self.manifest,m)
        intake.publish(self.c,self.manifest,self.draft);self.c.update(recorder_deletion_enabled=True,first_recording_reviewed=True)
        with self.assertRaises(ValueError):intake.finalize(self.c,self.manifest)
        self.assertTrue(self.audio.exists())
    def test_missing_intake_or_changed_audio_blocks_delete(self):
        self.prepare();intake.publish(self.c,self.manifest,self.draft);self.c.update(recorder_deletion_enabled=True,first_recording_reviewed=True)
        intake.control(self.c,'intake_name').write_text('Missing entry',encoding='utf-8')
        with self.assertRaises(ValueError):intake.finalize(self.c,self.manifest)
        self.assertTrue(self.audio.exists())
    def test_non_pcm16_stops(self):
        with wave.open(str(self.audio),'wb') as wav:
            wav.setnchannels(1);wav.setsampwidth(1);wav.setframerate(8000);wav.writeframes(b'\0'*8000)
        with self.assertRaises(ValueError):intake.transcribe(self.c,self.audio)
        self.assertTrue(self.audio.exists())
    def test_truncated_wav_stops_without_deleting(self):
        data=self.audio.read_bytes();self.audio.write_bytes(data[:-10000])
        with self.assertRaises(ValueError):intake.transcribe(self.c,self.audio)
        self.assertTrue(self.audio.exists())
    def test_filename_collision_preserves_both_audio_files(self):
        self.archive.mkdir(exist_ok=True);original=self.archive/'sample.wav'
        original.write_bytes(b'different existing audio');before=intake.digest(original)
        result=self.prepare();m=json.loads(intake.read(self.manifest))
        self.assertNotEqual(Path(m['archive']),original);self.assertEqual(before,intake.digest(original))
    def test_changed_note_blocks_cleanup(self):
        self.prepare();result=intake.publish(self.c,self.manifest,self.draft)
        path=Path(result['note']);path.write_text(intake.read(path).replace('Beginning middle ending marker.','User-edited transcript.'),encoding='utf-8')
        self.c.update(recorder_deletion_enabled=True,first_recording_reviewed=True)
        with self.assertRaises(ValueError):intake.finalize(self.c,self.manifest)
        self.assertTrue(self.audio.exists())
    def test_actions_config_names_and_rollover(self):
        self.c.update(actions_enabled=True,act_name='My Tasks.md',wins_name='My Wins.md',week_end_day=4,rollover_hour=17,rollover_minute=30)
        intake.initialize(self.c);self.prepare(['Write report']);intake.publish(self.c,self.manifest,self.draft)
        task_engine.configure(self.c);act=intake.control(self.c,'act_name');wins=intake.control(self.c,'wins_name')
        text=intake.read(act);text=text.replace('Voice Note ACT - '+re_heading(text),'Voice Note ACT - 10.23.26').replace('- [ ] Write report','- [x] Write report')
        text+='\n- [x] Parent — id: VN-parent; due: 2026-10-20\n  - [x] Completed child — id: VN-done\n  - [ ] Unfinished child — id: VN-open\n'
        intake.save(act,text)
        self.assertEqual(task_engine.rollover(self.vault,datetime.fromisoformat('2026-10-23T17:29:00+00:00'))['status'],'before-cutoff')
        self.assertEqual(task_engine.rollover(self.vault,datetime.fromisoformat('2026-10-23T17:31:00+00:00'))['status'],'rolled')
        self.assertIn('Write report',intake.read(wins));self.assertNotIn('Write report',intake.read(act))
        self.assertIn('Unfinished child',intake.read(act));self.assertIn('due: 2026-10-20',intake.read(act))
        self.assertIn('Completed child',intake.read(wins))
        before=self.snapshot();self.assertEqual(task_engine.rollover(self.vault,datetime.fromisoformat('2026-10-23T17:32:00+00:00'))['status'],'already-rolled');self.assertEqual(before,self.snapshot())
    def test_windows_zone_data_and_python_syntax(self):
        for path in (PACKAGE/'scripts').glob('*.py'):
            ast.parse(intake.read(path),feature_version=(3,11))
        self.assertIsNotNone(intake.ZoneInfo('America/New_York'))


def re_heading(text):
    import re
    return re.search(r'^# Voice Note ACT - (\S+)',text,re.M)[1]


if __name__=='__main__':unittest.main()

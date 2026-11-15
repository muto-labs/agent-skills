# Guided onboarding

The AI guides decisions; scripts validate settings. Do not customize package code for each user.

## Read-only discovery

Confirm Windows, Python 3.11+, PowerShell 7, and the selected Obsidian vault. Discover recorder drives with PowerShell (`Get-PSDrive -PSProvider FileSystem`), then inspect candidate source folders without copying/deleting. Ask which device if ambiguous. Record formats, timestamps and clock plausibility. Find installed Voicebox and health-check the API; do not assume an executable location, running service, model or hardware acceleration. `doctor` reports runtime, source/vault existence, time-zone support and API health; the agent additionally checks Obsidian and the installed model through Voicebox's supported API/UI.

## Ask for configuration

Collect these choices progressively, reusing user-confirmed answers:

- Existing vault, source folder, separate retained-audio archive, and note subfolder. All three directories must be non-nested and separate from this package. Confirm cloud synchronization and retention implications. Do not point tests at any of them.
- IANA time zone, recording language and installed Whisper model. Python needs IANA zone data; on Windows, installing `tzdata` may be necessary with approval. Setup should not silently install dependencies.
- Light cleanup (punctuation/filler, preserve meaning) or verbatim text. v0.1 has a fixed note schema; broader custom schemas require a later release, not ad-hoc script editing.
- Starter note names and confirmed dictionary terms. Names must be unique simple `.md` filenames; no supplied personal terms. Preserve existing dictionary content.
- Optional action consolidation, ACT/WINs filenames, owner default (use unassigned when unclear), week-ending day (Monday=0 through Sunday=6), rollover hour/minute in the chosen zone.
- Whether to retain recorder originals (default) or later enable verified deletion. Whether to request a separate scheduler (default off). These are separate permissions.

Copy `config.example.json` to an external user-owned settings location. Fill required blank directories/time zone. Keep the three safety flags `setup_approved`, `first_recording_reviewed`, and `recorder_deletion_enabled` false initially. Show a proposed configuration and concrete destination changes; after approval, set `setup_approved=true`. This flag records user consent, not a permission bypass.

Run `python scripts/intake.py doctor --config <config>`. Missing dependencies, bad paths or API failures block readiness; explain the exact missing prerequisite. For approved setup, run `setup`; existing compatible control notes are preserved, incompatible intake/ACT formats stop for review. Setup must not initialize a user's unrelated folder as a new Obsidian vault.

## Test in stages

1. Run `python -m unittest discover -s tests -v`. This is synthetic audio with a mock endpoint, not an accuracy evaluation.
2. Make a separate test configuration with a temporary existing test vault, test archive and copied test source, all outside the package and the real data directories. Use a short user-selected recording with a recognizable beginning, middle and end. Make sure copying this recording is authorized. Leave deletion and scheduling disabled.
3. Run actual Voicebox segmented transcription. Compare all raw segments and the independent ending against the audio; draft, publish and inspect the note. Confirm language, dates, terminology, links, task extraction and table layout. Publish/transcribe replay must skip duplicate fingerprints without writes.
4. Return to the approved real configuration and do a first reviewed intake, retaining the recorder source. Ask whether the note accurately represents the complete recording. Only on confirmation set `first_recording_reviewed=true` and record that evidence in the user's external setup report.
5. If the user explicitly opts into cleanup, set `recorder_deletion_enabled=true`; demonstrate a verified `finalize` on an approved non-replay source. Never use an archived file as the source for this test. Keep archived WAVs permanently unless separately instructed otherwise.
6. If scheduling is requested, inspect existing jobs and use the host's scheduler tools to create/update a single rollover job referencing the external configuration and installed skill. Confirm the scheduler's time-zone interpretation and next run. `scheduling_requested=true` is only intent. Do not write a fake “enabled” report. Without a scheduler, document manual rollover and the limitation.

## External setup report

Record configuration path, inspected runtime/software versions, actual tests and dates, source/vault/archive locations, file retention choices, review evidence, supported format, enabled options, scheduler ID/time zone/next run if actually created, and unresolved limitations. Keep the report private and outside this distribution. Do not include API secrets in the report or configuration; v0.1 supports local unauthenticated Voicebox only.

Never claim hour-scale or multi-speaker accuracy from a short test. A new machine requires its own real recording test. Changes to destinations, deletion policy or synchronization require renewed review of those settings, not a wholesale rewrite of the skill.

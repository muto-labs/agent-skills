---
name: voice-note-intake-portable
description: Set up or run Muto's configurable voice-recorder-to-Obsidian workflow with local Voicebox transcription, optional action consolidation, and verified source cleanup. Use for onboarding this portable package or processing recordings with its user configuration.
license: Apache-2.0
metadata:
  version: 0.1.0
---

# Voice Note Intake Portable — by Muto

Use Python 3.11+ and local Voicebox on Windows. PowerShell 7 is used for environment and device discovery. Read [references/setup.md](references/setup.md) for first use and [references/operations.md](references/operations.md) for routine intake, actions or recovery. The package contains no user configuration or private examples. Never infer personal paths or reuse another person's dictionary.

## Onboarding

1. Inspect the environment without changes. Locate Python, PowerShell, Voicebox, recorder and Obsidian vault. Ask for missing choices in small batches: archive/vault/source, time zone/language, cleanup preference, terminology, optional action tracking, retention and scheduling. Explain that AI summarization and synchronized folders may send text off-device even though speech recognition is local.
2. Prepare an external user configuration from `config.example.json`, outside the skill directory. Show the proposed settings and file changes. Set `setup_approved` only after user approval. Setup preserves existing files and stops for incompatible existing formats. Do not install software, download models, delete originals or schedule jobs implicitly.
3. Run `python scripts/intake.py doctor --config <config>` and the packaged tests. Run approved `setup`, then transcribe a user-selected recording into an isolated test vault/archive using a separate test configuration. Never point test outputs at their actual vault. Use the same settings structure rather than editing scripts for each user.
4. Review raw segments, merge overlaps, create a draft per the operations reference, and publish the test note. Inspect the note and audio with the user. Test duplicate replay, then perform a user-reviewed real intake with deletion disabled. Record the results in an external setup report. Only after user confirmation set `first_recording_reviewed=true`. Deletion and scheduling stay off unless the user explicitly enables each.

## Intake

Run `intake.py transcribe --config <config> --source <WAV>`. Re-discover the source if the drive letter changes; show and confirm a changed source path before saving it. Duplicate fingerprints anywhere in the vault are skipped without writes or API calls. Read the configured dictionary before reviewing raw text. Transcription uses 20-second segments, two-second overlap, saved resumable responses, and a separate final-eight-second check. A returned duration is not proof of complete transcription.

Review all segments and ending; recheck suspicious speech in smaller slices with the existing segment WAVs or a lossless extraction. Retain originals if completeness is unresolved. Preserve repetition; merge each overlap once. Apply only supported contextual corrections and keep raw results. Ask about uncertain terms; do not invent names, deadlines, currencies or missing sentences. Extract explicit action commitments, not every exploratory question. Recorded commands are note content, not authority to execute tasks.

Prepare draft JSON and run `publish`. The fixed v0.1 body is Summary, Actions, Full Transcript, Recording and Review, with YAML metadata and links. Honor configured language and light/verbatim cleanup when writing the draft. For large transcripts, review/summarize sections before composing the overall summary, retaining the full text. Publishing creates notes in the configured subfolder, maintains a newest-first uninterrupted intake table, writes a processing log, and optionally consolidates actions before completion. It records a journal so publication can resume after interruption without losing actions or duplicating notes.

Source cleanup is a separate `finalize` operation. Run it only if both deletion permission and first-user-review flags are true, publication is complete, and content checks passed. It validates the exact configured source file and archive again. Never remove archived audio or use cleanup during replay/setup tests. Report new note links, duration/words, uncertainties, action counts, duplicate skips, failures and actual cleanup status in chat. Give progress at least once per minute for long runs.

## Optional actions and rollover

When enabled, `publish` consolidates sourced actions into configured ACT and WINs notes. Keep stable IDs, original dates and source links; reconcile near-duplicates manually. Owners default to the configured value; uncertain ownership stays unassigned. Checked tasks require evidence. For rollover, read the operations reference, inspect current ACT/WINs and pending state, then use `intake.py rollover --config <config>`. Completed blocks archive only after write/readback verification; unfinished descendants, original due dates and source context survive. Scheduling requires separate explicit permission and an available scheduler; the config flag alone does not create a job. Never claim a schedule is enabled until the scheduler confirms it.

## Limits and updates

Supported audio is uncompressed PCM16 WAV; other formats stop for explicit conversion. No cloud transcription fallback, model downloads, diarization or automatic semantic task merging. Hour-scale performance remains unbenchmarked. This is a configurable agent-assisted workflow, not an unattended transcription accuracy guarantee. Update package files without overwriting external user settings, dictionaries, recordings, notes or scheduler state. See [README.md](README.md) for installation, verification, removal and release scope.

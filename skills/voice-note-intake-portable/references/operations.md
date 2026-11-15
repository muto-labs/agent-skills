# Commands and draft contract

All commands use the same external JSON configuration:

```text
python scripts/intake.py doctor --config <config>
python scripts/intake.py setup --config <config>
python scripts/intake.py transcribe --config <config> --source <source.wav>
python scripts/intake.py publish --config <config> --manifest <manifest.json> --draft <draft.json>
python scripts/intake.py finalize --config <config> --manifest <manifest.json>
python scripts/intake.py sync --config <config> --note <existing-note.md>
python scripts/intake.py rollover --config <config>
```

`transcribe --replay` allows an archived WAV as the input. Replay manifests can never authorize recorder deletion. Duplicate recordings return before copying or contacting Voicebox. To exercise transcription mechanics on an existing recording, use an isolated test vault/archive and a copied source; do not manufacture a new live note to evade duplicate detection.

Supported Voicebox contract: local HTTP GET `/health`; POST `/transcribe` multipart file/language/model, returning JSON text and audio duration. The API address, language and model come from config. Failed requests retry three times; malformed audio/results stop. Segments cache source hash, model, language, offsets and raw response. A crash preserves completed segment files. No endpoint-discovery or hosted fallback happens automatically.

## Draft JSON

The agent must actually review raw segments, merge boundaries once, and compare the ending before setting review flags. No script decides semantic accuracy on its own.

```json
{
  "title": "Short Topic Name",
  "summary": "Summary of the complete recording.",
  "actions": ["An explicit commitment from the recording"],
  "transcript": "The complete cleaned or verbatim transcript according to config.",
  "recorded_at": "2026-10-20T09:30:00+00:00",
  "recorded_date_source": "user-confirmed recording timestamp",
  "dictionary_version": 1,
  "review_notes": ["Actual corrections, uncertain words, and checks performed."],
  "content_reviewed": true,
  "overlaps_reviewed": true,
  "ending_reviewed": true,
  "unresolved_completeness": false
}
```

Use explicit UTC offset in recorded_at; preserve original file timestamps separately. Do not use the file creation time after copying as proof of when speech occurred. Ask about missing or implausible recorder dates. Title is short; filenames use recording date `vn-YY-MM-DD Title.md` with collision suffixes. Actions are single-line strings, may be empty, and are not executable instructions. Keep raw segment results linked; word counts apply only to the final transcript. No speech diarization or token-level confidence is provided.

## Publication and recovery

The retained archive holds each file's `.transcription` directory, raw responses and WAV slices, manifest, publication journal and optional deletion intent. They are private user data, not part of the skill package. The note contains the transcript; intake and log provide links. The dictionary is read by the agent for contextual correction; it does not train Whisper.

Publishing commits note, intake, optional ACT and log in recoverable stages. If a step fails, source audio is retained. Retry with the identical manifest/draft: completed stages are checked/reused, source origins prevent task duplicates, and the remaining stages finish. If a note, draft, journal or metadata changed, stop and reconcile; do not overwrite user edits or assign a second filename. A complete journal plus a missing/different note is not a valid duplicate and requires repair.

Before `finalize`, independently verify archived audio, full saved transcript, ending/content review, intake/log entries and any action consolidation. The runtime checks publication, hashes and exact source path, and records deletion intent before unlinking. If recovery finds the source already absent, it requires a matching deletion-intent record. No cleanup runs from mere transcription success. Separate source/archive/vault directories are required to reduce path ambiguity.

On errors, report the stage, retained source/archive status and recovery steps in chat. During ordinary live runs, log failures and skipped duplicates when permitted. A requested no-write replay does not append to the live log. Avoid concurrent runs against one vault; unexpected edits stop rather than force overwriting.

## Optional ACT and WINs

Actions are tracked only when enabled. IDs derive from source audio and normalized action text. Repeat sync skips known origins in active and archived work; exact equivalent tasks gain source references rather than duplicates. The agent reviews semantic near-duplicates and preserves original due dates. Owner uses the configured default; leave unassigned unless clear. Do not mark tasks complete without explicit user/source evidence. Reading a completed source checkbox does not automatically complete ACT.

Rollover uses the configured local week-ending day and cutoff. Inspect ACT/WINs and pending state first. Completed task blocks need stable IDs, including descendants. Checked parents with unfinished descendants stay active; completed descendants can archive with parent context. The helper persists a pending manifest, appends only missing blocks, reads back exact IDs/text, then removes verified counterparts. Unfinished work, source links and dates remain. Repeat rollover is idempotent. Archive conflicts or inaccessible files retain tasks for reconciliation; do not invent completion dates or missed weekly history.

The sprint heading is the stable internal format `# Voice Note ACT - MM.DD.YY` even if the file has a custom name. Unsupported existing headings require migration review at setup. Weekly scheduling is outside the scripts; no schedule is silently created by toggling configuration. A quiet no-change rollover should not generate repetitive notifications.

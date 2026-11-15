# Architecture and data flow

```text
Recorder or exported PCM16 WAV
  -> Python intake: fingerprint, verify and keep an archive copy
  -> Voicebox on localhost: run Whisper on overlapping audio segments
  -> Raw segment results and manifest saved alongside the archive
  -> AI assistant: review overlaps and ending, write a structured draft
  -> Python publisher: save the Markdown note, index and processing log
  -> Obsidian: read, link and edit notes; optionally track actions in ACT/WINs
```

| Component | Role |
|---|---|
| Recorder | Produces the original WAV. The source directory is configurable; the skill does not require a particular brand. |
| PowerShell 7 | Helps the assistant discover Windows drives and inspect the environment during setup. |
| Voicebox and Whisper | Voicebox exposes a local HTTP API; Whisper converts speech to text. The Python helper sends 20-second slices with two seconds of overlap and separately checks the final eight seconds. |
| Python | Checks audio fingerprints, caches transcription results for resume, verifies and publishes files, and supports optional action consolidation and weekly rollover. |
| AI assistant | Guides onboarding, reviews transcription and uncertain language, merges overlaps, and drafts the summary and explicit actions. It does not execute commands spoken in recordings. |
| Obsidian | Opens the Markdown vault. The publisher writes Markdown files directly; it does not require an Obsidian plugin. |

Configuration is kept outside the skill. Use separate source, archive and vault folders. The archive holds the retained WAV and raw transcription data; the vault holds the readable note and links. File fingerprint checks help prevent duplicate notes. A publication journal helps resume a partially completed run. Coverage checks confirm that audio intervals were processed, but they cannot prove every word was recognized.

**Privacy boundary:** Audio is transcribed by Voicebox on localhost. The assistant may receive transcript text, and synced folders may upload audio or notes according to your settings. Use a non-sensitive sample for onboarding. Recorder deletion, automatic task capture and scheduling are off by default. Deletion is a separate verified step after opt-in and initial review; the scripts do not enroll a scheduler.

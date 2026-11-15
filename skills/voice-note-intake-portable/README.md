# Voice Note Intake Portable — Muto

Version 0.1.0 · Apache-2.0 · Windows-first, agent-assisted workflow.

Turn intentional recorder WAVs into Obsidian notes, with preserved audio,
resumable local transcription, optional action tracking and verified cleanup.

Read [how the tools fit together](references/architecture.md) for the data flow and privacy boundaries.

## Install and start

1. Extract the ZIP. Copy the `voice-note-intake-portable` folder into your
   assistant's skills directory (for Codex, typically `~/.codex/skills`).
   An existing personal `voice-note-intake` skill can remain installed separately.
2. Start a new session if the assistant does not yet list the installed skill.
3. Ask: “Use voice-note-intake-portable to inspect my system and onboard me.”
4. The assistant reads `references/setup.md`, creates your configuration outside
   the package, asks for approval, and tests in an isolated destination first.

Requires Windows, Python 3.11+, PowerShell 7, Obsidian and an installed working
Voicebox local transcription API with a Whisper model. On Windows, Python may
also need the `tzdata` package for IANA time zones. Run the doctor before setup;
install missing dependencies only with the user's approval. No software, model,
account, API key, audio or user data is bundled. No subscription is required by
these scripts; your assistant and third-party services may have their own costs.

## Verify

```text
python -m unittest discover -s tests -v
python scripts/intake.py doctor --config <your-external-config.json>
```

Tests generate synthetic WAVs and use a local mock API; they do not use private
recordings, real vaults, external network services or AI credentials. Automated
tests cover mechanics, not the accuracy of an AI's transcript merge or summary.
The setup report must distinguish mock tests from a real Voicebox recording test.
See [the validation record](references/validation.md) for actual checks and limits.

## Privacy and permissions

Local transcription does not make the whole workflow offline: your assistant
can receive transcript text, and a synced vault/archive may upload files.
Deletion and scheduler enrollment default off. Ordinary capture permissions do
not authorize executing tasks, sending messages or creating calendar events.
The skill never deletes the retained audio archive. Users decide what to record
and obtain any permissions appropriate to their situation.

## Updates and removal

Keep configuration, private setup reports, notes and audio outside this folder.
For updates, back up the installed package and replace only package files;
review schema changes before migrating configuration. To remove, disable any
separately created schedules and remove only this skill folder. Leave the user's
configuration, vault and archive intact unless the user separately requests removal.

## Distribution

Redistribute LICENSE and applicable NOTICE content with the package. The Apache
license permits commercial reuse under its terms; “free from Muto” does not
prevent others charging for their own services or modifications. Muto branding
does not imply endorsement of third-party forks; the license grants no general
trademark permission. Identify modified versions and do not misrepresent them
as official Muto releases.

Muto is credited in NOTICE. Review any third-party additions before redistributing a modified package.

# Version 0.1.0 validation record

Validated 2026-10-20 on Windows with Python 3.13 and PowerShell 7 available.
Python scripts also passed syntax parsing for the declared Python 3.11 baseline;
execution on an actual Python 3.11 installation has not been tested.

## Automated checks

18 tests passed using synthetic PCM16 audio and a loopback-only mock Voicebox:

- approved setup and preservation of existing files;
- incompatible intake format rejection before setup writes;
- non-nested paths and safe control-note names;
- segmented coverage and independent ending check;
- cached resume without repeated API calls;
- publishing into the configured note folder;
- duplicate transcription/publication replay without writes;
- required content/overlap/ending review;
- recovery after a simulated partial-publication failure;
- deletion disabled by default;
- enabled cleanup and repeated cleanup recovery;
- replay sources protected from deletion;
- missing intake and changed note checks;
- unsupported audio width and truncated WAV rejection;
- audio filename collision without overwriting the existing file;
- configurable ACT/WINs names and local rollover cutoff;
- checked-parent/unfinished-child preservation and idempotent rollover;
- IANA time-zone availability and Python syntax compatibility.

## Actual local Voicebox check

In a separate private fixture outside the distribution, a copied 69.76-second
previously reviewed WAV was processed through the actual installed Voicebox API.
Four main segments and an independent final-eight-second check were obtained.
The expected final marker was present. A reviewed merged transcript was published
into the isolated vault, actions consolidated, and duplicate replay skipped without
writes. The copied source was retained; no real recorder or live vault was modified.

The real fixture, transcript, raw responses and configuration are deliberately
not shipped. This check confirms the local API integration and mechanics, not
independent transcription/summarization accuracy. An AI's content review remains
necessary, and another user's environment requires its own recording test.

## Distribution checks and limits

- Official Apache 2.0 text is unmodified; SHA-256:
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
- Skill frontmatter validated with the skill-creator validator.
- Distribution excludes recordings, transcripts, real user settings, test fixtures,
  compiled Python caches and personal paths/terminology.
- The package creates no scheduler.
- A second tester reported successful installation and use; detailed environment and accuracy measurements were not supplied.
- No hour-scale, noisy-room or multi-speaker benchmark yet.

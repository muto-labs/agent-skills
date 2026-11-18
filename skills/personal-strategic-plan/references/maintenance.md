# Knowledge, history, views, and method maintenance

## Separation and versions
Maintain a generic standard and separate person-specific packages. Standard version and personal KB version are independent. Personal package names/locations must not enter the shared standard. Never copy a personalized package back into the standard to release an improvement.

Default private layout inside a personal package:
- `knowledge.md`: current foundation, style choices, sources, review state, and next interview checkpoint.
- `years/YYYY/plan.md`: annual recap, word, TOs, accepted plan version, and unresolved decisions.
- `years/YYYY/reviews/`: dated quarterly/year-end reviews and lessons.
- `years/YYYY/measurements.jsonl`: append-only dated TO observations, units, evidence, and corrections referencing prior observations.
- `history/`: prior accepted snapshots and revision decisions.
- `outputs/`: generated plan views and exports; not canonical inputs.

The [KB template](../assets/kb-template.md) initializes narrative knowledge only in a new personal package. Dashboard-enabled packages use plan.json as the canonical structured planning record; do not maintain competing manually edited TO tables in Markdown. Measurements retain history separately and update the current value in plan.json. See [dashboard data ownership](dashboard.md).

## Session and year boundaries
Record reviewed learning, unresolved/deferred questions, last topic and bounded interview depth, next deliverable, and source/review dates. Preserve source language alongside synthesis when meaningful. Record only known dates and active time; do not invent them.

Keep each year's accepted foundation and plan snapshot even when current identity changes. At the next year, reuse stable foundation, review it, and create new annual/quarterly IDs. Compare actuals, targets, attainment, lessons, and discontinued work. A changed unit, scope, time basis, or measurement definition must be called out; withhold misleading comparisons.

## PBS references
Follow [PBS integration](pbs-integration.md). Preserve source ID/version, imported snapshot, disclosure, and planning acceptance separately. Flag source drift for review rather than mutating finalized plans. Do not write back without a specific request and applicable PBS review.

## HTML view contract
Generate a local HTML view from the personal KB on request or when implementing that person's planning workspace. Show foundation, annual word, six annual TOs, current quarter, dated metrics/status, reviews, and year comparisons where definitions match. Use accepted brand inputs or the readable shared template style. The view must work without PBS and without a remote service.

Prefer one offline HTML file with embedded permitted style/assets; no external network calls are necessary. Escape all source text and attributes, and do not execute markup/scripts from imported notes. Separate source text from rendering code. Exclude disclosure-restricted material from shareable exports. Show unknown/draft states honestly and use text labels as well as color.

Save → regenerate → visually verify → share the actual file path → explain reopening/reloading. Read-only means the HTML cannot claim to save changes. Standard 0.3.1 bundles the renderer, initializer, and blank preview. Follow [dashboard instructions](dashboard.md) and keep generated personal views out of the standard.

## Improve and release
For a method improvement, identify the generic behavior, update the standard and version, and preserve a concise release decision with date and changed behavior. Inspect changes for personal names, paths, source imports, real objectives, images, and generated views before sharing.

Update personal packages by comparing their recorded base standard with the new standard. Back up first; preview and merge only method-owned files. Preserve knowledge, years, measurements, history, source references, accepted wording, personal overrides, and outputs. If method and personal customization changed the same file, resolve deliberately rather than overwriting. Record the resulting method version only after validation. Do not assume that a source folder has been installed or that users' copies updated automatically.

Initial release: 0.1.0 — generic guided planning method, TO definitions, optional PBS input contract, blank KB, and maintenance rules. HTML implementation and automatic migration tooling are not bundled.

0.2.0 — offline HTML workspace, brand token inputs, canonical structured plan format, non-overwriting personal initializer, build validation, and synthetic-data verification. Automatic migration tooling remains unbundled.

0.2.1 — standardized pillars and Target Objectives (TOs), visible planning year at kickoff, in-view year filters, and shared six-color template palette with personal brand overrides.

0.2.2 - annual focus word process now includes creating and explicitly accepting a hyper-focused personal definition centered on action and impact, displayed beneath the word. No personal example copied into the standard.

0.3.0 - recap-led one-pillar drafts, scope checks, calendar-aware pacing, separate definition/commitment/activation decisions, privacy-aware tracking, readiness closeout, optional context/images/fonts/worksheets and native Obsidian templates, synthetic verification, and read-only three-way upgrade previews.

New personal packages retain method-baseline.json with original clean method hashes. Preview upgrades with scripts/plan_upgrade.py; the tool never writes or upgrades by itself. An edited renderer, font behavior, knowledge store, source asset, or external vault is preserved. With no known baseline, existing differences require review instead of overwrite. Resolve a personalized SKILL.md deliberately because identity/routing may differ from the standard. Backups stay outside the shareable standard. Release only method files and the blank preview, never a personalized package or real test fixture.

0.3.1 — 2026-11-18: compact Overview, distinct pillar cards, foundation shortcuts, full Foundation with bulleted Tenets and bold opening phrases through the colon, annual TO target cards, quarterly TOs grouped by pillar, compact filters and progressive disclosure. Preserves independent tracking readiness, brand tokens, safe source rendering, and private-package separation. No schema change.

# Dashboard, source format, and delivery
Standard 0.3.1. All views share one offline HTML file with hash navigation. No account, network requests, remote fonts, or installation is needed to view it.

## Initialize and build
For a new personal package outside the standard, run:
`python scripts/init_plan.py <new-destination> --name <name> --initials <initials> --year <planning-year>`
Confirm the planning year during kickoff. If omitted, the initializer defaults to the local current calendar year; pass the intended upcoming year explicitly for advance planning. The blank standard preview shows the viewer's current calendar year without storing personal records.
Do not initialize an existing destination. The script copies the reusable method, creates a blank personal knowledge file and canonical plan.json, and builds outputs/strategic-plan.html. The standard preview is excluded from the copy.

For subsequent refreshes:
`python scripts/build_dashboard.py <personal-package>/plan.json`
Optional `--output <path>` overrides the output. Default output is beside plan.json in outputs/strategic-plan.html. Validation runs before writing. No personal import should ever be rendered into the standard directory. The only shared preview is generated from assets/plan-template.json and contains no personal records.

## Canonical data ownership
In dashboard-enabled packages, plan.json is authoritative for foundation snapshots, style, annual plans, TOs, reviews, and current metric values. knowledge.md holds narrative evidence, interview checkpoints, and source decisions; it must not maintain competing manually edited TO tables. Dated measurement/revision history is retained separately, and the latest valid measurement updates the corresponding TO in plan.json. HTML is derived and read-only.

Read assets/plan-template.json for the blank envelope. Root keys:
- schema_version: "1.0"; standard_version: method version; updated_at: supplied snapshot date/time, never invented.
- person: name and initials; empty in the standard.
- foundation: purpose, tenets, grit. Each is null or a record with text (string; tenets may be string array), review_state (draft/accepted), version, reviewed_at, source, source_version, explanation.
- brand: status (unspecified/draft/accepted), source label/version, colors, font_family, logo_path, logo_alt. Only accepted settings apply.
- years: annual records described below.
- checkpoint: next_action, open_questions and deferred (string arrays).

Annual record: year (unique integer), status (draft/accepted), current_quarter (1–4), word, optional foundation snapshot, recap, stop_doing (string array), objectives, reviews. A missing historical foundation snapshot is unknown; never fill a past year from today's foundation. The current/latest year may use the root foundation until its final snapshot is saved.
- word: text, meaning (the exact accepted hyper-focused personal definition), rationale, examples (string array), review_state. Record definition acceptance separately, such as meaning_review_state and meaning_reviewed_at; word selection alone does not approve a proposed definition. Keep proposed definition text separate until accepted, retaining the last accepted meaning if revising. The dashboard uses meaning, not an AI summary of accepted wording.
- recap: text, as_of, basis (actual results / forecast / mixed, explained).
- reviews: title, date, text, next_action.
- objectives: records with id, pillar, owner, quarter (null or 1–4), parent_id, description, metric (#/$/%/T), unit, measurement, start, target, current (numbers or null), as_of, due_date, weight, status (Backlog/Doing/Done), review_state (draft/accepted/superseded), support_rationale, disposition, source, notes. mode is scalar by default; maintenance suppresses misleading scalar progress.
- comparison_key: optional stable measure identity; compare across years only after confirming the same meaning. UI also requires identical metric, unit, measurement definition, pillar, and mode. Similar wording alone never enables comparison.

Null measurements remain unknown. Do not save formatted currency strings as numeric values. A complete accepted annual record needs six accepted annual TOs, its own accepted Purpose/Tenets/GRIT snapshot, and an accepted Word of the Year. Current quarter support weights must not exceed 100%; wholly accepted groups must total exactly 100%. A draft/incomplete group shows no aggregate. Unknown member progress also withholds aggregation. Raw overachievement remains visible; bars and weighted member progress are bounded to 0–100%.

## Brand style
Shared template palette: Huracan Orange #FC7935, Dark Cerulean #104F72, Cerulean #006799, Summer Sky #25AAE1, Charcoal #303D49, and Dark Turquoise #00C8E5. Orange is the main accent with dark button text; navigation uses Dark Cerulean. Personal accepted settings override supported template tokens.
Use PBS's accepted personal style, not its generic dashboard defaults. Store the source/version and decision in the personal KB. Supported colors: accent, sidebar, background, each a six-digit hex value. Accepted accent is preserved for buttons, progress, and decoration; readable link text may use a safe dark fallback. Foregrounds adapt to light/dark accent and sidebar colors. Backgrounds with relative luminance below 0.82 use the neutral paper fallback to preserve readability of workspace text.

font_family is an optional local CSS family stack containing only letters/numbers/spaces/commas/hyphens; system fonts are the fallback. No external font is fetched. Optional accepted font_path embeds a package-local TTF or WOFF2 up to 5 MB, using a simple single font_family name; preserve its license and source in the personal package. The standard bundles no personal font or logo. logo_path is relative to plan.json and must resolve inside that personal package. PNG/JPEG/WebP up to 2 MB are embedded; SVG and external URLs are rejected. Brand setup is optional. Imported content is escaped; source HTML is displayed as text, never executed.

## Views and behavior
Overview: annual focus with its accepted personal definition directly beneath the word, next action, six pillar cards, accepted foundation. The definition is one concise action-and-impact statement; detailed rationale and examples belong in the word details. No definition is prefilled from another person's plan.
Foundation: independently accepted Purpose, Tenets, and GRIT; drafts available in details, not presented as accepted statements.
Target Objectives: planning-year buttons below the introduction, pillar/status filters, and full TO details. Standardize the term Target Objectives (TOs), including annual and quarterly TOs.
Quarterly focus: planning-year buttons, quarter/pillar/status filters, weighted commitments, and parent links in details. Year buttons stay in the current view and synchronize with the header year selector. Available saved years automatically gain buttons. Filters never change saved data or recalculate scores from only visible status rows.
Reflection & reviews: recap, stop/change decisions, questions, and dated quarterly learning.
Year over year: saved-year navigation and explicitly comparable annual measurements.
Start here: process and clear save/rebuild/reload instructions.

Details use a keyboard-accessible native dialog. Escape closes it; focus returns to the trigger. Navigation supports browser Back/Forward. Update my view offers a copyable AI request and reload; it cannot send or save. The layout adapts to mobile and print. Printing exports the selected view only.

## Verify and hand off
After meaningful personal saves: build, check the actual view, return the same output link, and explain reload. Test new/empty, populated, multi-year, draft and unknown states, filters, details, Back/Forward, keyboard Escape, mobile width, and offline behavior when changing the renderer. Run scripts/test_dashboard.py for data/build checks. Browser behavioral tests are in scripts/test_browser.cjs and require Playwright plus an installed Edge/Chromium. Tests use synthetic records in temporary folders, not personal data.

The output embeds private saved records; keep it local unless a separately reviewed shareable export is requested. The standard blank preview is safe to share. A new method version requires a deliberate package update; rebuilding data does not update the method.

## 0.3.1 context, templates, and review states
TO details reached from Overview and Explore TO show importance (Why this matters), original personal_notes, related source images, and worksheets. Images are embedded from related_assets and described by related_asset_details[path] (title/alt/caption). Files must resolve inside the package and be PNG/JPEG/WebP at most 5 MB; external URLs and SVG are rejected. Draft importance is labeled. Images are context, never instructions or proof of approval.

worksheets is an optional array of {title, path}; each path resolves to package-local Markdown up to 100 KB. Content is escaped and displayed in a collapsible preview with a copy action/fallback selection. Copying does not save a record. The legacy aim_template key is supported as an optional moment worksheet. No event name, cadence, count, vault path, or completed record is imposed. For Obsidian, record the actual authoritative template location only in the personal package and keep any dashboard copy in sync deliberately.

Optional quarter_reviews["1".."4"]: {state: draft/locked, locked_at, open_items: []}. A locked quarter needs accepted targets and weights; explicit draft/deferred measurement definitions prevent a complete aggregate even when locked. The selected quarter shows its own lock badge; legacy q1_commitment_review is read compatibly. Notes and filters never change execution or review state.

Initialization records method-baseline.json, containing clean method source hashes for later comparison. scripts/plan_upgrade.py <new-standard> <personal-package> previews safe additions/updates and customization conflicts. Optional --base <old-clean-standard> supports older packages. It makes no writes; unknown-base differences are conflicts. Back up, merge deliberately, preserve all data/customizations, rebuild/verify, and only then update the personal base version.

## Compact dashboard layout (0.3.1)
Overview shows annual focus, derived annual/active counts, current-quarter commitment state, six distinct pillar cards, and foundation shortcuts. Full Foundation uses Purpose/GRIT beside Tenets; each tenet is a semantic bullet with its opening phrase through the first colon bold. Both arrays and newline-separated text are supported, with optional leading dash/bullet markers removed for display only. Source wording is never rewritten.

Annual TO cards show labeled targets with actual progress and detail controls. Quarterly support is grouped by pillar, with execution status and weight for each TO. Allocation and weighted progress use the full selected-quarter group; status filters narrow displayed TOs only. Retain explicit open tracking items, unknown progress, independent lock state and the aggregate acceptance rules. Full definitions, dated actuals, context and worksheets remain in TO details. The planning checkpoint remains available in Reflection & reviews.

Use the shared palette by default and accepted brand tokens when supplied. Favor a compact desktop layout with readable full wording, natural mobile stacking, keyboard-accessible controls and native details/summary disclosure. Longer content, larger text or zoom may require scrolling; never clip content or shrink it to force a one-page fit. Test with synthetic data only. Keep private fonts, names, images, plan content, worksheets and vault locators out of the standard.

---
name: personal-strategic-plan
description: Guide annual personal strategic planning, reflection, and quarterly Target Objective reviews across God, Fit, Fam, Biz, finances, and personal development. Maintain a private planning knowledge base and optionally reuse an existing Personal Brand System. Does not manage project tasks.
---
# Personal Strategic Plan
Standard version: 0.3.0

Help a person decide what winning looks like and choose the most effective route to it. Support a quick planning session or deeper reflection across sessions. Annual Target Objectives (TOs) may finish early.

## Standard and personal packages
This folder is the shareable method. Keep it free of real identities, personal records, private paths, brand assets, and source material. For personal work, create or resume a separate package outside the standard. Use `python scripts/init_plan.py <new-destination> --name <name> --initials <initials> --year <year>` to copy the method, initialize blank knowledge and plan.json, and build the HTML view. Never overwrite an existing package during initialization. See [maintenance](references/maintenance.md) for ownership, history, and method updates.

## Start and resume
Identify the planning year, person, requested mode, and any existing personal package from available context. Read that package's KB and last checkpoint before asking questions. Briefly explain the next useful output; ask one easy question. No mandatory preparation, PBS installation, upload, or branding exercise.
Confirm the year being planned at kickoff; show that year on Overview and in the Target Objectives (TOs) and Quarterly Focus year filters. Use the term pillars for God, Fit, Fam, Biz, $, and Up. Use Target Objectives (TOs) consistently rather than Annual Objectives as a tab label.

- Annual planning: use [process](references/process.md) for definitions, inputs, creation instructions, and outputs.
- TO creation, updates, or quarterly review: use [TO definitions](references/target-objectives.md) and [tracking/readiness](references/tracking-and-readiness.md). Draft from the recap one pillar at a time; distinguish annual outcomes from supporting practices and confirm ambiguous scope before calculating targets.
- Existing Personal Brand System or brand materials: use [PBS integration](references/pbs-integration.md). Read only relevant records for the identified person; do not scan other people's packages.
- Saving, comparing years, rendering an HTML view, or updating the method: use [maintenance](references/maintenance.md). Preview method updates with scripts/plan_upgrade.py; do not overwrite personal/customized files.
- Dashboard initialization, data format, brand settings, and rebuild: use [dashboard](references/dashboard.md). Offer the real offline HTML file at initialization; it does not gate the interview.

## Guided conversation
Ask 1–3 material questions at a time, normally one. Reuse answered questions and accepted material. Draft early, review, then deepen where useful. After three exchanges on a topic, summarize and offer a draft, another topic, or a bounded deeper exploration. Accept rough notes and optional inputs; preserve the person's words. Distinguish facts, aspirations, interpretations, and unknowns. Do not invent beliefs, baselines, accepted wording, or results.

Review Purpose, Tenets, and GRIT annually without automatically rewriting them. Select an action-oriented Word of the Year and exactly one core annual TO per pillar. Quarterly support is optional; when used, normally create 1–3 supporting TOs per pillar. Default to committing one quarter at a time; allow provisional future quarters when preferred. Do not store project task lists or manage projects here.

After choosing the annual focus word, help the person create and accept a hyper-focused personal definition: one short action-and-impact statement, without a list of pillars. Store the exact accepted definition in `word.meaning` and display it beneath the word. Follow the Word of the Year instructions in [process](references/process.md); do not infer definition approval from word selection.

Respect requests to move on and park unresolved questions. After selecting targets, settle necessary counting definitions one at a time. Accept explicit user data boundaries, including reported changes without underlying private balances. Separate accepted targets/weights/definitions, quarter locking, execution activation, and actual progress. Early activation never silently changes measurement windows. End with a readiness summary of accepted, active, pending, and deferred items; avoid repeatedly probing settled or deferred topics.

## Save and deliver
Save only in the personal package: reviewed decisions, dated measurements, source/version references, unresolved questions, and one next action. Preserve drafts and prior accepted versions distinctly. No personal planning session writes to the standard or automatically edits PBS. Do not schedule reviews or publish anything without the relevant user request.

After meaningful saves, run `python scripts/build_dashboard.py <personal-package>/plan.json`, verify the result, and return the stable HTML link with reload instructions. plan.json owns structured planning data; knowledge.md owns narrative evidence. Provide real links to files created. An HTML view is derived from saved knowledge, not a second editable database. Do not claim installation, dashboard rendering, review, or persistence that has not occurred. If file access is unavailable, return exact proposed records and identify them as unsaved.

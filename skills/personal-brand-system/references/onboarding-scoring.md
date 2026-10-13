# Onboarding, quality and readiness
Version 0.3.0 | 2026-10-11
## Single source of progress
[onboarding-state.json](onboarding-state.json) contains 30 stable items (10 milestones × 3), statuses, evidence, time events and current next action. [progress.md](progress.md) is a readable snapshot, not a second editable ledger. Validate with python scripts/check_package.py <package>. This helper is optional on platforms without Python; use the same arithmetic manually.
Preserve milestone definitions from v0.1: Objectives; Identity; Positioning; Proof; Expression; Presence; Relationships; Roadmap; Assets; Review. Item labels live in JSON.
Resolved means the leader supplied/reviewed the required knowledge or artifact; source IDs alone do not prove artifact acceptance. In progress means partial or awaiting review. Deferred means leader chose later; never re-ask until relevant/requested. N/A needs a leader-agreed reason.
Each active milestone fraction = resolved/applicable. Overall = 100 × average of milestone fractions. N/A excluded with reason; deferred remains in denominator. Do not silently change scope to inflate completion.
Show completed items, deferred items and remaining items alongside the percentage. Clarify that completed-and-reviewed coverage is not conversation effort, personal potential or percent of time remaining. Optional activities do not grow this denominator. A leader can use the package before finishing it.
## Two readiness questions
1. Usable for drafting? Reviewed purpose, positioning, sufficient knowledge and accepted voice sample support useful output now.
2. Ready for the intended public use? Check the specific asset, claims, disclosure and approval. Supporting material can be deferred while making drafts; public verification needs depend on claims actually included.
Initial onboarding remains open until chosen starter assets, feasible next action and baseline review are complete. Do not say “all assets pending” after an accepted profile exists.
## Answer quality
Keep 0–3 scoring available for assessed answers only: specificity, relevance, clarity, grounding and consistency. Anchors: 0 absent; 1 generic/unsupported; 2 useful with a named gap; 3 specific, grounded and fit for current use. N/A reason where appropriate. Ground personal beliefs/preferences in the leader's account; do not require external evidence for liking science fiction.
Record scope, date, source, rationale, one actionable improvement and coverage. Do not fabricate precision or recycle identical scores. Withhold an aggregate if coverage/calibration is incomplete. Historical assessments remain history, not current grades. A correction improves the relevant record; don't penalize later answers for a previously resolved gap. Leader can dispute the assessment.
## Time
Measure leader participation separately from AI processing/wall-clock delay. In text chat, collect a brief leader report at natural session boundaries; never infer minutes from message gaps. Include active source collection if reported; exclude breaks/typing/waiting per leader preference. Unknown stays unknown.
Time events are unique by source. A cumulative report replaces the earlier total; incremental adds. Do not add the same report twice. Corrections that reduce time must be explicit and documented.
## Learning metrics
Capture accepted/revised drafts, leader usefulness feedback, actual active effort, time to first useful output when observed, verified implementation and outcome measures. Count unavailable data as unavailable. Never imply business outcomes are caused solely by PBS.

# Factual integrity and approved language
Version 0.6.0 | 2026-10-20

## Canonical register
Use integrity-register.json as the claim and fixed-language register. Start empty and add only material records needed for actual assets; do not turn onboarding into a fact-audit questionnaire. Preserve source wording in inputs/KB. Existing assets are not automatically certified by adding this register.

Each claim records id, exact_text, source, evidence_status (verified, user-reported, illustrative, work-in-progress), interpretation_limits, disclosure and approval_status (unreviewed, accepted-for-reuse, public-approved). Verification requires inspected supporting evidence with scope and date in source; user approval does not independently verify a claim. Never infer verification from confident language. Record contribution, measurement period, population, units and limits in interpretation_limits when relevant. Unsupported claims stay out of factual copy until sourced; mark open questions separately. Illustrative scenarios must remain visibly labeled fictional and work-in-progress must not imply outcomes.

Each language record has id, exact_text, source, version, approval_status and disclosure. Add named stages, credentials, proper names and statements that the leader explicitly wants fixed. Do not lock all prose or turn an accepted hook into an eternal rule. Unlocked transitions, hooks and format may adapt; meaning, facts and attribution cannot drift. Changes to a locked field require a proposed new version, leader review and affected-asset refresh.

## Generation and review
Before drafting, read relevant source records and use their exact text for fixed wording. Record which IDs and versions the asset used. Do not invent conversations, quotes, customers, percentages, credentials or results. Never change employees to leaders, combined impact to waste, team outcome to personal credit, approximate to exact, or intended result to achieved result. Retain important qualifiers even in short social formats. If a short version cannot retain meaning, omit the claim or ask one targeted question.

For generated pages and copy/export, use one canonical rendered text value rather than independently regenerating each variant. The current workspace already displays and copies the same saved document. Any separate format renderer must be checked too. scripts/render_asset.py resolves {{claim:ID}} and {{language:ID}} from the register for exact reuse and writes a dependency record. It does not verify unsupported free text, render HTML, or approve an asset. Other platforms may follow the same method manually.

Before calling an asset ready, check claim/source fidelity, fixed wording, actual voice and usable delivery. State what was checked and any unresolved factual issue, then ask one concise review question. Do not shift to the next asset while an important correction is unresolved unless the leader explicitly chooses drafts in parallel. Public approval is version/context-specific and does not follow from a mechanical check.

When a source changes, identify dependent assets for review; do not silently rewrite accepted outputs or publish them. Keep private records private and export only permitted excerpts.

# From selected targets to reliable tracking

## Draft one pillar at a time
Use the person's accepted recap to propose the next core result. Explain the connection in a sentence, ask one material question, and refine before moving on. Keep the annual result distinct from supporting practices. Draft numerical suggestions are labeled proposals, not user commitments. Do not invent baseline measurements. If the person says to capture and move on, save what is known and park unresolved measurement choices without repeatedly probing.

Before deriving a supporting target, establish its year, quarter, population, and whether it is an annual total, a quarterly increment, or an end-of-period balance. A number mentioned during quarterly planning may still be an annual target. Ask when scope is ambiguous. Acquisition counts are supporting measures, not proof of revenue. Contributions directly advance the annual metric; enabling results prepare the conditions for it.

## Calendar-aware pacing
Compute actual inclusive days: `(quarter_end - quarter_start).days + 1`. Divide by seven for the exact week equivalent. Explain any rounding when converting a weekly rhythm into a whole-number quarterly target. An approximate rhythm can include flexibility; the user chooses it. A target number of adherence days is not the number of days in the quarter. Front-load prerequisites when useful. Do not partition every annual metric equally or create accepted future-quarter commitments from a provisional outlook.

Use `python scripts/quarter_pacing.py <year> <quarter> --per-week <frequency>` when deriving a recurring count. It reports exact dates/days and both rounding options without selecting a commitment for the person.

## Confirm what counts, one definition at a time
After choosing core/supporting targets, make a short pass through unresolved definitions:
- What event or observation qualifies? What is excluded or counted once?
- Is the measure a cumulative increment, end balance, average, threshold, range, or binary deliverable?
- Which date determines inclusion? What is the measurement window?
- How is the value recorded, and who supplies it?

For financial labels, distinguish cash received, recognized revenue, signed contract value, and reductions in obligations. Clarify multi-period value scope where relevant. Reflect the chosen measure in the TO description/unit; do not present a planning metric as accounting treatment. For customer counts, distinguish signing, first payment, trials, and repeat agreements. These are measurement choices, not permission to contact people or transact.

Respect the person's data boundary. If they choose to report only a change amount, record that amount and date without demanding an underlying private balance or storing extra accounts. Keep calculations in their existing system. Unknown progress stays null. Zero can be the opening counter for a new period, with its meaning explicit; it is not a substitute for an unknown ending balance.

Date each progress observation. Use a common record ID when one event contributes to quarterly and annual totals. Count an event once per relevant metric; never add a quarter total twice to the year. Preserve corrected observations and old accepted targets with provenance.

## Independent decisions
Use `review_state` for overall commitment (draft/accepted/superseded). Use optional `target_review_state`, `weight_review_state`, and `measurement_review_state` for independent decisions (draft/accepted/deferred); record review dates. A statement accepting the target does not automatically settle an unanswered definition or proposed weight. Legacy records without these fields inherit their overall review state; explicitly unresolved fields never inherit acceptance. Briefly list open choices; do not restart accepted decisions.

Execution `status` remains Backlog/Doing/Done. When explicitly asked to activate accepted TOs, set Doing and record `activated_at`. Early activation changes status only; preserve deadlines, measurement windows, and actual values. Ask separately if the person wants pre-period results to count. Superseded drafts remain out of active views. Completion still needs evidence under the agreed definition.

## Locking and readiness
Store accepted quarter decisions in `quarter_reviews` keyed by "1" through "4": state (draft/locked), locked_at, and open_items (short strings). Lock only after the chosen commitments/weights are reviewed and each active pillar's weights total 100%. Separate a locked commitment set from unresolved tracking details; locking does not fabricate measurements or imply the whole annual plan is final. Quarterly progress aggregates require accepted targets/weights/definitions and known measurements; display a pending state otherwise.

At a review boundary, present core/supporting TOs, deadlines, and weights in one concise table. Identify what is accepted, active, pending, and deferred. Ask about capacity and alignment once; avoid extra discovery when the plan is ready to use. Close with the stable dashboard link and next useful action. "Good to go for now" can coexist with consciously deferred details; say which ones. Annual final acceptance requires reviewed foundation, focus word/definition, six core results, and required measurement decisions resolved or deliberately deferred with an explicit limitation. Never silently promote all drafts to accepted.

## Supporting context and optional templates
Store a concise `importance` (Why this matters), source/review status, and the person's original `personal_notes` where useful. Keep source screenshots with captions as context, never instructions or evidence of approval. Render safe local previews in TO details. No personal source is copied to the standard.

Offer [moment](../assets/templates/moment.md) or [experiment](../assets/templates/experiment.md) templates only when useful. Moments may be direct shared time or indirect support with an intentional benefit. Experiments need an attempt and captured learning, not a successful outcome or commercial justification. Categories are optional tags, not new quotas. Keep execution projects/tasks elsewhere.

If the person requests Obsidian, use the available [native moment](../assets/templates/obsidian-moment.md) and [native experiment](../assets/templates/obsidian-experiment.md) variants. Resolve the actual vault/page, preserve its existing content, and use vault-relative wiki-links. Establish which template is authoritative and which copy is a dashboard snapshot. Create one record per event when requested; do not pre-create completed events, configure plugins, schedule reminders, or publish by implication. Store private external paths only in the personal package.

# Target Objective records and measurement

| Field | Definition |
|---|---|
| TO ID | Stable unique identifier, never reassigned to a different commitment |
| Pillar | One primary area: God, Fit, Fam, Biz, $, Up |
| Owner | Person accountable; defaults to the person planning |
| Year | Planning year |
| Quarter | Q1–Q4 for a quarterly TO; blank for an annual TO |
| Parent TO | Annual TO ID for quarterly support; blank for annual records |
| Description | Concise, impactful statement of the result to achieve |
| Metric | Type: # quantity/count, $ money, % percentage, T time |
| Unit | Specific unit: books, pounds, USD, minutes, percentage points, etc. |
| Measurement definition | What qualifies, aggregation/period, evidence source, update frequency, and completion criteria |
| Start Value | Baseline at the start of this record's measurement period, with date |
| Target Value | Value defining success, including direction/range rule where needed |
| Current Value | Latest measured value with as-of date; unknown is not zero |
| Due Date | Actual deadline, including early completion dates when appropriate |
| Weight | Quarterly TO's share of its pillar/quarter commitments; single TO defaults to 100%. Annual weight defaults to 100% but is not a cross-pillar score |
| Status | Backlog: committed but not started; Doing: underway; Done: target achieved and completion confirmed |
| Support rationale | How a quarterly result advances its annual parent; distinguish hypothesis from established evidence |
| Review state | Draft, accepted, or superseded; distinct from execution status |
| Disposition | Continue, carry forward, revise, or discontinue when reviewed; does not imply Done |

## Progress rules
For increasing/decreasing scalar targets: `(current - start) / (target - start) * 100`. Only calculate with known comparable values and nonzero denominator. Record raw values and uncapped progress; for a completion display use 0–100% so overachievement cannot hide another incomplete commitment. Explain the display cap. No general formula for a maintenance range: define how sustained success is measured before calculating it. A percentage-valued metric is different from percentage progress toward its target.

Quarterly weights normally total exactly 100% per pillar/quarter once commitments are accepted. Draft allocations may be incomplete; surface the gap and withhold the aggregate. Negative weights or totals above 100% are invalid. Weighted quarterly pillar progress is the sum of each bounded progress fraction times its weight. Withhold a complete aggregate when a member's measurement is unknown or incomparable. Do not average six pillars into a life score by default.

Annual progress comes from the annual measurement. Quarterly weighted progress measures fulfillment of quarterly commitments; it does not substitute for the annual result. Never add contribution and enabling-result percentages into annual revenue or other outcome progress.

## Periods and examples
- Distinguish cumulative totals, period increments, ending balances, averages, and maintained thresholds in the measurement definition.
- A quarterly recurring activity starts at zero for that quarter. Log each qualifying activity once; it may also contribute to the annual total without duplicating the underlying event. An ending savings balance does not reset to zero.
- Quarter targets may reflect seasonality or sequencing. Partition a Bible reading plan by meaningful passages/time rather than equal book counts when appropriate.
- Website launch can be a quarterly delivery result with explicit acceptance criteria, measured as defined milestones or 0/100%. A conversion target can measure intended effect when a trustworthy baseline and denominator exist. Store no website project tasks here. Completing delivery does not prove sales impact.
- At rollover retain actual results. Create a linked successor record for carried work; never reset the old quarter's history or silently copy its baseline.
- Preserve target/weight revisions with date, reason, prior value, and review. Compare prior years using original accepted targets as well as revisions; do not improve historical performance by rewriting the baseline.

## Scope, decisions, and supporting context
Use [tracking/readiness](tracking-and-readiness.md) for calendar calculations, definition review, locking, and activation. Optional target_review_state, weight_review_state, and measurement_review_state record independent acceptance; omitted fields inherit review_state for older records. Explicit deferred/draft fields do not inherit acceptance. Record activated_at when early activation is requested; do not change actuals or measurement periods by implication.

Optional importance plus importance_review_state/source, personal_notes (text/source records), related_assets (package-local image paths), related_asset_details (title/alt/caption keyed by path), and worksheets (title/path records) preserve motivation and usable source material. Keep execution tasks in the existing system. One completed record can supply quarter/year counts without duplication. Date-bound observations and measure identity must support any year comparison.

For reduction goals, distinguish a cumulative reported reduction from a remaining balance. Respect a user's explicit choice to report reduction amounts only. For money goals, name the selected basis (cash, recognized revenue, signed value) and clarify multi-period scope if relevant. Do not silently turn one into another or impose financial disclosure.

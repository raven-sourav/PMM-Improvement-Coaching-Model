# Observe — Review Execution Logger

## Trigger
Run **after every review, pattern analysis, report generation, or dashboard update**.

## Purpose
Track how the review system performs over time. The Master-reviewer already has feedback retention tracking (the 3x flag), but observations are needed to detect when the *review system itself* needs improvement — not just the PMMs being reviewed.

## Process

### Step 1 — Capture execution context
After a workflow completes, record:
- **workflow**: Which workflow ran (review, patterns, campaign-view, report, improvement-track, refresh, dashboard)
- **timestamp**: ISO date (YYYY-MM-DD)
- **pmm**: Which PMM was involved (if applicable)
- **outcome**: `success` | `partial` | `failure`

### Step 2 — Capture quality signals
For reviews:
- Which dimensions were hardest to score? (ambiguous evidence, borderline scores)
- Did any dimension score feel miscalibrated? (too harsh or too lenient compared to actual quality)
- Was the Focus 3 selection obvious or difficult?
- Were rewrite examples specific and actionable, or generic?
- Did the document type applicability matrix correctly include/exclude contextual dimensions?
- Feedback retention check result (iteration 2+): was prior feedback applied?

For pattern analysis:
- Were there enough data points to identify real patterns vs. noise?
- Did the persistent feedback gap flag (3x without improvement) trigger?
- If it triggered: was the issue with the PMM or with how feedback was framed?

For reports:
- Did the report accurately reflect the underlying data?
- Were growth trajectories meaningful or noisy?

### Step 3 — Write observation log
```markdown
---
workflow: {workflow_name}
timestamp: {YYYY-MM-DD}
pmm: {email_if_applicable}
outcome: {success|partial|failure}
---

## Task
{One-line summary}

## Result
{What happened — 2-3 sentences}

## Quality Signals
- Difficult dimensions: {list}
- Calibration concerns: {dimension}: scored {x}, felt like {y}
- Focus 3 clarity: {clear|ambiguous}
- Rewrite quality: {specific|generic}
- Feedback retention: {applied|not_applied|N/A}

## System Drift Indicators
{Signs that the review system itself needs updating}
- Scoring rubric unclear for certain document types?
- Dimension definitions ambiguous?
- Focus 3 selection criteria need refinement?
- New document types not covered by applicability matrix?
- Feedback framing patterns that consistently fail retention?
```

**File naming**: `_logs/{workflow}-{pmm_shortname}-{YYYY-MM-DD}-{seq}.md`

### Step 4 — Flag critical observations
If outcome is `failure`, or a calibration concern is detected, or a feedback framing pattern fails retention 3+ times, append to `_logs/_flags.md`:
```
- [{timestamp}] {workflow}: {one-line description}
```

## Primary Metric
**Feedback retention rate** — % of coaching feedback items applied by PMMs in subsequent iterations.

This is the single number that tells us if the review system is producing actionable feedback. Track it in each observation log's frontmatter:
```
retention_rate: {N%|N/A}
```

When this rate drops below **60%** across 5+ iteration-2+ reviews, the feedback framing or rubric needs inspection.

## Auto-Learn Gate
Before logging an observation, it must pass ALL 4 criteria:
1. **Genuine discovery** — not just a routine review or expected pattern
2. **Durable value** — will this signal still matter in 6 months?
3. **Verified signal** — the quality concern is confirmed, not just a feeling
4. **Clear trigger** — you can describe exactly what condition caused it

If any criterion fails, skip the log. This prevents observation noise.

## Rules
- Distinguish between PMM performance issues (not our concern here) and system/skill performance issues (our concern)
- Keep observations factual
- Never modify scoring rubric or templates from this workflow
- One log file per workflow execution
- Apply the Auto-Learn Gate — do not log routine reviews without actionable system signals

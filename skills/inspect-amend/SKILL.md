# Inspect & Amend — Self-Improving Review System

## Trigger
- "Inspect review system", "Check scoring health", "Review system performance"
- "Amend scoring", "Improve rubric"
- Automatically suggested when `_logs/_flags.md` has 3+ entries for the same dimension or workflow

## Purpose
Close the self-improvement loop for the review system itself. When coaching feedback is consistently ignored, the issue might not be with the PMM — it might be with how the feedback is framed. When scoring feels miscalibrated, the rubric descriptions might need sharpening.

## Process

### Phase 1 — Inspect
1. Read all observation logs from `_logs/`
2. Read `_logs/_flags.md` for flagged issues
3. Cross-reference with PMM profiles for feedback retention data
4. Identify patterns:
   - **Calibration drift**: Dimensions consistently scored too high or too low
   - **Rubric ambiguity**: Same dimension scored differently in similar contexts
   - **Feedback retention failures**: Specific feedback framings that PMMs never act on (the system's fault, not the PMM's)
   - **Focus 3 noise**: Priorities selected that don't drive real improvement
   - **Applicability gaps**: Document types triggering wrong contextual dimensions
   - **Rewrite generics**: Rewrite examples that are too vague to be actionable

4. Generate **Inspection Report**:
```markdown
## Inspection Report: {target — rubric|dimension|workflow}
**Date**: {YYYY-MM-DD}
**Observation window**: {date range}
**Reviews observed**: {N}

### Patterns Detected
1. {Pattern with evidence from logs and PMM profiles}

### Root Cause Analysis
- Is the issue in the scoring rubric?
- Is it in the feedback framing?
- Is it in the dimension definition?
- Is it in the applicability matrix?

### Recommendation
{Amend rubric | Reframe feedback pattern | Update applicability matrix | Monitor}
```

### Phase 2 — Amend
If inspection recommends amendment:

1. **Identify the target file**: `templates/scoring-rubric.md`, `templates/review-template.md`, `templates/pmm-profile.md`, or `CLAUDE.md`
2. **Propose a specific change**:
   - Sharpen a dimension's scoring band descriptions
   - Reframe a feedback pattern for better retention
   - Add/remove a dimension from a document type's applicability
   - Adjust Focus 3 selection criteria
   - Update rewrite example guidelines

3. **Version before changing**:
   - Create `_versions/` in project root if it doesn't exist
   - Copy the target file → `_versions/{filename}-v{N}.md`
   - Write to `_versions/_changelog.md`:
     ```
     ## v{N+1} — {YYYY-MM-DD}
     **Target**: {file changed}
     **Trigger**: {Pattern from inspection}
     **Change**: {What was changed}
     **Evidence**: {Supporting log entries + PMM retention data}
     **Expected improvement**: {What metric should improve}
     ```

4. **Present proposed diff to user** for approval before applying

### Phase 3 — Evaluate
After amendment:

1. Mark in `_logs/_flags.md`:
   ```
   - [EVAL] {target} v{N+1} applied {date} — monitoring
   ```

2. After 3-5 subsequent reviews using the amended rubric/template, compare:
   - Feedback retention rates before vs. after
   - Scoring consistency (less calibration concern flags)
   - Focus 3 follow-through rates
   - Rewrite specificity (observed quality)

3. Generate **Evaluation Report** with before/after comparison

4. If degraded: roll back from `_versions/`, log the rollback

## Amendment Thresholds
- **Trigger threshold**: Only propose amendment when feedback retention rate drops below **60%** across 5+ iteration-2+ reviews, OR when 3+ flags accumulate for the same dimension/workflow
- **Improvement bar**: An amendment must improve feedback retention by at least **15 percentage points** OR resolve a persistent feedback gap (3x flag)
- **Revert rule**: If an amended rubric/template doesn't improve retention within **5 subsequent reviews**, auto-revert. No exceptions.
- **Cooldown**: After a revert, wait for **3 reviews** before proposing a new amendment to the same component

## Rules
- Never amend without inspection evidence
- Never apply without user approval
- Always version before amending
- One amendment per cycle
- Evaluate before proposing next amendment
- Distinguish system issues from PMM performance issues
- The 29-dimension structure is foundational — amend descriptions and scoring bands, not the dimension list itself

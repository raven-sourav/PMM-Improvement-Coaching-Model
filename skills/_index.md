# Skill Index — Master Reviewer

## Data Flow

```
Documents (v1 + v2) → [review] → scored analysis (29 dims)
                           ↓
                     PMM profile update (pmms/{email}.md)
                           ↓
              [patterns] → strengths, weaknesses, growth areas
              [campaign-view] → iteration arc, feedback retention chain
              [reports] → individual / team / promotion / learning
              [improvement-tracking] → dimension goals with baselines
                           ↓
              [dashboard] → HTML visualization (heatmap, radar, cards)
                           ↓
              [refresh-patterns] → recompute everything from all reviews
```

## Workflows

| Workflow | Purpose | Depends On | Feeds Into |
|----------|---------|------------|------------|
| Register PMM | Create new PMM profile | templates/pmm-profile.md | All other workflows |
| Review | Score document iterations (29 dims) | scoring-rubric.md, review-template.md | PMM profile, patterns |
| Patterns | Show accumulated strengths/weaknesses | PMM profile (reviews/) | Reports |
| Campaign View | Show iteration arc for one campaign | reviews/ for PMM + campaign | Coaching decisions |
| Reports | Generate individual/team/promotion/learning | PMM profiles, reviews/ | Standalone output |
| Improvement Tracking | Set and track dimension goals | PMM profile | Review (checks progress) |
| Refresh Patterns | Recompute patterns from all reviews | All reviews/ for a PMM | PMM profile update |
| Dashboard | Generate visual HTML dashboard | All PMM profiles + reviews | dashboard/index.html |

## Meta-Layer (Self-Improving)

| Skill | Purpose | Watches |
|-------|---------|---------|
| `skills/observe/` | Log review system quality signals | All workflows above |
| `skills/inspect-amend/` | Propose amendments to rubric/templates | observe logs → templates/ |

**Primary metric**: Feedback retention rate (target: >60%)

## Templates (do not modify directly — amend through inspect-amend)

- `templates/scoring-rubric.md` — 29 dimensions, scoring bands, applicability matrix
- `templates/review-template.md` — Review output format with Focus 3
- `templates/pmm-profile.md` — PMM profile structure with campaign history

# PMM Improvement & Coaching Model

> A self-improving coaching system that scores PMM work across 29 dimensions, tracks growth across campaigns, and fixes itself — built entirely with Claude Code and markdown.

**No APIs. No databases. No setup.** Clone → open with Claude Code → start reviewing.

[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blueviolet)](https://claude.ai/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Why This Exists

PMM feedback has three structural failures:

1. **Unscored** — "The positioning needs tightening" compared to what? No rubric, no baseline, no shared definition of quality.
2. **Untracked** — Every review is a clean slate. The same CTA note shows up across three campaigns and nobody notices.
3. **Unprioritized** — Eight comments, all weighted equally. The PMM fixes the easy ones and skips the rest.

The result: growth happens invisibly, and when promotion season arrives, the evidence is anecdotal.

This system fixes all three.

---

## Visual Dashboard

The system generates a self-contained HTML dashboard — no server, no dependencies. Open in any browser.

### Team Dashboard
> Team-level stats, progress cards per PMM with score rings, skill category breakdowns, and recent review activity.

📄 **[View Team Dashboard →](dashboard/index.html)** *(download and open in browser)*

### Product Brief
> A one-page overview of how the system works — dimensions, scoring, Focus 3, and tracking.

📄 **[View Product Brief →](brief.html)** *(download and open in browser)*

---

## What It Does

### 29 Dimensions Across 5 Categories

Every piece of PMM work is scored across component skills — not collapsed into "needs work."

| Category | Dimensions | What It Covers |
|----------|-----------|----------------|
| **A. Strategic Foundation** | 6 | Messaging clarity, value prop, audience targeting, competitive positioning, CTA effectiveness, evidence usage |
| **B. Copywriting Craft** | 10 | Headline strength, word economy, specificity, sentence rhythm, repetition, power language, vivid language, emotional resonance, opening/closing, readability |
| **C. Structure & Logic** | 4 | Information hierarchy, argument structure, transitions, scannability |
| **D. Persuasion & Conversion** | 5 | Social proof, benefit/feature ratio, objection handling, urgency/trust, technical simplification |
| **E. Brand & Voice** | 4 | Tone consistency, brand distinctiveness, confidence calibration, jargon appropriateness |

**17 Core** dimensions are always scored. **12 Contextual** dimensions activate based on document type.

Each scored **0–10** against a **4-band rubric** with specific criteria per band:

| Score | Band | Meaning |
|-------|------|---------|
| 0–3 | Needs Work | Fundamental gaps — missing or counterproductive |
| 4–6 | Developing | Elements present but inconsistent or generic |
| 7–8 | Proficient | Solid, effective, minor refinements needed |
| 9–10 | Exceptional | Best-in-class, could be used as a teaching example |

### Focus 3 — Built for Humans

29 dimensions are scored for tracking, but **every review surfaces only 3 priorities**:

- **2 Quick Wins** — 15–30 minute fixes (swap weak verbs, cut filler, add one proof point)
- **1 Deeper Work** — 1–2 hour investment that builds a real skill

Everything else is explicitly **parked** — named, scored, acknowledged, and set aside.

**Priority logic:**
- Strategy problems (Cat A) always fixed before craft problems (Cat B)
- High-impact, low-effort fixes come first
- If same feedback given 3x without improvement → flags the coaching method, not the PMM

### Rewrites, Not Advice

Every feedback note includes a concrete rewrite using the PMM's own text:

```
Their line:    "Our solution helps companies improve their operations."
Could become:  "Ramp cut pipeline incidents by 73% in 90 days."
Why it works:  Replaces vague benefit with a specific customer outcome and timeframe.
```

### Multi-Iteration Campaign Tracking

```
Campaign: "q3-launch-messaging"

Draft 1 → Draft 2     (Iteration 1 — after manager feedback)
          Draft 2 → Draft 3     (Iteration 2 — after peer review)
                     Draft 3 → Final    (Iteration 3 — final polish)
```

Each iteration scored independently. The system runs a **feedback retention check** — did coaching from iteration N show up in iteration N+1? (Yes / Partial / No, with evidence.)

### Cross-Campaign Growth Tracking

Over months and multiple campaigns, the system tracks:

- **Draft quality progression** — are first-draft scores improving? (the real signal of internalized learning)
- **Feedback retention rates** — percentage of coaching that sticks
- **Dimension trajectories** — which skills trending up, flat, or regressing
- **Persistent gap flags** — same feedback 3x without improvement triggers a coaching method review

### Reporting Suite

| Report | What It Shows |
|--------|---------------|
| **Individual** | Score trends, category analysis, patterns, active improvement tracks |
| **Promotion** | Growth trajectory, draft quality progression, feedback retention — quantified evidence for appraisals |
| **Learning** | Whether feedback is being internalized vs. applied reactively |
| **Team** | Dimension heatmap, team-wide gaps, standouts for peer mentoring |
| **Comparison** | Side-by-side dimension scores for any two PMMs |

### Self-Improving System

The system watches itself and adapts:

1. **Observe** — After every review, logs quality signals (rubric ambiguity, scoring miscalibration, generic rewrites, unclear Focus 3 selection)
2. **Inspect** — When 3+ observations flag the same issue, analyzes the pattern
3. **Amend** — Proposes targeted changes to the rubric, feedback framing, or applicability matrix
4. **Version** — All amendments versioned in `_versions/` — nothing permanently lost

**Primary metric:** Feedback retention rate (target >60%). If PMMs aren't retaining coaching, the system assumes the problem is its own approach.

---

## Supported Document Types

| Type | Key | Typical Contextual Dimensions |
|------|-----|-------------------------------|
| Messaging Document | `messaging_doc` | Competitive Positioning, Scannability |
| Positioning Brief | `positioning` | Competitive Positioning, Evidence |
| Marketing Copy | `copy` | Headline & Hook, Sensory Language, Emotional Resonance, Opening & Closing |
| Launch Brief | `launch_brief` | CTA, Social Proof, Urgency & Trust |
| Blog Post | `blog` | Headline & Hook, Emotional Resonance, Opening & Closing, Readability |
| Case Study | `case_study` | Social Proof, Evidence, Technical Simplification |
| Email | `email` | Headline & Hook, CTA, Urgency & Trust |
| Landing Page | `landing_page` | All contextual dimensions typically apply |

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/raven-sourav/PMM-Improvement-Coaching-Model.git
cd PMM-Improvement-Coaching-Model

# 2. Open with Claude Code
claude

# 3. Register a PMM
> Add a PMM: Sarah Chen, sarah@company.com, team "Growth Marketing"

# 4. Submit a review
> Review these docs for Sarah. Campaign: q3-launch-messaging, type: messaging_doc
> Here's Draft 1: [paste or file path]
> And here's Draft 2: [paste or file path]

# 5. Continue iterating
> Now review iteration 2 of the same campaign for Sarah

# 6. Track progress
> Show patterns for Sarah
> Promotion report for Sarah
> Team report

# 7. Generate dashboard
> Generate dashboard
```

## All Workflows

| Command | What Happens |
|---------|--------------|
| `Add a PMM` | Registers a PMM with name, email, team |
| `Review these docs for [PMM]` | Scores across 29 dimensions, saves review, updates profile |
| `Show campaign [id] for [PMM]` | Full iteration arc with feedback retention chain |
| `Show patterns for [PMM]` | Strengths, weaknesses, growth areas, draft-stage strengths |
| `Set a goal for [PMM]` | Creates an improvement track with baseline and target |
| `Report on [PMM]` | Full coaching report with score trends |
| `Promotion report for [PMM]` | Quantified growth portfolio for appraisals |
| `Learning report for [PMM]` | Feedback internalization analysis |
| `Team report` | Cross-PMM dimension heatmap, gaps, standouts |
| `Compare [PMM1] and [PMM2]` | Side-by-side dimension comparison |
| `Refresh patterns for [PMM]` | Recompute all patterns from review history |
| `Generate dashboard` | Builds visual HTML dashboard from all data |

---

## Project Structure

```
├── CLAUDE.md                 ← Agent instructions (the brain)
├── templates/
│   ├── scoring-rubric.md     ← 29 dimensions with 4-band rubrics + applicability matrix
│   ├── review-template.md    ← Review output format with feedback retention check
│   └── pmm-profile.md        ← Profile structure with campaign tracking
├── dashboard/
│   ├── generate.py           ← Parses markdown, generates standalone HTML
│   └── index.html            ← Generated dashboard (open in browser)
├── skills/
│   ├── observe/SKILL.md      ← Execution logging (self-improving)
│   ├── inspect-amend/SKILL.md← System amendment loop
│   ├── git-pushing/          ← Git commit & push automation
│   └── _index.md             ← Skill data flow diagram
├── pmms/                     ← PMM profiles (one per person)
├── reviews/                  ← Individual review analyses
├── reports/                  ← Generated reports
├── brief.html                ← Product brief (visual overview)
└── test-docs/                ← Sample draft & final for testing
```

## Customization

- **Adjust rubrics** — Edit `templates/scoring-rubric.md` to match your team's standards
- **Add dimensions** — Add new sections to the rubric and update `CLAUDE.md`
- **Change applicability** — Modify the applicability matrix for your document types
- **Add doc types** — Extend the matrix for new document formats
- **Adjust scoring weights** — Modify overall score calculation if some categories matter more

---

## Built With

- [Claude Code](https://claude.ai/claude-code) — AI agent that powers the entire review, tracking, and reporting system
- Markdown — All data lives in readable, editable text files
- Python — Dashboard generation only (standalone HTML output, no server)

## License

MIT

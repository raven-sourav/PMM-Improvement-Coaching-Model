# Master Reviewer

An AI-powered coaching tool for Product Marketing Managers. Clone this repo, open it with [Claude Code](https://claude.ai/claude-code), and start reviewing PMM work objectively.

**No APIs. No setup. No dependencies.** Just Claude Code + markdown files.

---

## The Problem

Managers review PMM work constantly — messaging docs, launch briefs, blog posts, case studies. But feedback is inconsistent, subjective, and hard to track over time. Did the PMM actually improve? Which skills are stuck? Is coaching working? Come appraisal season, the evidence is anecdotal.

Master Reviewer fixes this by scoring every document iteration across 29 dimensions, tracking whether feedback gets applied, and measuring growth across campaigns over months.

## What It Does

- **Scores document iterations** across **29 dimensions in 5 categories** — from strategic positioning to sentence-level copywriting craft
- **Surfaces only 3 priorities per review** (the "Focus 3") — ranked by effort vs. impact, because humans can't absorb 29 things at once
- **Shows exactly what better looks like** — every feedback note rewrites the PMM's own text, not abstract advice
- **Tracks campaigns end-to-end** — multiple iterations within a project (Draft 1→2→3→Final)
- **Measures feedback retention** — did the PMM actually address the coaching notes from last iteration?
- **Tracks cross-campaign growth** — are initial draft scores improving over time? (the real signal of internalized learning)
- **Generates reports** for coaching, appraisals, and promotion cases

---

## How It Works

### The Review Process

1. **PMM submits two versions** of a document — the initial draft and the revised version
2. **Master Reviewer scores both** across all applicable dimensions (0–10 each)
3. **Computes an overall score** (0–100) and identifies the delta between versions
4. **Selects 3 priorities** using an effort/impact matrix — what to fix first, and what to park for later
5. **Writes concrete rewrites** using the PMM's own text for every dimension
6. **Updates the PMM profile** with scores, patterns, and campaign data

### Scoring Scale

| Score | Band | Meaning |
|-------|------|---------|
| 0–3 | Needs Work | Fundamental gaps — missing or counterproductive |
| 4–6 | Developing | Elements present but inconsistent or generic |
| 7–8 | Proficient | Solid, effective, minor refinements needed |
| 9–10 | Exceptional | Best-in-class, could be used as a teaching example |

**Overall score** = (sum of Version 2 scores / number of dimensions scored) × 10 → 0–100 scale.

The denominator varies per review because contextual dimensions are only scored when applicable to the document type.

---

## 29 Dimensions in 5 Categories

### A. Strategic Foundation (6 dimensions)
| Dimension | What It Measures | Type |
|-----------|-----------------|------|
| Messaging Clarity | Is the core message clear and repeatable? | Core |
| Value Proposition | Is the value differentiated and tied to customer pain? | Core |
| Audience Targeting | Is the language tailored to the specific persona? | Core |
| Competitive Positioning | Does it differentiate with evidence? | Contextual |
| CTA Effectiveness | Is the next step clear and compelling? | Contextual |
| Evidence & Proof Points | Are claims backed by data and proof? | Core |

### B. Copywriting Craft (10 dimensions) — *inspired by Gary Provost's "Write Music" principle*
| Dimension | What It Measures | Type |
|-----------|-----------------|------|
| Headline & Hook Quality | Does the opening grab and hold attention? | Contextual |
| Word Economy | Is the writing tight? Could it say the same in fewer words? | Core |
| Specificity vs. Vagueness | Concrete details or abstract generalities? | Core |
| Sentence Rhythm & Musicality | Does sentence length vary to create music? (Provost principle) | Core |
| Repetition & Parallel Structure | Is repetition intentional and rhetorical, or lazy? | Core |
| Power Language & Verb Strength | Strong active verbs or weak passive constructions? | Core |
| Sensory & Vivid Language | Does it paint pictures with concrete imagery and fresh analogies? | Contextual |
| Emotional Resonance | Does it connect with the reader's experience? | Contextual |
| Opening & Closing Craft | Does the opening create a loop the closing resolves? | Contextual |
| Readability | Is it easy to read for the target audience? | Core |

### C. Structure & Logic (4 dimensions)
| Dimension | What It Measures | Type |
|-----------|-----------------|------|
| Information Hierarchy | Is the most important info presented first? | Core |
| Argument Structure | Is there a clear claim → evidence → conclusion flow? | Core |
| Transition Quality | Do sections flow naturally into each other? | Core |
| Scannability | Can a reader skim and get the key points? | Contextual |

### D. Persuasion & Conversion (5 dimensions)
| Dimension | What It Measures | Type |
|-----------|-----------------|------|
| Social Proof | Are testimonials and case studies placed effectively? | Contextual |
| Benefit vs. Feature Ratio | Does it lead with outcomes, not capabilities? | Core |
| Objection Handling | Are likely concerns anticipated and addressed? | Contextual |
| Urgency & Trust Signals | Does it create appropriate urgency and build trust? | Contextual |
| Technical Simplification | Are complex ideas made accessible? | Contextual |

### E. Brand & Voice (4 dimensions)
| Dimension | What It Measures | Type |
|-----------|-----------------|------|
| Tone Consistency | Is the tone maintained throughout? | Core |
| Brand Voice Distinctiveness | Does it sound like this brand, or could it be anyone? | Core |
| Confidence Calibration | Neither overclaiming nor hedge-heavy? | Core |
| Jargon Appropriateness | Is vocabulary calibrated to the audience? | Contextual |

**17 Core** dimensions are always scored. **12 Contextual** dimensions are scored when applicable based on document type.

---

## Supported Document Types

| Type | Key | Typical Contextual Dims |
|------|-----|------------------------|
| Messaging Document | `messaging_doc` | Competitive Positioning, Scannability |
| Positioning Brief | `positioning` | Competitive Positioning, Evidence |
| Marketing Copy | `copy` | Headline & Hook, Sensory Language, Emotional Resonance, Opening & Closing |
| Launch Brief | `launch_brief` | CTA, Social Proof, Urgency & Trust |
| Blog Post | `blog` | Headline & Hook, Emotional Resonance, Opening & Closing, Readability |
| Case Study | `case_study` | Social Proof, Evidence, Technical Simplification |
| Email | `email` | Headline & Hook, CTA, Urgency & Trust |
| Landing Page | `landing_page` | All contextual dims typically apply |

The exact applicability matrix is in `templates/scoring-rubric.md` — you can customize it for your team.

---

## The Focus 3 — Built for Humans, Not Robots

29 dimensions are scored for tracking, but **every review surfaces only 3 priorities** — ranked by effort vs. impact:

- **2 Quick Wins**: Things the PMM can fix in 15–30 minutes (swap weak verbs, cut filler, add one proof point)
- **1 Medium/Deeper Lift**: A section-level improvement that moves the needle

Everything else is explicitly **"Parked for Later"** — giving the PMM permission to NOT worry about those dimensions yet.

### Priority logic

- Strategy problems (Category A) are always fixed before craft problems (Category B) — fix *what* you're saying before *how* you're saying it
- High-impact, low-effort fixes come first
- If the PMM has active improvement goals, at least 1 Focus 3 item aligns with them
- If the same feedback has been given 3 times without improvement, the system flags the coaching method, not the PMM

### Every feedback note includes a rewrite example

Master Reviewer doesn't just say "improve specificity" — it shows you exactly what better looks like using *your own text*:

```
Their line:    "Our solution helps companies improve their operations."
Could become:  "Ramp cut pipeline incidents by 73% in 90 days."
Why it works:  Replaces vague benefit with a specific customer outcome and timeframe.
```

This makes feedback immediately actionable — the PMM can see the technique applied to their own work.

---

## How Tracking Works

### Within a Campaign (Multiple Iterations)

A single project goes through multiple rounds of feedback:

```
Campaign: "q3-launch-messaging"

 Draft 1 → Draft 2     (Iteration 1 — after manager feedback)
           Draft 2 → Draft 3     (Iteration 2 — after peer review)
                      Draft 3 → Final    (Iteration 3 — after copy editing)
```

Each iteration is scored independently. The system tracks:
- **Score arc**: How the overall score improves across iterations
- **Feedback retention**: Did the PMM address the coaching notes from the prior iteration? (Yes / Partial / No for each item, with evidence)
- **Which dimensions plateau**: Some improve early, others need sustained effort

### Across Campaigns (Long-Term Growth)

Over months, a PMM works on multiple projects:

```
Campaign A (messaging doc)     Draft 1 avg: 3.2  → Final: 74/100
Campaign B (launch brief)      Draft 1 avg: 4.8  → Final: 81/100
Campaign C (blog post)         Draft 1 avg: 5.9  → Final: 86/100
```

The system tracks:
- **Draft quality progression**: Are initial drafts getting better? (This means feedback is being internalized, not just applied reactively)
- **Dimension trajectories**: Which dimensions are consistently improving in final work?
- **Persistent feedback gaps**: Coaching notes given repeatedly but never addressed
- **Draft-stage strengths**: Dimensions where even first drafts score 6+ (skill is internalized)

### Improvement Tracks

Managers set specific goals tied to dimensions:

```
Dimension: tone_consistency
Goal: "Develop distinctive brand voice"
Baseline: 4.0  |  Current: 6.5  |  Target: 8.0
Campaign Evidence: Campaign A: 6.0, Campaign B: 6.5
Status: Active
```

Progress updates automatically as new reviews come in.

---

## Quick Start

1. **Clone this repo**
   ```bash
   git clone https://github.com/yourusername/master-reviewer.git
   cd master-reviewer
   ```

2. **Open with Claude Code**
   ```bash
   claude
   ```

3. **Register a PMM**
   ```
   > Add a PMM: Sarah Chen, sarah@company.com, team "Growth Marketing"
   ```

4. **Submit a review**
   ```
   > Review these docs for Sarah. Campaign: q3-launch-messaging, type: messaging_doc
   > Here's Draft 1: [paste or file path]
   > And here's Draft 2 after manager feedback: [paste or file path]
   ```

5. **Continue iterating**
   ```
   > Now review iteration 2 of the same campaign for Sarah
   > Here's Draft 2: [paste] and Draft 3: [paste]
   ```

6. **Track progress**
   ```
   > Show campaign q3-launch-messaging for Sarah
   > Show patterns for Sarah
   > Promotion report for Sarah
   > Learning report for Sarah
   > Team report
   ```

## All Workflows

| What to say | What happens |
|-------------|--------------|
| "Add a PMM" | Registers a PMM with name, email, team |
| "Review these docs for [PMM]" | Scores across 29 dimensions, saves review, updates profile |
| "Show campaign [id] for [PMM]" | Full iteration arc with feedback retention chain |
| "Show patterns for [PMM]" | Strengths, weaknesses, growth areas, draft-stage strengths |
| "Set a goal for [PMM]" | Creates an improvement track with baseline and target |
| "Report on [PMM]" | Full coaching report with score trends |
| "Promotion report for [PMM]" | Quantified growth portfolio for appraisals |
| "Learning report for [PMM]" | Is feedback being internalized? Draft quality trends |
| "Team report" | Cross-PMM dimension heatmap, gaps, standouts |
| "Compare [PMM1] and [PMM2]" | Side-by-side dimension comparison |
| "Refresh patterns for [PMM]" | Recompute all patterns from review history |
| "Generate dashboard" | Builds a visual HTML dashboard from all data |

---

## Dashboard

Master Reviewer includes a visual dashboard for managers and PMMs to review progress without reading raw markdown files.

```bash
# Generate the dashboard (run after adding new reviews)
python3 dashboard/generate.py

# Opens automatically, or open manually
open dashboard/index.html
```

**What you'll see:**

- **Team Dashboard** — Team-level stats, each person's progress card with a score ring and skill category breakdown, team-wide strengths and growth areas, recent review activity
- **Team Skills Map** — Color-coded grid of every team member × every skill. Spot who's strong where, and where the whole team needs coaching
- **Individual view** — Click any person to see their radar chart (draft vs. final), strongest and weakest skills, biggest improvements, project history, patterns, and their current "What to Work on Next" priorities

The dashboard is a single self-contained HTML file — no server, no dependencies, no internet required. It reads from the same markdown files everything else uses.

---

## Project Structure

```
├── CLAUDE.md              ← Agent instructions (the brain)
├── templates/             ← Scoring rubrics and file templates
│   ├── scoring-rubric.md  ← 29 dimensions with 4-band rubrics + applicability matrix
│   ├── review-template.md ← Review output format with feedback retention check
│   └── pmm-profile.md     ← Profile structure with campaign tracking
├── dashboard/             ← Visual dashboard
│   ├── generate.py        ← Parses markdown files, generates index.html
│   └── index.html         ← Generated dashboard (open in browser, gitignored)
├── pmms/                  ← PMM profiles (created when you add PMMs)
├── reviews/               ← Review analyses (created per iteration)
└── reports/               ← Generated reports
```

## Customization

- **Adjust rubrics**: Edit `templates/scoring-rubric.md` to match your team's standards
- **Add dimensions**: Add new sections to the rubric and update `CLAUDE.md`
- **Change applicability**: Modify the applicability matrix for your document types
- **Adjust weights**: Modify overall score calculation if some categories matter more
- **Add doc types**: Extend the applicability matrix in the rubric for new document formats

## License

MIT

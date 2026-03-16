# Build with Claude Code for PMMs #3: Making the Growth Story Visible

**The framework scores the work. The dashboard makes the coaching conversation possible.**

---

## The last mile problem

You've been running reviews for three months. Your PMM profiles have data — dimension scores, campaign arcs, feedback retention rates, patterns. The framework from article #2 is doing its job.

Then your VP asks: "How's the team doing?"

You open a markdown file. It's 130 lines of tables. You start explaining running averages and dimension trajectories and the VP's eyes glaze over before you finish the second sentence.

Or it's appraisal season. You're building a promotion case for someone on your team. You know her draft quality improved from 3.2 to 5.9. You know her feedback retention rate is 85%. You know specificity moved from weakness to strength across three campaigns. But you're assembling this narrative manually — copying numbers from markdown files into a slide deck, trying to make the growth story visible when the data was designed to be read, not shown.

The framework generates the evidence. But evidence locked in text files is evidence nobody sees.

## Three views for three conversations

The dashboard I built has three views. Not because three is a nice number — because there are three distinct conversations that need visual support, and each one needs different data at a different altitude.

### The team view: "Who needs attention?"

This is the manager's morning view. Cards for each PMM, each with a score ring showing their latest overall score and bars showing how they're performing across the five skill categories. A recent activity feed shows which reviews were run and when.

You're not reading dimension scores here. You're scanning. Which score rings are green and which are amber? Whose Copywriting Craft bar is noticeably shorter than their Strategic Foundation bar? Who hasn't had a review in six weeks?

The team view answers the question every manager carries around but rarely has data for: where should I spend my coaching time this week? Not on the PMM who's consistently green across the board. On the one whose strategy scores are climbing but whose craft scores haven't moved in two campaigns. That's where attention has leverage.

### The skills heatmap: "Where are the real gaps?"

This is the view that changes team-level decisions.

A table. All your PMMs down the left side. All 29 dimensions across the top. Each cell color-coded by final score — dark green for strong, amber for developing, red for needs work. Team averages in the rightmost column.

The first time you look at this, something jumps out that you couldn't see in individual reviews: patterns that span the team. Three out of four PMMs scoring below 5 on objection handling. Everyone strong on messaging clarity but weak on sentence rhythm. One PMM scoring 9 on competitive positioning while everyone else sits at 5.

These aren't individual coaching notes anymore. A team-wide gap in objection handling is a training need — a workshop, a shared resource, a pairing session with someone who does it well. A standout in competitive positioning is a peer mentoring opportunity you didn't know you had.

Without the heatmap, you'd discover these patterns eventually, maybe, across dozens of individual reviews over months. With it, you see them in five seconds.

This is also the view that answers uncomfortable questions honestly. "Are we a strong PMM team?" becomes a specific conversation: "We're a strong strategy team with a craft gap. Our messaging is clear and differentiated — but the writing itself isn't sharp enough. Here's exactly where." That's a different conversation than vibes.

### The individual view: "What's my shape?"

This is where the PMM sees themselves. And for a lot of people, it's the first time they've ever had a visual picture of their craft profile.

The centerpiece is a radar chart — a pentagon with one axis per skill category, showing two overlapping shapes. The dashed shape is their initial draft. The solid shape is their final version. The gap between the two is how much the editing process is doing for them.

A PMM whose two shapes nearly overlap is someone whose instincts are sharp — their first drafts are already close to final quality. A PMM with a big gap is someone who's responsive to feedback but hasn't internalized it yet. Both are useful to know. Neither is a judgment — it's a starting point for a conversation.

Below the radar: their top 5 strongest skills and top 5 growth opportunities. A bar chart showing biggest improvements — which dimensions moved most from draft to final. Their project history with iteration scores. And their current "What to Work on Next" priorities pulled from the most recent review.

The individual view is the one that changes the self-coaching conversation. When a PMM can see that their Strategic Foundation pentagon is wide but their Copywriting Craft axis is stunted, they don't need someone to tell them where to focus. They can see it. And next quarter, they can see whether the shape changed.

## What changes when the data is visible

I want to linger on this for a second because it's the thing that surprised me most about building the dashboard.

The framework from article #2 is useful. Dimension scores, feedback retention, draft quality progression — that's real data that answers real questions. But the behavioral change happened when the data became visible.

The VP stops asking "how's the team doing?" as a conversation starter and starts asking "why is everyone low on objection handling?" That's a better question. It leads somewhere.

The PMM stops thinking of feedback as a checklist of things their manager wants changed and starts seeing their own skill profile — a shape they can watch evolve. The improvement isn't happening to them. They're watching it happen.

The manager stops giving the same note in isolation and starts seeing it in the context of a pattern. "I've been coaching sentence rhythm for three campaigns and the score hasn't moved. Maybe I need to change my approach — show examples instead of giving notes." That's the dashboard prompting a coaching decision that would have taken months of accumulated frustration to arrive at otherwise.

Visibility doesn't just present data. It changes which questions people ask.

## The build: one decision worth mentioning

Same philosophy as articles #1 and #2 — Claude Code, no external dependencies. A Python script parses the markdown files (PMM profiles and reviews), extracts the structured data, and generates a single self-contained HTML file. All CSS, all JavaScript, all chart rendering — inline. Open the HTML in any browser. No server, no build step.

The interesting design decision was language. The framework uses precise terminology — "dimensions," "campaigns," "iterations," "contextual applicability." That's right for the scoring rubric. It's wrong for a dashboard that a VP might glance at.

So the dashboard translates. "Dimensions" become "skills." "Campaigns" become "projects." "Total reviews" becomes "reviews completed." "Contextual dimensions scored" becomes "skills assessed." Small shifts, but they're the difference between a tool that feels like it was built for the framework designer and one that feels like it was built for the person looking at it.

The radar chart and heatmap are rendered with inline SVG — no charting library. The score rings on the team view are SVG circles with calculated stroke offsets. This sounds like a detail, but it means the dashboard is truly self-contained. No CDN calls, no dependencies, no "this chart didn't load" moments. Generate the HTML, open it, everything works.

```
python3 dashboard/generate.py
open dashboard/index.html
```

Two commands. The dashboard regenerates from the current state of your markdown files every time you run it. Add a new review, regenerate, see the updated scores.

→ https://github.com/raven-sourav/master-reviewer

## The full picture

Three articles. One system.

**Article #1** built a knowledge brain — 600+ newsletter posts, searchable by meaning, connected across authors. The input layer. What you know.

**Article #2** built a performance framework — 29 dimensions across 5 categories, with Focus 3 prioritization, feedback retention tracking, and draft quality progression. The measurement layer. How you grow.

**Article #3** built the visual layer — a dashboard that makes the growth story visible to the manager, the VP, and the PMM themselves. The communication layer. How you show it.

Together, they answer the question I started with: can a PMM build their own tools, without an engineering team, that actually change how they work?

The answer isn't just "yes." It's that the tools you build for yourself — the ones shaped by exactly your problems, your workflows, your frustrations — end up being more useful than the ones you could buy. Because nobody's selling a PMM performance framework. Nobody's selling a newsletter knowledge brain. The category doesn't exist yet.

So you build it. And then you share it.

---

*This is part 3 of Build with Claude Code for PMMs — a series on building your own marketing tools without an engineering team. Built with Claude Code. No code written manually. The whole series and all three tools are open source.*

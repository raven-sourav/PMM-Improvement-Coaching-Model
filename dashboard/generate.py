#!/usr/bin/env python3
"""
Master Reviewer Dashboard Generator

Parses PMM profiles and review markdown files, then generates a self-contained
HTML dashboard with charts, heatmaps, and navigation. No external dependencies.

Usage:
    python dashboard/generate.py
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ─── Constants ───────────────────────────────────────────────────────────────

DIMENSIONS = {
    "A": {
        "name": "Strategic Foundation",
        "desc": "Is the core message right?",
        "dims": [
            ("messaging_clarity", "Messaging Clarity"),
            ("value_proposition", "Value Proposition"),
            ("audience_targeting", "Audience Targeting"),
            ("competitive_positioning", "Competitive Positioning"),
            ("cta_effectiveness", "CTA Effectiveness"),
            ("evidence_usage", "Evidence & Proof Points"),
        ],
    },
    "B": {
        "name": "Copywriting Craft",
        "desc": "Is the writing sharp and engaging?",
        "dims": [
            ("headline_hook", "Headline & Hook Quality"),
            ("word_economy", "Word Economy"),
            ("specificity", "Specificity"),
            ("sentence_rhythm", "Sentence Rhythm"),
            ("repetition_parallelism", "Parallel Structure"),
            ("power_language", "Power Language"),
            ("vivid_language", "Vivid Language"),
            ("emotional_resonance", "Emotional Resonance"),
            ("opening_closing_craft", "Opening & Closing"),
            ("readability", "Readability"),
        ],
    },
    "C": {
        "name": "Structure & Logic",
        "desc": "Is it organized and persuasive?",
        "dims": [
            ("information_hierarchy", "Information Hierarchy"),
            ("argument_structure", "Argument Structure"),
            ("transitions", "Transitions"),
            ("scannability", "Scannability"),
        ],
    },
    "D": {
        "name": "Persuasion & Conversion",
        "desc": "Does it convince and convert?",
        "dims": [
            ("social_proof", "Social Proof"),
            ("benefit_feature_ratio", "Benefits vs. Features"),
            ("objection_handling", "Objection Handling"),
            ("urgency_trust", "Urgency & Trust"),
            ("technical_simplification", "Technical Simplification"),
        ],
    },
    "E": {
        "name": "Brand & Voice",
        "desc": "Does it sound like us?",
        "dims": [
            ("tone_consistency", "Tone Consistency"),
            ("brand_voice_distinctiveness", "Brand Voice"),
            ("confidence_calibration", "Confidence Calibration"),
            ("jargon_appropriateness", "Jargon Appropriateness"),
        ],
    },
}

_NAME_TO_KEY = {}
_KEY_TO_NAME = {}
_KEY_TO_CAT = {}
for cat_key, cat_data in DIMENSIONS.items():
    for dim_key, dim_name in cat_data["dims"]:
        _NAME_TO_KEY[dim_name.lower()] = dim_key
        _KEY_TO_NAME[dim_key] = dim_name
        _KEY_TO_CAT[dim_key] = cat_key

_ALIASES = {
    "sentence craft & rhythm": "sentence_rhythm",
    "sentence rhythm & musicality": "sentence_rhythm",
    "sentence rhythm": "sentence_rhythm",
    "word economy & conciseness": "word_economy",
    "word economy": "word_economy",
    "specificity vs. vagueness": "specificity",
    "specificity": "specificity",
    "readability & accessibility": "readability",
    "readability": "readability",
    "scannability & formatting": "scannability",
    "scannability": "scannability",
    "power language & verb strength": "power_language",
    "power language": "power_language",
    "evidence & proof points": "evidence_usage",
    "evidence": "evidence_usage",
    "audience": "audience_targeting",
    "audience targeting": "audience_targeting",
    "benefit vs. feature ratio": "benefit_feature_ratio",
    "benefit ratio": "benefit_feature_ratio",
    "repetition & parallel structure": "repetition_parallelism",
    "headline & hook quality": "headline_hook",
    "sensory & vivid language": "vivid_language",
    "emotional resonance & empathy": "emotional_resonance",
    "opening & closing craft": "opening_closing_craft",
    "social proof placement": "social_proof",
    "urgency & trust signals": "urgency_trust",
    "brand voice distinctiveness": "brand_voice_distinctiveness",
    "cta effectiveness": "cta_effectiveness",
    "transition quality": "transitions",
}


def resolve_dim_key(name: str) -> Optional[str]:
    lower = name.strip().lower()
    if lower in _NAME_TO_KEY:
        return _NAME_TO_KEY[lower]
    if lower in _ALIASES:
        return _ALIASES[lower]
    for known, key in _NAME_TO_KEY.items():
        if lower in known or known in lower:
            return key
    for known, key in _ALIASES.items():
        if lower in known or known in lower:
            return key
    return None


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class CampaignInfo:
    campaign_id: str
    doc_type: str
    status: str
    period: str
    arc: str
    iterations: list = field(default_factory=list)
    starting_quality: str = ""


@dataclass
class PMMProfile:
    name: str
    email: str
    role: str
    team: str
    registered: str
    total_reviews: int
    total_campaigns: int
    campaigns: list = field(default_factory=list)
    running_averages: dict = field(default_factory=dict)
    patterns: dict = field(default_factory=dict)
    improvement_tracks: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    cross_campaign: dict = field(default_factory=dict)


@dataclass
class Review:
    title: str
    pmm_name: str
    pmm_email: str
    date: str
    doc_type: str
    campaign_id: str
    iteration: str
    dimensions_scored: int
    overall_score: int
    summary: str
    top_strength: str
    top_growth: str
    focus_3: list = field(default_factory=list)
    dimension_scores: dict = field(default_factory=dict)
    category_averages: dict = field(default_factory=dict)


# ─── Parsing Helpers ─────────────────────────────────────────────────────────

def parse_float(val: str) -> Optional[float]:
    if not val:
        return None
    val = val.strip()
    if val in ("-", "\u2014", "not scored", "n/a", ""):
        return None
    m = re.search(r"([+-]?\d+\.?\d*)", val)
    return float(m.group(1)) if m else None


def parse_int(val: str) -> int:
    m = re.search(r"(\d+)", val.strip())
    return int(m.group(1)) if m else 0


def extract_metadata(text: str) -> dict:
    meta = {}
    for m in re.finditer(r"^\- \*\*(.+?)\*\*:\s*(.+)$", text, re.MULTILINE):
        meta[m.group(1).strip()] = m.group(2).strip()
    return meta


def split_sections(text: str, level: int = 2) -> dict:
    prefix = "#" * level + " "
    sections = {}
    current_heading = None
    current_lines = []
    for line in text.split("\n"):
        if line.startswith(prefix) and not line.startswith(prefix + "#"):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines)
            current_heading = line[len(prefix):].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines)
    return sections


def parse_md_table(text: str) -> list:
    lines = [l.strip() for l in text.strip().split("\n") if l.strip().startswith("|")]
    if len(lines) < 3:
        return []
    headers = [h.strip() for h in lines[0].split("|")[1:-1]]
    rows = []
    for line in lines[2:]:
        if line.startswith("|--") or line.startswith("| --"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


# ─── PMM Profile Parser ─────────────────────────────────────────────────────

def parse_pmm_profile(filepath: Path) -> PMMProfile:
    text = filepath.read_text()
    meta = extract_metadata(text)

    name_match = re.search(r"^# PMM Profile:\s*(.+)$", text, re.MULTILINE)
    profile = PMMProfile(
        name=name_match.group(1).strip() if name_match else "Unknown",
        email=meta.get("Email", ""),
        role=meta.get("Role", "pmm"),
        team=meta.get("Team", ""),
        registered=meta.get("Registered", ""),
        total_reviews=parse_int(meta.get("Total Reviews", "0")),
        total_campaigns=parse_int(meta.get("Total Campaigns", "0")),
    )

    sections = split_sections(text, level=2)

    # Parse campaigns
    if "Campaign History" in sections:
        camp_sections = split_sections(sections["Campaign History"], level=3)
        for heading, content in camp_sections.items():
            m = re.match(r"Campaign:\s*(.+?)\s*\((.+?)\)", heading)
            if not m:
                continue
            camp = CampaignInfo(
                campaign_id=m.group(1).strip(),
                doc_type=m.group(2).strip(),
                status="", period="", arc="",
            )
            for line in content.split("\n"):
                if line.startswith("**Status**:"):
                    camp.status = line.split(":", 1)[1].strip()
                elif line.startswith("**Period**:"):
                    camp.period = line.split(":", 1)[1].strip()
                elif line.startswith("**Arc**:"):
                    camp.arc = line.split(":", 1)[1].strip()
                elif line.startswith("**Starting Quality"):
                    camp.starting_quality = line.split(":", 1)[1].strip() if ":" in line else ""
            camp.iterations = parse_md_table(content)
            profile.campaigns.append(camp)

    # Parse running averages
    if "Running Averages by Category" in sections:
        cat_sections = split_sections(sections["Running Averages by Category"], level=3)
        for heading, content in cat_sections.items():
            cat_match = re.match(r"([A-E])\.", heading)
            if not cat_match:
                continue
            cat_key = cat_match.group(1)
            rows = parse_md_table(content)
            dims = {}
            for row in rows:
                dim_name = row.get("Dimension", "")
                dim_key = resolve_dim_key(dim_name)
                if dim_key:
                    dims[dim_key] = {
                        "key": dim_key,
                        "name": dim_name,
                        "category": cat_key,
                        "v1": parse_float(row.get("Avg V1", "-")),
                        "v2": parse_float(row.get("Avg V2", "-")),
                        "improvement": parse_float(row.get("Avg Improvement", "-")),
                    }
            profile.running_averages[cat_key] = dims

    # Parse patterns
    if "Patterns" in sections:
        pat_sections = split_sections(sections["Patterns"], level=3)
        for heading, content in pat_sections.items():
            key = heading.lower().replace(" ", "_").replace("-", "_")
            items = []
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("- "):
                    items.append(line[2:].strip())
            profile.patterns[key] = items

    # Parse cross-campaign trends
    if "Cross-Campaign Trends" in sections:
        trend_sections = split_sections(sections["Cross-Campaign Trends"], level=3)
        if "Draft Quality Progression" in trend_sections:
            profile.cross_campaign["draft_quality"] = parse_md_table(trend_sections["Draft Quality Progression"])
        if "Dimension Trajectories (Final Scores Across Campaigns)" in trend_sections:
            profile.cross_campaign["trajectories"] = parse_md_table(
                trend_sections["Dimension Trajectories (Final Scores Across Campaigns)"]
            )

    # Parse notes
    if "Notes" in sections:
        for line in sections["Notes"].split("\n"):
            line = line.strip()
            if line.startswith("- "):
                profile.notes.append(line[2:].strip())

    return profile


# ─── Review Parser ───────────────────────────────────────────────────────────

def parse_review(filepath: Path) -> Review:
    text = filepath.read_text()
    meta = extract_metadata(text)

    title_match = re.search(r"^# Review:\s*(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filepath.stem

    pmm_raw = meta.get("PMM", "")
    pmm_match = re.match(r"(.+?)\s*\((.+?)\)", pmm_raw)
    pmm_name = pmm_match.group(1).strip() if pmm_match else pmm_raw
    pmm_email = pmm_match.group(2).strip() if pmm_match else ""

    sections = split_sections(text, level=2)
    summary = ""
    top_strength = ""
    top_growth = ""
    if "Summary" in sections:
        summary_text = sections["Summary"]
        paragraphs = [p.strip() for p in summary_text.split("\n\n") if p.strip()]
        summary = paragraphs[0] if paragraphs else ""
        for line in summary_text.split("\n"):
            if line.startswith("**Top Strength**:"):
                top_strength = line.split(":", 1)[1].strip()
            elif line.startswith("**Top Growth Area**:"):
                top_growth = line.split(":", 1)[1].strip()

    focus_3 = []
    if "Focus 3 \u2014 What to Work on Next" in sections:
        f3_sections = split_sections(sections["Focus 3 \u2014 What to Work on Next"], level=3)
        for heading, content in f3_sections.items():
            if heading.startswith("Parked"):
                continue
            # Extract effort and impact lines
            effort = ""
            impact = ""
            for line in content.split("\n"):
                if line.startswith("**Effort**:"):
                    effort = line.split(":", 1)[1].strip()
                elif line.startswith("**Impact**:"):
                    impact = line.split(":", 1)[1].strip()
            focus_3.append({
                "title": heading,
                "content": content.strip()[:300],
                "effort": effort,
                "impact": impact,
            })

    dim_scores = {}
    if "Dimension Scores" in sections:
        cat_sections = split_sections(sections["Dimension Scores"], level=3)
        for heading, content in cat_sections.items():
            cat_match = re.match(r"([A-E])\.", heading)
            if not cat_match:
                continue
            cat_key = cat_match.group(1)
            rows = parse_md_table(content)
            scores = []
            for row in rows:
                dim_name = row.get("Dimension", "")
                dim_key = resolve_dim_key(dim_name)
                if dim_key:
                    scores.append({
                        "key": dim_key,
                        "name": dim_name,
                        "v1": parse_float(row.get("Version 1", "-")),
                        "v2": parse_float(row.get("Version 2", "-")),
                        "change": parse_float(row.get("Change", "-")),
                    })
            dim_scores[cat_key] = scores

    cat_avgs = {}
    if "Category Averages" in sections:
        rows = parse_md_table(sections["Category Averages"])
        for row in rows:
            cat_name = row.get("Category", "")
            cat_match = re.match(r"([A-E])\.", cat_name)
            if cat_match:
                cat_avgs[cat_match.group(1)] = {
                    "v1": parse_float(row.get("Version 1 Avg", "-")),
                    "v2": parse_float(row.get("Version 2 Avg", "-")),
                    "change": parse_float(row.get("Change", "-")),
                }

    return Review(
        title=title,
        pmm_name=pmm_name,
        pmm_email=pmm_email,
        date=meta.get("Date", ""),
        doc_type=meta.get("Document Type", ""),
        campaign_id=meta.get("Campaign", ""),
        iteration=meta.get("Iteration", ""),
        dimensions_scored=parse_int(meta.get("Dimensions Scored", "0")),
        overall_score=parse_int(meta.get("Overall Score", "0")),
        summary=summary,
        top_strength=top_strength,
        top_growth=top_growth,
        focus_3=focus_3,
        dimension_scores=dim_scores,
        category_averages=cat_avgs,
    )


# ─── Serialization ──────────────────────────────────────────────────────────

def serialize_data(pmms, reviews):
    pmm_list = []
    for p in pmms:
        pmm_list.append({
            "name": p.name, "email": p.email, "role": p.role, "team": p.team,
            "registered": p.registered, "total_reviews": p.total_reviews,
            "total_campaigns": p.total_campaigns,
            "campaigns": [
                {"campaign_id": c.campaign_id, "doc_type": c.doc_type,
                 "status": c.status, "period": c.period, "arc": c.arc,
                 "iterations": c.iterations, "starting_quality": c.starting_quality}
                for c in p.campaigns
            ],
            "running_averages": p.running_averages,
            "patterns": p.patterns,
            "improvement_tracks": p.improvement_tracks,
            "notes": p.notes,
            "cross_campaign": p.cross_campaign,
        })

    review_list = []
    for r in reviews:
        review_list.append({
            "title": r.title, "pmm_name": r.pmm_name, "pmm_email": r.pmm_email,
            "date": r.date, "doc_type": r.doc_type, "campaign_id": r.campaign_id,
            "iteration": r.iteration, "dimensions_scored": r.dimensions_scored,
            "overall_score": r.overall_score, "summary": r.summary,
            "top_strength": r.top_strength, "top_growth": r.top_growth,
            "focus_3": r.focus_3, "dimension_scores": r.dimension_scores,
            "category_averages": r.category_averages,
        })

    dim_meta = {}
    for cat_key, cat_data in DIMENSIONS.items():
        dim_meta[cat_key] = {
            "name": cat_data["name"],
            "desc": cat_data["desc"],
            "dims": [{"key": k, "name": n} for k, n in cat_data["dims"]],
        }

    return {"pmms": pmm_list, "reviews": review_list, "dimensions": dim_meta}


# ─── HTML / CSS / JS ─────────────────────────────────────────────────────────

CSS = r"""
:root {
  --sidebar-bg: #111827;
  --sidebar-active: #1f2937;
  --sidebar-hover: #1f2937;
  --sidebar-text: #9ca3af;
  --sidebar-text-active: #ffffff;
  --main-bg: #f8fafc;
  --card-bg: #ffffff;
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --accent: #6366f1;
  --accent-light: #e0e7ff;
  --success: #10b981;
  --success-light: #d1fae5;
  --warning: #f59e0b;
  --warning-light: #fef3c7;
  --danger: #ef4444;
  --danger-light: #fee2e2;
  --border: #e2e8f0;
  --radius: 16px;
  --radius-sm: 10px;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -2px rgba(0,0,0,0.03);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.06), 0 4px 6px -4px rgba(0,0,0,0.04);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, sans-serif;
  background: var(--main-bg);
  color: var(--text-primary);
  display: flex;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

/* ── Sidebar ── */
.sidebar {
  width: 272px; background: var(--sidebar-bg); color: var(--sidebar-text);
  display: flex; flex-direction: column;
  position: fixed; top: 0; left: 0; bottom: 0; z-index: 100; overflow-y: auto;
}
.sidebar-brand { padding: 28px 24px 20px; }
.sidebar-brand h1 { font-size: 17px; font-weight: 700; color: #fff; letter-spacing: -0.3px; }
.sidebar-brand p { font-size: 12px; color: var(--sidebar-text); margin-top: 4px; }
.sidebar-divider { height: 1px; background: rgba(255,255,255,0.06); margin: 0 16px; }
.sidebar-section {
  padding: 20px 24px 8px; font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.8px; color: rgba(255,255,255,0.28); font-weight: 600;
}
.sidebar-nav { list-style: none; padding: 0 8px; }
.sidebar-nav li a {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 16px; color: var(--sidebar-text); text-decoration: none;
  font-size: 14px; transition: all 0.15s; border-radius: 8px; cursor: pointer;
  margin-bottom: 2px;
}
.sidebar-nav li a:hover { background: var(--sidebar-hover); color: #e2e8f0; }
.sidebar-nav li a.active {
  background: var(--sidebar-active); color: var(--sidebar-text-active); font-weight: 500;
}
.sidebar-nav .nav-icon { width: 18px; text-align: center; font-size: 14px; opacity: 0.7; }
.sidebar-nav .nav-badge {
  margin-left: auto; background: rgba(99,102,241,0.25); color: #a5b4fc;
  padding: 2px 9px; border-radius: 10px; font-size: 11px; font-weight: 600;
}

/* ── Main Content ── */
main { margin-left: 272px; flex: 1; padding: 36px 40px; max-width: 1280px; }

/* ── Page Header ── */
.page-header { margin-bottom: 32px; }
.page-header h2 { font-size: 26px; font-weight: 700; letter-spacing: -0.5px; }
.page-header p { color: var(--text-secondary); font-size: 15px; margin-top: 6px; line-height: 1.5; }

/* ── Stat Cards ── */
.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }
.stat-card {
  background: var(--card-bg); border-radius: var(--radius); padding: 24px;
  box-shadow: var(--shadow); border: 1px solid var(--border);
}
.stat-card .stat-icon { font-size: 20px; margin-bottom: 12px; }
.stat-card .stat-label { font-size: 13px; color: var(--text-secondary); font-weight: 500; }
.stat-card .stat-value { font-size: 36px; font-weight: 700; margin-top: 4px; letter-spacing: -1px; }
.stat-card .stat-sub { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

/* ── Cards ── */
.card {
  background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow);
  margin-bottom: 24px; border: 1px solid var(--border); overflow: hidden;
}
.card-header {
  padding: 20px 28px; border-bottom: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
}
.card-header h3 { font-size: 16px; font-weight: 600; }
.card-header .card-subtitle { font-size: 13px; color: var(--text-secondary); }
.card-body { padding: 28px; }

/* ── Grid ── */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }

/* ── PMM Progress Cards (Home) ── */
.pmm-progress-card {
  background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow);
  border: 1px solid var(--border); padding: 28px; cursor: pointer;
  transition: all 0.2s ease;
}
.pmm-progress-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-3px); border-color: var(--accent); }
.pmm-progress-card .ppc-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.pmm-progress-card .ppc-name { font-size: 18px; font-weight: 700; }
.pmm-progress-card .ppc-role { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }
.pmm-progress-card .ppc-score-ring {
  width: 64px; height: 64px; position: relative;
}
.pmm-progress-card .ppc-score-ring svg { transform: rotate(-90deg); }
.pmm-progress-card .ppc-score-num {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  font-size: 18px; font-weight: 700;
}

.ppc-categories { display: flex; gap: 6px; margin-bottom: 20px; }
.ppc-cat-bar { flex: 1; height: 8px; border-radius: 4px; position: relative; }
.ppc-cat-tooltip {
  display: none; position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%);
  background: var(--text-primary); color: #fff; padding: 4px 10px; border-radius: 6px;
  font-size: 11px; white-space: nowrap; z-index: 10;
}
.ppc-cat-bar:hover .ppc-cat-tooltip { display: block; }

.ppc-meta { display: flex; gap: 24px; }
.ppc-meta-item { }
.ppc-meta-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; }
.ppc-meta-value { font-size: 14px; font-weight: 600; margin-top: 2px; }

.ppc-strengths { margin-top: 18px; padding-top: 18px; border-top: 1px solid var(--border); }
.ppc-strengths-title { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 8px; }
.ppc-tag {
  display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 12px;
  font-weight: 500; margin-right: 6px; margin-bottom: 4px;
}
.ppc-tag-green { background: var(--success-light); color: #065f46; }
.ppc-tag-amber { background: var(--warning-light); color: #92400e; }
.ppc-tag-red { background: var(--danger-light); color: #991b1b; }

/* ── Score Circle ── */
.score-circle { display: inline-flex; align-items: center; justify-content: center; }

/* ── Tables ── */
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th {
  text-align: left; padding: 12px 16px; border-bottom: 2px solid var(--border);
  font-weight: 600; color: var(--text-secondary); font-size: 12px;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.data-table td { padding: 12px 16px; border-bottom: 1px solid var(--border); }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover { background: #f8fafc; }

/* ── Heatmap ── */
.heatmap-wrap { overflow-x: auto; border-radius: var(--radius-sm); }
.heatmap { border-collapse: collapse; font-size: 13px; width: 100%; }
.heatmap th, .heatmap td { padding: 10px 14px; text-align: center; border: 1px solid var(--border); }
.heatmap th {
  background: #f1f5f9; font-weight: 600; position: sticky; top: 0; z-index: 1;
}
.heatmap th:first-child { text-align: left; min-width: 210px; position: sticky; left: 0; z-index: 2; background: #f1f5f9; }
.heatmap td:first-child { text-align: left; font-weight: 500; position: sticky; left: 0; background: var(--card-bg); z-index: 1; }
.heatmap .cat-row td {
  background: var(--sidebar-bg) !important; color: #fff; font-weight: 600;
  text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;
}
.heatmap td.heat { font-weight: 600; transition: all 0.15s; }
.heatmap td.heat:hover { transform: scale(1.05); box-shadow: var(--shadow-md); z-index: 2; position: relative; }

/* ── Bar Chart Rows ── */
.bar-group { margin-bottom: 24px; }
.bar-group-title {
  font-size: 13px; font-weight: 600; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;
  padding-bottom: 8px; border-bottom: 1px solid var(--border);
}
.bar-group-subtitle { font-size: 12px; color: var(--text-muted); font-weight: 400; text-transform: none; letter-spacing: 0; margin-left: 8px; }
.bar-row { display: flex; align-items: center; margin-bottom: 10px; gap: 12px; }
.bar-label { width: 180px; font-size: 13px; text-align: right; flex-shrink: 0; color: var(--text-primary); }
.bar-track { flex: 1; height: 32px; background: #f1f5f9; border-radius: 8px; position: relative; overflow: hidden; }
.bar-v1 { position: absolute; top: 0; left: 0; height: 100%; border-radius: 8px; opacity: 0.2; }
.bar-fill {
  height: 100%; border-radius: 8px; display: flex; align-items: center;
  padding: 0 10px; font-size: 12px; font-weight: 600; color: #fff;
  transition: width 0.6s ease; position: relative; z-index: 1;
}
.bar-fill-inner { margin-left: auto; }
.bar-delta { width: 60px; font-size: 13px; font-weight: 600; text-align: right; flex-shrink: 0; }
.delta-pos { color: var(--success); }
.delta-neg { color: var(--danger); }

/* ── Radar ── */
.radar-wrap { display: flex; justify-content: center; }

/* ── Patterns ── */
.pattern-section { margin-bottom: 20px; }
.pattern-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
.pattern-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.pattern-list { list-style: none; }
.pattern-list li {
  padding: 12px 16px; border-radius: var(--radius-sm); margin-bottom: 8px;
  font-size: 14px; line-height: 1.6; border-left: 3px solid;
}
.pat-strength { border-color: var(--success); background: #f0fdf4; }
.pat-weakness { border-color: var(--danger); background: #fef2f2; }
.pat-growth { border-color: var(--warning); background: #fffbeb; }

/* ── Focus Items ── */
.focus-card {
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  padding: 20px; margin-bottom: 14px; transition: all 0.15s;
}
.focus-card:hover { border-color: var(--accent); box-shadow: var(--shadow); }
.focus-card .focus-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 24px; height: 24px; border-radius: 50%; background: var(--accent);
  color: #fff; font-size: 12px; font-weight: 700; margin-right: 10px;
}
.focus-card h4 { display: inline; font-size: 14px; font-weight: 600; }
.focus-card .focus-effort { font-size: 12px; color: var(--text-muted); margin-top: 8px; }
.focus-card .focus-impact { font-size: 12px; color: var(--accent); margin-top: 4px; font-weight: 500; }

/* ── Campaign Cards ── */
.campaign-card {
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  padding: 20px; margin-bottom: 16px;
}
.campaign-card .cc-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.campaign-card .cc-title { font-size: 16px; font-weight: 600; }
.campaign-card .cc-type { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.campaign-card .cc-status {
  padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
}
.status-active { background: var(--accent-light); color: var(--accent); }
.status-complete { background: var(--success-light); color: #065f46; }
.cc-summary { font-size: 14px; color: var(--text-secondary); line-height: 1.5; margin-top: 12px; }

/* ── Tabs ── */
.tabs { display: flex; gap: 0; border-bottom: 2px solid var(--border); margin-bottom: 28px; }
.tab {
  padding: 12px 24px; font-size: 14px; font-weight: 500; color: var(--text-secondary);
  cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: all 0.15s;
}
.tab:hover { color: var(--text-primary); }
.tab.active { color: var(--accent); border-bottom-color: var(--accent); font-weight: 600; }
.tab-content { display: none; }
.tab-content.active { display: block; }

/* ── Review card in activity ── */
.activity-item {
  display: flex; gap: 20px; padding: 20px 0; border-bottom: 1px solid var(--border);
  cursor: pointer; transition: all 0.15s;
}
.activity-item:hover { background: #f8fafc; margin: 0 -28px; padding-left: 28px; padding-right: 28px; }
.activity-item:last-child { border-bottom: none; }
.activity-score {
  width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; font-size: 18px; font-weight: 700; flex-shrink: 0;
}
.activity-detail { flex: 1; }
.activity-detail h4 { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.activity-detail p { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }
.activity-meta {
  font-size: 12px; color: var(--text-muted); margin-top: 6px;
  display: flex; gap: 16px;
}

/* ── Utility ── */
.hidden { display: none !important; }
.mt-2 { margin-top: 8px; }
.mt-4 { margin-top: 16px; }
.mt-6 { margin-top: 24px; }
.mb-4 { margin-bottom: 16px; }
.mb-6 { margin-bottom: 24px; }
.text-muted { color: var(--text-secondary); }

.back-link {
  font-size: 13px; color: var(--accent); cursor: pointer;
  display: inline-flex; align-items: center; gap: 6px; margin-bottom: 16px;
  font-weight: 500;
}
.back-link:hover { text-decoration: underline; }

.empty-state {
  text-align: center; padding: 60px 20px; color: var(--text-muted);
}
.empty-state .empty-icon { font-size: 40px; margin-bottom: 16px; opacity: 0.4; }
.empty-state p { font-size: 15px; }

.legend { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-secondary); }
.legend-swatch { width: 14px; height: 14px; border-radius: 3px; }

/* ── Responsive ── */
@media (max-width: 960px) {
  .sidebar { width: 64px; }
  .sidebar-brand p, .sidebar-section, .sidebar-nav li a span, .sidebar-nav .nav-badge { display: none; }
  .sidebar-brand h1 { font-size: 13px; text-align: center; }
  .sidebar-nav li a { justify-content: center; padding: 12px; }
  main { margin-left: 64px; padding: 20px; }
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
"""

JS = r"""
const DATA = __DATA_PLACEHOLDER__;

// ─── Helpers ────────────────────────────────────────────────────────────────

function scoreColor(s) {
  if (s == null) return '#cbd5e1';
  if (s >= 8) return '#10b981';
  if (s >= 6) return '#6366f1';
  if (s >= 4) return '#f59e0b';
  return '#ef4444';
}

function scoreBg(s) {
  if (s == null) return '#f1f5f9';
  if (s >= 8) return '#d1fae5';
  if (s >= 6) return '#e0e7ff';
  if (s >= 4) return '#fef3c7';
  return '#fee2e2';
}

function heatBg(s) {
  if (s == null) return '#f1f5f9';
  if (s >= 8.5) return '#059669';
  if (s >= 7.5) return '#10b981';
  if (s >= 6.5) return '#34d399';
  if (s >= 5.5) return '#a7f3d0';
  if (s >= 4.5) return '#fde68a';
  if (s >= 3.5) return '#fbbf24';
  return '#f87171';
}

function heatFg(s) {
  if (s == null) return '#94a3b8';
  if (s >= 6.5) return '#fff';
  if (s >= 4.5) return '#1e293b';
  return '#fff';
}

function changeHtml(v) {
  if (v == null) return '<span style="color:#94a3b8">—</span>';
  let c = v > 0 ? 'delta-pos' : v < 0 ? 'delta-neg' : '';
  return `<span class="${c}">${v > 0?'+':''}${v.toFixed(1)}</span>`;
}

function docTypeLabel(t) {
  let map = {
    messaging_doc: 'Messaging Document', positioning: 'Positioning', copy: 'Copy',
    launch_brief: 'Launch Brief', blog: 'Blog Post', case_study: 'Case Study',
    email: 'Email', landing_page: 'Landing Page',
  };
  return map[t] || t.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function getLatestScore(pmm) {
  let r = DATA.reviews.filter(x => x.pmm_email === pmm.email).sort((a,b) => b.date.localeCompare(a.date));
  return r.length > 0 ? r[0].overall_score : null;
}

function getV2Avg(pmm) {
  let vals = [];
  for (let cat of Object.values(pmm.running_averages))
    for (let dim of Object.values(cat))
      if (dim.v2 != null) vals.push(dim.v2);
  return vals.length > 0 ? (vals.reduce((a,b)=>a+b,0)/vals.length) : null;
}

function getCatAvg(pmm, catKey, version) {
  let cat = pmm.running_averages[catKey] || {};
  let vals = [];
  for (let dim of Object.values(cat)) {
    let v = version === 'v1' ? dim.v1 : dim.v2;
    if (v != null) vals.push(v);
  }
  return vals.length > 0 ? vals.reduce((a,b)=>a+b,0)/vals.length : null;
}

function getTopDims(pmm, count, direction) {
  let all = [];
  for (let [ck, cat] of Object.entries(pmm.running_averages))
    for (let [dk, dim] of Object.entries(cat))
      if (dim.v2 != null) all.push({key: dk, name: dim.name, v2: dim.v2, imp: dim.improvement});
  all.sort((a,b) => direction === 'top' ? b.v2 - a.v2 : a.v2 - b.v2);
  return all.slice(0, count);
}

function scoreRingSvg(score, size, stroke) {
  if (score == null) return `<div style="width:${size}px;height:${size}px;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-size:${size/3.5}px;font-weight:700">—</div>`;
  let r = (size - stroke) / 2;
  let circ = 2 * Math.PI * r;
  let pct = Math.min(score / 100, 1);
  let dashoffset = circ * (1 - pct);
  let color = scoreColor(score / 10);
  return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" style="transform:rotate(-90deg)">
    <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="#f1f5f9" stroke-width="${stroke}"/>
    <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="${color}" stroke-width="${stroke}"
      stroke-dasharray="${circ}" stroke-dashoffset="${dashoffset}" stroke-linecap="round"
      style="transition:stroke-dashoffset 0.8s ease"/>
  </svg>`;
}

// ─── Navigation ─────────────────────────────────────────────────────────────

let currentView = 'home';
let currentPMM = null;

function navigate(view, email) {
  currentView = view;
  currentPMM = email || null;
  document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
  let id = view === 'home' ? 'nav-home' : view === 'skills' ? 'nav-skills' : `nav-pmm-${email}`;
  let el = document.getElementById(id);
  if (el) el.classList.add('active');
  renderContent();
  window.scrollTo(0, 0);
}

function renderContent() {
  const main = document.getElementById('content');
  switch (currentView) {
    case 'home': main.innerHTML = renderHome(); break;
    case 'skills': main.innerHTML = renderSkillsMap(); break;
    case 'pmm': main.innerHTML = renderPMMDetail(currentPMM); break;
    default: main.innerHTML = renderHome();
  }
}

// ─── HOME: Manager's view ───────────────────────────────────────────────────

function renderHome() {
  let pmms = DATA.pmms;
  let totalReviews = pmms.reduce((s,p) => s + p.total_reviews, 0);
  let scores = pmms.map(p => getLatestScore(p)).filter(s => s != null);
  let avgScore = scores.length > 0 ? Math.round(scores.reduce((a,b)=>a+b,0)/scores.length) : 0;

  // Find team-wide best & weakest dims
  let dimTotals = {};
  let dimCounts = {};
  pmms.forEach(p => {
    for (let cat of Object.values(p.running_averages))
      for (let [k, dim] of Object.entries(cat))
        if (dim.v2 != null) {
          dimTotals[k] = (dimTotals[k]||0) + dim.v2;
          dimCounts[k] = (dimCounts[k]||0) + 1;
        }
  });
  let dimAvgs = Object.entries(dimTotals).map(([k,t]) => ({key:k, avg: t/dimCounts[k], name: findDimName(k)}));
  dimAvgs.sort((a,b) => b.avg - a.avg);
  let teamStrengths = dimAvgs.slice(0, 3);
  let teamGaps = dimAvgs.slice(-3).reverse();

  let html = `
    <div class="page-header">
      <h2>Team Dashboard</h2>
      <p>See how your product marketing team is performing across reviews. Click any team member for a detailed breakdown.</p>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon">&#128101;</div>
        <div class="stat-label">Team Members</div>
        <div class="stat-value">${pmms.length}</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">&#128196;</div>
        <div class="stat-label">Reviews Completed</div>
        <div class="stat-value">${totalReviews}</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">&#127919;</div>
        <div class="stat-label">Team Average Score</div>
        <div class="stat-value" style="color:${scoreColor(avgScore/10)}">${avgScore}<span style="font-size:16px;color:var(--text-muted)">/100</span></div>
        <div class="stat-sub">Based on most recent review per person</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">&#128200;</div>
        <div class="stat-label">Avg Improvement</div>
        <div class="stat-value delta-pos">+${getTeamAvgImprovement().toFixed(1)}</div>
        <div class="stat-sub">Points gained from first draft to final</div>
      </div>
    </div>

    <!-- Team Strengths & Gaps -->
    <div class="grid-2 mb-6">
      <div class="card">
        <div class="card-header"><h3>Team Strengths</h3><span class="card-subtitle">Highest-scoring skills across the team</span></div>
        <div class="card-body">
          ${teamStrengths.map((d,i) => `
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:${i<2?'14px':'0'}">
              <div style="width:32px;height:32px;border-radius:8px;background:var(--success-light);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#065f46">${i+1}</div>
              <div style="flex:1">
                <div style="font-size:14px;font-weight:600">${d.name}</div>
              </div>
              <div style="font-size:18px;font-weight:700;color:var(--success)">${d.avg.toFixed(1)}<span style="font-size:12px;color:var(--text-muted)">/10</span></div>
            </div>
          `).join('')}
        </div>
      </div>
      <div class="card">
        <div class="card-header"><h3>Areas for Growth</h3><span class="card-subtitle">Where the team could improve most</span></div>
        <div class="card-body">
          ${teamGaps.map((d,i) => `
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:${i<2?'14px':'0'}">
              <div style="width:32px;height:32px;border-radius:8px;background:var(--warning-light);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#92400e">${i+1}</div>
              <div style="flex:1">
                <div style="font-size:14px;font-weight:600">${d.name}</div>
              </div>
              <div style="font-size:18px;font-weight:700;color:var(--warning)">${d.avg.toFixed(1)}<span style="font-size:12px;color:var(--text-muted)">/10</span></div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- PMM Progress Cards -->
    <div class="card-header" style="background:transparent;border:none;padding:0 0 16px 0">
      <h3>Team Members</h3>
    </div>
    <div class="grid-2 mb-6">
      ${pmms.map(p => renderPMMProgressCard(p)).join('')}
    </div>

    <!-- Recent Activity -->
    <div class="card">
      <div class="card-header"><h3>Recent Reviews</h3><span class="card-subtitle">Latest review activity across the team</span></div>
      <div class="card-body">
        ${DATA.reviews.length > 0 ? DATA.reviews.sort((a,b) => b.date.localeCompare(a.date)).map(r => `
          <div class="activity-item" onclick="navigate('pmm','${r.pmm_email}')">
            <div class="activity-score" style="background:${scoreBg(r.overall_score/10)};color:${scoreColor(r.overall_score/10)}">
              ${r.overall_score}
            </div>
            <div class="activity-detail">
              <h4>${r.pmm_name} — ${r.title}</h4>
              <p>${r.summary.substring(0, 180)}${r.summary.length > 180 ? '...' : ''}</p>
              <div class="activity-meta">
                <span>${r.date}</span>
                <span>${docTypeLabel(r.doc_type)}</span>
                <span>${r.dimensions_scored} skills assessed</span>
                <span>Project: ${r.campaign_id.replace(/-/g, ' ')}</span>
              </div>
            </div>
          </div>
        `).join('') : '<div class="empty-state"><div class="empty-icon">&#128196;</div><p>No reviews yet. Run your first review to see results here.</p></div>'}
      </div>
    </div>
  `;
  return html;
}

function getTeamAvgImprovement() {
  let total = 0, count = 0;
  DATA.pmms.forEach(p => {
    for (let cat of Object.values(p.running_averages))
      for (let dim of Object.values(cat))
        if (dim.improvement != null) { total += dim.improvement; count++; }
  });
  return count > 0 ? total / count : 0;
}

function findDimName(key) {
  for (let cat of Object.values(DATA.dimensions))
    for (let dim of cat.dims)
      if (dim.key === key) return dim.name;
  return key;
}

function renderPMMProgressCard(pmm) {
  let score = getLatestScore(pmm);
  let v2avg = getV2Avg(pmm);

  // Category bars
  let catBars = '';
  let catKeys = ['A','B','C','D','E'];
  for (let ck of catKeys) {
    let avg = getCatAvg(pmm, ck, 'v2');
    let name = DATA.dimensions[ck]?.name || ck;
    let desc = DATA.dimensions[ck]?.desc || '';
    let bg = avg != null ? scoreColor(avg) : '#e2e8f0';
    catBars += `<div class="ppc-cat-bar" style="background:${bg};opacity:${avg!=null?'1':'0.3'}" title="${name}: ${avg!=null?avg.toFixed(1):'No data'}">
      <div class="ppc-cat-tooltip">${name}: ${avg!=null?avg.toFixed(1)+'/10':'Not yet reviewed'}</div>
    </div>`;
  }

  // Top strengths and growth areas
  let tops = getTopDims(pmm, 2, 'top');
  let bots = getTopDims(pmm, 2, 'bottom');

  let latestCamp = pmm.campaigns.length > 0 ? pmm.campaigns[0] : null;

  return `
    <div class="pmm-progress-card" onclick="navigate('pmm','${pmm.email}')">
      <div class="ppc-top">
        <div>
          <div class="ppc-name">${pmm.name}</div>
          <div class="ppc-role">${pmm.team}</div>
        </div>
        <div class="ppc-score-ring" title="Overall score: ${score||'—'}/100">
          ${scoreRingSvg(score, 64, 5)}
          <div class="ppc-score-num" style="color:${scoreColor(score?score/10:null)}">${score||'—'}</div>
        </div>
      </div>

      <div style="margin-bottom:6px;font-size:11px;color:var(--text-muted);display:flex;justify-content:space-between">
        <span>Skill category overview</span>
        <span>Draft &rarr; Final average: ${v2avg!=null?v2avg+'/10':'—'}</span>
      </div>
      <div class="ppc-categories">${catBars}</div>

      <div class="ppc-meta">
        <div class="ppc-meta-item">
          <div class="ppc-meta-label">Reviews</div>
          <div class="ppc-meta-value">${pmm.total_reviews}</div>
        </div>
        <div class="ppc-meta-item">
          <div class="ppc-meta-label">Projects</div>
          <div class="ppc-meta-value">${pmm.total_campaigns}</div>
        </div>
        <div class="ppc-meta-item">
          <div class="ppc-meta-label">Latest Project</div>
          <div class="ppc-meta-value">${latestCamp ? latestCamp.campaign_id.replace(/-/g,' ') : '—'}</div>
        </div>
        <div class="ppc-meta-item">
          <div class="ppc-meta-label">Member Since</div>
          <div class="ppc-meta-value">${pmm.registered}</div>
        </div>
      </div>

      ${tops.length > 0 || bots.length > 0 ? `
      <div class="ppc-strengths">
        <div class="ppc-strengths-title">Key skills</div>
        ${tops.map(d => `<span class="ppc-tag ppc-tag-green">${d.name} ${d.v2.toFixed(1)}</span>`).join('')}
        ${bots.map(d => `<span class="ppc-tag ${d.v2 < 5 ? 'ppc-tag-red' : 'ppc-tag-amber'}">${d.name} ${d.v2.toFixed(1)}</span>`).join('')}
      </div>` : ''}
    </div>
  `;
}

// ─── PMM DETAIL ─────────────────────────────────────────────────────────────

function renderPMMDetail(email) {
  let pmm = DATA.pmms.find(p => p.email === email);
  if (!pmm) return '<p>Person not found.</p>';
  let reviews = DATA.reviews.filter(r => r.pmm_email === email).sort((a,b) => b.date.localeCompare(a.date));
  let latestScore = getLatestScore(pmm);
  let latestReview = reviews[0];
  let v2avg = getV2Avg(pmm);

  // Count scored dims
  let scoredCount = 0;
  for (let cat of Object.values(pmm.running_averages))
    for (let dim of Object.values(cat))
      if (dim.v2 != null) scoredCount++;

  let html = `
    <div class="back-link" onclick="navigate('home')">&#8592; Back to Team Dashboard</div>
    <div class="page-header">
      <h2>${pmm.name}</h2>
      <p>${pmm.team} &middot; Member since ${pmm.registered}</p>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">Latest Overall Score</div>
        <div style="display:flex;align-items:center;gap:16px;margin-top:8px">
          <div style="position:relative;width:72px;height:72px">
            ${scoreRingSvg(latestScore, 72, 5)}
            <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:22px;font-weight:700;color:${scoreColor(latestScore?latestScore/10:null)}">${latestScore||'—'}</div>
          </div>
          <div>
            <div style="font-size:12px;color:var(--text-muted)">out of 100</div>
            <div style="font-size:12px;color:var(--text-muted);margin-top:2px">${scoredCount} skills assessed</div>
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Average Final Score</div>
        <div class="stat-value" style="color:${scoreColor(v2avg)}">${v2avg!=null?v2avg:'—'}<span style="font-size:14px;color:var(--text-muted)">/10</span></div>
        <div class="stat-sub">Across all reviewed skills</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Reviews Completed</div>
        <div class="stat-value">${pmm.total_reviews}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Projects</div>
        <div class="stat-value">${pmm.total_campaigns}</div>
        <div class="stat-sub">${pmm.campaigns.filter(c=>c.status==='Active').length} active</div>
      </div>
    </div>

    <!-- Focus 3: What to work on -->
    ${latestReview && latestReview.focus_3.length > 0 ? `
    <div class="card mb-6">
      <div class="card-header">
        <h3>What to Work on Next</h3>
        <span class="card-subtitle">From the most recent review (${latestReview.date})</span>
      </div>
      <div class="card-body">
        ${latestReview.focus_3.map((f, i) => `
          <div class="focus-card">
            <div><span class="focus-num">${i+1}</span><h4>${cleanFocusTitle(f.title)}</h4></div>
            ${f.effort ? `<div class="focus-effort">Effort: ${f.effort}</div>` : ''}
            ${f.impact ? `<div class="focus-impact">Expected impact: ${f.impact}</div>` : ''}
          </div>
        `).join('')}
      </div>
    </div>` : ''}

    <!-- Tabs -->
    <div class="tabs" id="pmm-tabs">
      <div class="tab active" onclick="switchTab(this,'overview')">Overview</div>
      <div class="tab" onclick="switchTab(this,'skills')">All Skills</div>
      <div class="tab" onclick="switchTab(this,'projects')">Projects</div>
      <div class="tab" onclick="switchTab(this,'patterns')">Patterns & Notes</div>
    </div>

    <!-- Overview Tab -->
    <div class="tab-content active" id="tab-overview">
      <div class="grid-2">
        <!-- Radar Chart -->
        <div class="card">
          <div class="card-header">
            <h3>Skill Categories</h3>
            <span class="card-subtitle">Draft vs. Final</span>
          </div>
          <div class="card-body radar-wrap" id="radar-chart"></div>
          <div style="padding:0 28px 20px;display:flex;justify-content:center">
            <div class="legend">
              <div class="legend-item"><div class="legend-swatch" style="background:rgba(239,68,68,0.3);border:1.5px dashed #ef4444"></div> First Draft</div>
              <div class="legend-item"><div class="legend-swatch" style="background:rgba(99,102,241,0.3);border:1.5px solid #6366f1"></div> Final Version</div>
            </div>
          </div>
        </div>

        <!-- Top / Bottom skills -->
        <div>
          <div class="card">
            <div class="card-header"><h3>Strongest Skills</h3><span class="card-subtitle">Final version scores</span></div>
            <div class="card-body">
              ${renderTopBottomDims(pmm, 'top', 5)}
            </div>
          </div>
          <div class="card">
            <div class="card-header"><h3>Biggest Growth Opportunities</h3><span class="card-subtitle">Skills with most room to improve</span></div>
            <div class="card-body">
              ${renderTopBottomDims(pmm, 'bottom', 5)}
            </div>
          </div>
        </div>
      </div>

      <!-- Biggest Improvements -->
      <div class="card">
        <div class="card-header"><h3>Biggest Improvements (Draft to Final)</h3><span class="card-subtitle">Skills that improved the most during revision</span></div>
        <div class="card-body">
          ${renderImprovementChart(pmm)}
        </div>
      </div>

      <!-- Latest Review Summary -->
      ${latestReview ? `
      <div class="card">
        <div class="card-header"><h3>Latest Review Summary</h3><span class="card-subtitle">${latestReview.date} — ${latestReview.title}</span></div>
        <div class="card-body">
          <p style="font-size:14px;line-height:1.7;margin-bottom:16px">${latestReview.summary}</p>
          ${latestReview.top_strength ? `<p style="font-size:14px;margin-bottom:8px"><strong>Top strength:</strong> ${latestReview.top_strength}</p>` : ''}
          ${latestReview.top_growth ? `<p style="font-size:14px"><strong>Area to focus on:</strong> ${latestReview.top_growth}</p>` : ''}
        </div>
      </div>` : ''}
    </div>

    <!-- Skills Tab -->
    <div class="tab-content" id="tab-skills">
      ${renderSkillBars(pmm)}
    </div>

    <!-- Projects Tab -->
    <div class="tab-content" id="tab-projects">
      ${renderProjects(pmm, reviews)}
    </div>

    <!-- Patterns Tab -->
    <div class="tab-content" id="tab-patterns">
      ${renderPatterns(pmm)}
    </div>
  `;

  setTimeout(() => renderRadar(pmm), 50);
  return html;
}

function cleanFocusTitle(title) {
  return title.replace(/^\d+\.\s*/, '').replace(/\[.*?\]\s*/, '');
}

function switchTab(el, tabId) {
  el.closest('.tabs').querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  let parent = el.closest('.tabs').parentElement;
  parent.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
  let target = document.getElementById('tab-' + tabId);
  if (target) target.classList.add('active');
  if (tabId === 'overview' && currentPMM) {
    let pmm = DATA.pmms.find(p => p.email === currentPMM);
    if (pmm) setTimeout(() => renderRadar(pmm), 50);
  }
}

function renderTopBottomDims(pmm, dir, count) {
  let dims = getTopDims(pmm, count, dir);
  if (dims.length === 0) return '<p class="text-muted">No skill scores available yet.</p>';
  return dims.map((d, i) => {
    let pct = (d.v2 / 10) * 100;
    let color = scoreColor(d.v2);
    return `<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
      <div style="width:140px;font-size:13px;text-align:right;flex-shrink:0;color:var(--text-primary)">${d.name}</div>
      <div style="flex:1;height:24px;background:#f1f5f9;border-radius:6px;overflow:hidden">
        <div style="width:${pct}%;height:100%;background:${color};border-radius:6px;transition:width 0.6s"></div>
      </div>
      <div style="width:40px;font-size:14px;font-weight:700;color:${color}">${d.v2.toFixed(1)}</div>
    </div>`;
  }).join('');
}

function renderImprovementChart(pmm) {
  let all = [];
  for (let cat of Object.values(pmm.running_averages))
    for (let dim of Object.values(cat))
      if (dim.improvement != null && dim.improvement > 0)
        all.push({name: dim.name, imp: dim.improvement, v1: dim.v1, v2: dim.v2});
  all.sort((a,b) => b.imp - a.imp);
  let top = all.slice(0, 8);
  if (top.length === 0) return '<p class="text-muted">No improvement data available yet.</p>';

  let maxImp = Math.max(...top.map(d => d.imp));
  return top.map(d => {
    let pct = (d.imp / maxImp) * 100;
    return `<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
      <div style="width:160px;font-size:13px;text-align:right;flex-shrink:0">${d.name}</div>
      <div style="flex:1;height:28px;background:#f0fdf4;border-radius:6px;overflow:hidden;position:relative">
        <div style="width:${pct}%;height:100%;background:#10b981;border-radius:6px;display:flex;align-items:center;justify-content:flex-end;padding-right:8px;color:#fff;font-size:12px;font-weight:600;min-width:50px">
          +${d.imp.toFixed(1)}
        </div>
      </div>
      <div style="width:80px;font-size:12px;color:var(--text-muted);flex-shrink:0">${d.v1?.toFixed(1)||'?'} &rarr; ${d.v2?.toFixed(1)||'?'}</div>
    </div>`;
  }).join('');
}

function renderSkillBars(pmm) {
  let html = '';
  for (let [catKey, catData] of Object.entries(DATA.dimensions)) {
    let catScores = pmm.running_averages[catKey] || {};
    let catAvgV2 = getCatAvg(pmm, catKey, 'v2');

    html += `<div class="bar-group">
      <div class="bar-group-title">${catData.name}
        <span class="bar-group-subtitle">${catData.desc}${catAvgV2 != null ? ' — Category average: ' + catAvgV2.toFixed(1) + '/10' : ''}</span>
      </div>`;

    for (let dim of catData.dims) {
      let score = catScores[dim.key];
      let v1 = score ? score.v1 : null;
      let v2 = score ? score.v2 : null;
      let imp = score ? score.improvement : null;
      let v2Pct = v2 != null ? (v2/10*100) : 0;
      let v1Pct = v1 != null ? (v1/10*100) : 0;

      html += `<div class="bar-row">
        <div class="bar-label">${dim.name}</div>
        <div class="bar-track" title="${dim.name}: Draft ${v1!=null?v1.toFixed(1):'—'} → Final ${v2!=null?v2.toFixed(1):'—'}">
          ${v1 != null ? `<div class="bar-v1" style="width:${v1Pct}%;background:${scoreColor(v1)}"></div>` : ''}
          ${v2 != null ? `<div class="bar-fill" style="width:${v2Pct}%;background:${scoreColor(v2)}"><span class="bar-fill-inner">${v2.toFixed(1)}</span></div>` : '<div style="padding:6px 12px;color:var(--text-muted);font-size:12px">Not yet reviewed</div>'}
        </div>
        <div class="bar-delta">${imp != null ? changeHtml(imp) : '<span style="color:var(--text-muted)">—</span>'}</div>
      </div>`;
    }
    html += '</div>';
  }

  return `<div class="card"><div class="card-header"><h3>All Skills — Draft vs. Final Scores</h3>
    <span class="card-subtitle">Faded bar = first draft, solid bar = final version, number = improvement</span>
  </div><div class="card-body">${html}</div></div>`;
}

function renderProjects(pmm, reviews) {
  if (pmm.campaigns.length === 0) return '<div class="empty-state"><div class="empty-icon">&#128194;</div><p>No projects yet.</p></div>';

  let html = '';
  for (let camp of pmm.campaigns) {
    let campReviews = reviews.filter(r => r.campaign_id === camp.campaign_id);
    let statusCls = camp.status === 'Active' ? 'status-active' : 'status-complete';

    html += `<div class="campaign-card">
      <div class="cc-header">
        <div>
          <div class="cc-title">${camp.campaign_id.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</div>
          <div class="cc-type">${docTypeLabel(camp.doc_type)} &middot; ${camp.period}</div>
        </div>
        <span class="cc-status ${statusCls}">${camp.status}</span>
      </div>

      ${camp.iterations.length > 0 ? `
        <table class="data-table" style="font-size:13px">
          <thead><tr>
            <th>Round</th><th>Date</th><th>Score</th><th>Best Improvement</th>
          </tr></thead>
          <tbody>${camp.iterations.map(iter => `<tr>
            <td>Round ${iter.Iter || iter.iter || '?'}</td>
            <td>${iter.Date || iter.date || '—'}</td>
            <td style="font-weight:600">${iter.Overall || iter.overall || '—'}</td>
            <td>${iter['Top Improvement'] || iter.top_improvement || '—'}</td>
          </tr>`).join('')}</tbody>
        </table>
      ` : ''}

      ${camp.starting_quality ? `<div class="cc-summary">Starting quality: ${camp.starting_quality}</div>` : ''}

      ${campReviews.length > 0 ? campReviews.map(r => `
        <div class="cc-summary" style="margin-top:12px">
          <strong>Review summary:</strong> ${r.summary.substring(0, 250)}${r.summary.length > 250 ? '...' : ''}
        </div>
      `).join('') : ''}
    </div>`;
  }
  return html;
}

function renderPatterns(pmm) {
  let html = '';

  let sections = [
    {key: 'strengths', title: 'Consistent Strengths', subtitle: 'Skills that are reliably strong', cls: 'pat-strength', dot: 'var(--success)'},
    {key: 'weaknesses', title: 'Persistent Weaknesses', subtitle: 'Skills that need focused attention', cls: 'pat-weakness', dot: 'var(--danger)'},
    {key: 'growth_areas', title: 'Growth Areas', subtitle: 'Skills showing improvement over time', cls: 'pat-growth', dot: 'var(--warning)'},
    {key: 'draft_stage_strengths', title: 'Internalized Skills', subtitle: 'Skills that are strong even in first drafts — meaning the learning has stuck', cls: 'pat-strength', dot: 'var(--success)'},
    {key: 'persistent_feedback_gaps', title: 'Recurring Feedback Gaps', subtitle: 'Feedback given multiple times that hasn\'t been addressed yet', cls: 'pat-weakness', dot: 'var(--danger)'},
  ];

  let hasContent = false;
  for (let sec of sections) {
    let items = pmm.patterns[sec.key] || [];
    if (items.length === 0 || (items.length === 1 && items[0].toLowerCase().includes('insufficient'))) continue;
    if (items.length === 1 && items[0].toLowerCase().startsWith('none')) continue;
    hasContent = true;
    html += `<div class="pattern-section">
      <h4><span class="pattern-dot" style="background:${sec.dot}"></span> ${sec.title}</h4>
      <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px;margin-left:16px">${sec.subtitle}</p>
      <ul class="pattern-list">${items.map(item => `<li class="${sec.cls}">${item.replace(/\*\*/g, '')}</li>`).join('')}</ul>
    </div>`;
  }

  if (!hasContent) {
    html += '<div class="empty-state"><div class="empty-icon">&#128202;</div><p>Patterns emerge after 2+ projects. Keep reviewing to build a picture of this person\'s strengths and growth areas.</p></div>';
  }

  // Notes
  if (pmm.notes.length > 0) {
    html += `<div class="card mt-6">
      <div class="card-header"><h3>Notes & History</h3></div>
      <div class="card-body">
        ${pmm.notes.map(n => `<div style="padding:10px 0;border-bottom:1px solid var(--border);font-size:13px;line-height:1.6;color:var(--text-secondary)">${n}</div>`).join('')}
      </div>
    </div>`;
  }

  return html;
}

// ─── RADAR CHART ────────────────────────────────────────────────────────────

function renderRadar(pmm) {
  let el = document.getElementById('radar-chart');
  if (!el) return;

  let cats = Object.entries(DATA.dimensions).map(([key, cat]) => ({
    key, name: cat.name,
    v1: getCatAvg(pmm, key, 'v1') || 0,
    v2: getCatAvg(pmm, key, 'v2') || 0,
  }));

  let w = 380, h = 380, cx = w/2, cy = h/2, R = 140, n = cats.length;
  let svg = `<svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" style="max-width:100%">`;

  // Grid rings
  for (let ring = 2; ring <= 10; ring += 2) {
    let rr = (ring/10)*R;
    let pts = [];
    for (let i = 0; i < n; i++) {
      let a = (i*2*Math.PI/n) - Math.PI/2;
      pts.push(`${cx+rr*Math.cos(a)},${cy+rr*Math.sin(a)}`);
    }
    svg += `<polygon points="${pts.join(' ')}" fill="none" stroke="#e2e8f0" stroke-width="1"/>`;
    if (ring % 4 === 0) svg += `<text x="${cx+4}" y="${cy - rr + 4}" fill="#94a3b8" font-size="10" font-weight="500">${ring}</text>`;
  }

  // Axes
  for (let i = 0; i < n; i++) {
    let a = (i*2*Math.PI/n) - Math.PI/2;
    svg += `<line x1="${cx}" y1="${cy}" x2="${cx+R*Math.cos(a)}" y2="${cy+R*Math.sin(a)}" stroke="#e2e8f0" stroke-width="1"/>`;
    let lx = cx + (R+28)*Math.cos(a), ly = cy + (R+28)*Math.sin(a);
    let anchor = Math.abs(Math.cos(a))<0.1 ? 'middle' : Math.cos(a)>0 ? 'start' : 'end';
    // Wrap long names
    let name = cats[i].name;
    svg += `<text x="${lx}" y="${ly}" text-anchor="${anchor}" dominant-baseline="middle" fill="#475569" font-size="11" font-weight="600">${name}</text>`;
  }

  // V1 polygon (draft)
  let v1pts = cats.map((c,i) => {
    let a = (i*2*Math.PI/n)-Math.PI/2, r = (c.v1/10)*R;
    return `${cx+r*Math.cos(a)},${cy+r*Math.sin(a)}`;
  }).join(' ');
  svg += `<polygon points="${v1pts}" fill="rgba(239,68,68,0.08)" stroke="#ef4444" stroke-width="2" stroke-dasharray="6,3"/>`;

  // V2 polygon (final)
  let v2pts = cats.map((c,i) => {
    let a = (i*2*Math.PI/n)-Math.PI/2, r = (c.v2/10)*R;
    return `${cx+r*Math.cos(a)},${cy+r*Math.sin(a)}`;
  }).join(' ');
  svg += `<polygon points="${v2pts}" fill="rgba(99,102,241,0.12)" stroke="#6366f1" stroke-width="2.5"/>`;

  // Data dots
  cats.forEach((c,i) => {
    let a = (i*2*Math.PI/n)-Math.PI/2;
    let r2 = (c.v2/10)*R;
    svg += `<circle cx="${cx+r2*Math.cos(a)}" cy="${cy+r2*Math.sin(a)}" r="4" fill="#6366f1"/>`;
  });

  svg += '</svg>';
  el.innerHTML = svg;
}

// ─── SKILLS MAP (HEATMAP) ───────────────────────────────────────────────────

function renderSkillsMap() {
  let pmms = DATA.pmms;

  let html = `
    <div class="page-header">
      <h2>Team Skills Map</h2>
      <p>Compare final-version scores across the team. Each cell shows how well that person performed on that skill. Darker green = stronger. Use this to spot team-wide strengths and coaching opportunities.</p>
    </div>

    <div class="card">
      <div class="card-body heatmap-wrap">
        <table class="heatmap">
          <thead><tr>
            <th>Skill</th>
            ${pmms.map(p => `<th style="cursor:pointer" onclick="navigate('pmm','${p.email}')">${p.name.split(' ')[0]}</th>`).join('')}
            <th>Team Average</th>
          </tr></thead>
          <tbody>
  `;

  for (let [catKey, catData] of Object.entries(DATA.dimensions)) {
    html += `<tr class="cat-row"><td colspan="${pmms.length+2}">${catData.name} — ${catData.desc}</td></tr>`;
    for (let dim of catData.dims) {
      let teamVals = [];
      html += `<tr><td>${dim.name}</td>`;
      for (let pmm of pmms) {
        let cat = pmm.running_averages[catKey] || {};
        let score = cat[dim.key];
        let v2 = score ? score.v2 : null;
        if (v2 != null) teamVals.push(v2);
        html += `<td class="heat" style="background:${heatBg(v2)};color:${heatFg(v2)}">${v2!=null?v2.toFixed(1):'—'}</td>`;
      }
      let avg = teamVals.length>0 ? teamVals.reduce((a,b)=>a+b,0)/teamVals.length : null;
      html += `<td class="heat" style="background:${heatBg(avg)};color:${heatFg(avg)};font-weight:700">${avg!=null?avg.toFixed(1):'—'}</td></tr>`;
    }
  }

  html += '</tbody></table></div></div>';

  // Legend
  html += `<div class="card mt-4"><div class="card-body">
    <div class="legend">
      <span style="font-size:12px;font-weight:600;color:var(--text-secondary);margin-right:4px">Score guide:</span>
      ${[
        {s:2,l:'Needs work (0–3.5)'},{s:4.5,l:'Developing (3.5–5.5)'},{s:6,l:'Solid (5.5–6.5)'},
        {s:7,l:'Strong (6.5–7.5)'},{s:8,l:'Very strong (7.5–8.5)'},{s:9,l:'Exceptional (8.5–10)'}
      ].map(x => `<div class="legend-item"><div class="legend-swatch" style="background:${heatBg(x.s)}"></div>${x.l}</div>`).join('')}
    </div>
  </div></div>`;

  return html;
}

// ─── Init ───────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => { navigate('home'); });
"""


def generate_html(data_json: str) -> str:
    js_with_data = JS.replace("__DATA_PLACEHOLDER__", data_json)

    pmms_nav_script = r"""
    <script>
    (function() {
      let nav = document.getElementById('pmm-nav-list');
      DATA.pmms.forEach(p => {
        let score = null;
        let reviews = DATA.reviews.filter(r => r.pmm_email === p.email);
        if (reviews.length > 0) {
          reviews.sort((a,b) => b.date.localeCompare(a.date));
          score = reviews[0].overall_score;
        }
        let li = document.createElement('li');
        li.innerHTML = `<a id="nav-pmm-${p.email}" onclick="navigate('pmm','${p.email}')">
          <span class="nav-icon">&#9679;</span>
          <span>${p.name}</span>
          ${score ? `<span class="nav-badge">${score}</span>` : ''}
        </a>`;
        nav.appendChild(li);
      });
    })();
    </script>
    """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Master Reviewer — Team Dashboard</title>
  <style>{CSS}</style>
</head>
<body>
  <nav class="sidebar">
    <div class="sidebar-brand">
      <h1>Master Reviewer</h1>
      <p>Writing Quality Tracker</p>
    </div>
    <div class="sidebar-divider"></div>

    <div class="sidebar-section">Views</div>
    <ul class="sidebar-nav">
      <li><a id="nav-home" class="active" onclick="navigate('home')">
        <span class="nav-icon">&#9632;</span>
        <span>Team Dashboard</span>
      </a></li>
      <li><a id="nav-skills" onclick="navigate('skills')">
        <span class="nav-icon">&#9638;</span>
        <span>Team Skills Map</span>
      </a></li>
    </ul>

    <div class="sidebar-section">Team Members</div>
    <ul class="sidebar-nav" id="pmm-nav-list"></ul>
  </nav>

  <main id="content"><p>Loading...</p></main>

  <script>{js_with_data}</script>
  {pmms_nav_script}
</body>
</html>"""


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    base_dir = Path(__file__).parent.parent

    pmms = []
    pmm_dir = base_dir / "pmms"
    if pmm_dir.exists():
        for f in sorted(pmm_dir.glob("*.md")):
            try:
                pmms.append(parse_pmm_profile(f))
            except Exception as e:
                print(f"  Warning: Could not parse {f.name}: {e}")

    reviews = []
    review_dir = base_dir / "reviews"
    if review_dir.exists():
        for f in sorted(review_dir.glob("*.md")):
            try:
                reviews.append(parse_review(f))
            except Exception as e:
                print(f"  Warning: Could not parse {f.name}: {e}")

    print(f"Parsed {len(pmms)} PMM profiles and {len(reviews)} reviews.")

    data = serialize_data(pmms, reviews)
    data_json = json.dumps(data, indent=None)

    html = generate_html(data_json)
    output_path = base_dir / "dashboard" / "index.html"
    output_path.write_text(html)
    print(f"Dashboard generated: {output_path}")
    print(f"Open in browser: file://{output_path.resolve()}")


if __name__ == "__main__":
    main()

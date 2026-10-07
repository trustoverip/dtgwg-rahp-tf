#!/usr/bin/env python3
"""
build.py — generate every derived view from the canonical YAML in data/.

Nothing in build/ is edited by hand. If a fact is wrong in a generated view,
fix it in data/ and run this again.

Outputs:
    build/rahp.json           single JSON bundle of every record
    build/jsonld/*.jsonld     JSON-LD per record type, with resolvable RAHP identifiers
    build/derived/            computed cross-references (persona xrefs, coverage rankings)
    build/site/               the HTML reference site
    build/normative.md        the standards action set — every normative candidate in one list

Usage:
    python3 tools/build.py [--out build]
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import sys
from collections import defaultdict

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("build.py requires PyYAML: pip install -r requirements.txt")

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE_IRI = "https://trustoverip.github.io/dtgwg-rahp-tf/id/"

SEV_SCORE = {"High": 3, "Medium": 2, "Low": 1}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_all(data_dir, instance):
    out = {}
    for ns, spec in instance["namespaces"].items():
        p = data_dir / spec["file"]
        doc = load(p) if p.exists() else {}
        out[spec["record_type"]] = (doc or {}).get("records") or []
    return out


# ---------------------------------------------------------------------------
# derived data
# ---------------------------------------------------------------------------

def risk_score(r):
    if r.get("severity") == "Critical":
        return None
    s = SEV_SCORE.get(r.get("severity"))
    l = SEV_SCORE.get(r.get("likelihood"))
    return s * l if s and l else None


def derive_persona_xrefs(records):
    """Persona cross-references are COMPUTED, never stored. This is what removes
    the class of error that produced the column-shift in the v6 workbook."""
    x = defaultdict(lambda: {"user_stories": set(), "scenarios": set(),
                             "epics": set(), "metrics": set(), "risks": set()})
    for us in records["user_story"]:
        if us.get("persona"):
            x[us["persona"]]["user_stories"].add(us["id"])
            x[us["persona"]]["metrics"].update(us.get("metrics") or [])
    for sc in records["scenario"]:
        for p in (sc.get("legitimate_personas") or []) + (sc.get("adversarial_personas") or []):
            x[p]["scenarios"].add(sc["id"])
            x[p]["metrics"].update(sc.get("metrics") or [])
    for ep in records["epic"]:
        for p in ep.get("personas") or []:
            x[p]["epics"].add(ep["id"])
    for m in records["metric"]:
        for p in (m.get("personas_want_high") or []) + (m.get("personas_want_suppressed") or []):
            x[p]["metrics"].add(m["id"])
    # risks reach personas via user stories and scenarios
    us_persona = {u["id"]: u.get("persona") for u in records["user_story"]}
    sc_personas = {s["id"]: (s.get("legitimate_personas") or []) + (s.get("adversarial_personas") or [])
                   for s in records["scenario"]}
    for r in records["risk"]:
        for u in r.get("user_stories") or []:
            if us_persona.get(u):
                x[us_persona[u]]["risks"].add(r["id"])
        for s in r.get("scenarios") or []:
            for p in sc_personas.get(s, []):
                x[p]["risks"].add(r["id"])
    return {k: {kk: sorted(vv) for kk, vv in v.items()} for k, v in sorted(x.items())}


def derive_coverage(records):
    """Which controls and guardrails cover the most High-severity risks."""
    risks = {r["id"]: r for r in records["risk"]}

    def rank(items, field):
        out = []
        for it in items:
            linked = it.get(field) or []
            highs = [r for r in linked if risks.get(r, {}).get("severity") in ("High", "Critical")]
            out.append({"id": it["id"], "name": it.get("name"),
                        "total_risks": len(linked), "high_risks": len(highs),
                        "risks": linked})
        out.sort(key=lambda d: (-d["high_risks"], -d["total_risks"], d["id"]))
        return out

    return {
        "controls": rank(records["control"], "linked_risks"),
        "guardrails": rank(records["guardrail"], "risks_addressed"),
    }


def derive_normative_set(records):
    """The standards action set: everything proposed for normative text, plus
    everything that is must_address and has no status assigned yet."""
    out = {"assigned": [], "awaiting_triage": []}
    for kind in ("control", "guardrail"):
        for it in records[kind]:
            entry = {"id": it["id"], "kind": kind, "name": it.get("name"),
                     "status": it.get("standards_status"),
                     "normative_language": it.get("normative_language")}
            if it.get("standards_status") in (None, "unassigned"):
                out["awaiting_triage"].append(entry)
            else:
                out["assigned"].append(entry)
    return out


# ---------------------------------------------------------------------------
# JSON-LD
# ---------------------------------------------------------------------------

TYPE_MAP = {
    "risk": "Risk", "control": "Control", "guardrail": "Guardrail",
    "assurance_test": "AssuranceTest", "metric": "Metric", "user_story": "UserStory",
    "scenario": "Scenario", "epic": "Epic", "persona": "Persona",
    "recommendation": "Recommendation", "risk_acceptance": "RiskAcceptance",
    "governance_precedent": "GovernancePrecedent",
}

CAMEL = {
    "affected_metrics": "affectedMetrics", "assurance_tests": "assuranceTests",
    "linked_risks": "linkedRisks", "risks_addressed": "risksAddressed",
    "risks_measured": "risksMeasured", "user_stories": "userStories",
    "standards_priority": "standardsPriority", "standards_status": "standardsStatus",
    "normative_language": "normativeLanguage", "lifecycle_phase": "lifecyclePhase",
    "harm_types": "harmType", "personas_want_high": "personasWantHigh",
    "personas_want_suppressed": "personasWantSuppressed", "risk_id": "riskId",
    "decision_date": "decisionDate", "review_date": "reviewDate",
    "superseded_by": "supersededBy",
}

IRI_FIELDS = {
    "affectedMetrics", "guardrails", "controls", "assuranceTests", "linkedRisks",
    "risksAddressed", "risksMeasured", "userStories", "scenarios", "epics",
    "personas", "personasWantHigh", "personasWantSuppressed", "riskId",
    "supersededBy", "linked_guardrails", "linked_controls", "metrics", "persona",
    "legitimate_personas", "adversarial_personas",
}


def to_jsonld(rtype, records):
    graph = []
    for rec in records:
        node = {"@id": BASE_IRI + rec["id"], "@type": TYPE_MAP[rtype]}
        for k, v in rec.items():
            if k == "id" or v is None or v == [] or v == {}:
                continue
            key = CAMEL.get(k, k)
            if key in IRI_FIELDS:
                v = [BASE_IRI + x for x in v] if isinstance(v, list) else BASE_IRI + v
            node[key] = v
        if rtype == "risk":
            score = risk_score(rec)
            if score is not None:
                node["riskScore"] = score
        graph.append(node)
    return {"@context": "../../context/rahp.jsonld", "@graph": graph}


# ---------------------------------------------------------------------------
# site
# ---------------------------------------------------------------------------

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#f6f5f1;--surface:#fff;--surface2:#fafaf8;--border:#e6e3db;--border2:#d4d0c6;
--text:#18170f;--muted:#6b6860;--faint:#a8a49a;--blue:#1a47b8;--blue-bg:#eef1fb;--blue-dark:#0e2e7a;
--teal:#0a7560;--teal-bg:#e6f5f1;--amber:#9a4a00;--amber-bg:#fdf2e3;--plum:#5b1fb5;--plum-bg:#f0eafb;
--plum-dark:#3b0f7a;--red:#b82020;--red-bg:#fdf0ee;--green:#145228;--green-bg:#edf7f0;
--font:'DM Sans',system-ui,-apple-system,sans-serif;--mono:'DM Mono',ui-monospace,monospace;
--r:8px;--rl:14px;--sh:0 1px 3px rgba(0,0,0,.06)}
body{font-family:var(--font);font-size:14px;line-height:1.6;color:var(--text);background:var(--bg)}
.layout{display:flex;min-height:100vh}
.sidebar{width:228px;min-width:228px;background:var(--surface);border-right:1px solid var(--border);
position:sticky;top:0;height:100vh;overflow-y:auto;display:flex;flex-direction:column}
.sb-brand{padding:22px 20px 18px;border-bottom:1px solid var(--border)}
.sb-wordmark{font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);display:block;margin-bottom:3px}
.sb-project{font-size:15px;font-weight:600;line-height:1.3}
.nav-group{padding:16px 20px 4px;font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}
.nav-a{display:flex;align-items:center;gap:9px;padding:8px 20px;font-size:13px;color:var(--muted);
text-decoration:none;border-left:2px solid transparent}
.nav-a:hover{background:var(--bg);color:var(--text)}
.nav-a.on{background:var(--bg);color:var(--text);font-weight:500;border-left-color:var(--text)}
.nav-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.sb-foot{margin-top:auto;padding:14px 20px;border-top:1px solid var(--border);font-size:11px;color:var(--faint);line-height:1.7}
.main{flex:1;max-width:calc(100vw - 228px)}
.ph{padding:30px 40px 22px;border-bottom:1px solid var(--border);background:var(--surface)}
.ph h1{font-size:22px;font-weight:600;letter-spacing:-.3px;margin-bottom:5px}
.ph-sub{font-size:14px;color:var(--muted);max-width:720px}
.gen{margin-top:10px;font-size:11px;font-family:var(--mono);color:var(--faint)}
.content{padding:28px 40px 60px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--rl);overflow:hidden;margin-bottom:20px}
.cb{padding:20px}
.sh2{display:flex;align-items:baseline;gap:10px;margin:26px 0 14px}
.sh2 h2{font-size:16px;font-weight:600}
.sh2 .cnt{font-size:12px;color:var(--faint);font-family:var(--mono)}
table{width:100%;border-collapse:collapse;font-size:13px}
th{font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);
padding:10px 12px;text-align:left;border-bottom:2px solid var(--border);background:var(--surface2);white-space:nowrap}
td{padding:11px 12px;border-bottom:1px solid var(--border);vertical-align:top}
tr:hover td{background:var(--bg)}
.pill{display:inline-flex;align-items:center;padding:2px 7px;border-radius:20px;font-size:11px;
font-weight:500;font-family:var(--mono);white-space:nowrap;margin:1px 2px 1px 0}
.prk{background:var(--red-bg);color:var(--red)}
.pct{background:#f0f4ff;color:#2d4da0}
.pgr{background:var(--amber-bg);color:var(--amber)}
.pat{background:#f5f0ff;color:var(--plum-dark)}
.pm{background:var(--plum-bg);color:var(--plum)}
.pu{background:var(--blue-bg);color:var(--blue-dark)}
.psc{background:var(--teal-bg);color:var(--teal)}
.sev-Critical{background:#2d0a0a;color:#fff}
.sev-High{background:var(--red-bg);color:var(--red)}
.sev-Medium{background:var(--amber-bg);color:var(--amber)}
.sev-Low{background:var(--green-bg);color:var(--green)}
.score{display:inline-block;font-family:var(--mono);font-size:13px;font-weight:600;padding:2px 10px;border-radius:6px}
.fbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:16px}
.finput,.fsel{padding:8px 12px;border:1px solid var(--border);border-radius:var(--r);font-size:13px;
font-family:var(--font);background:var(--surface);color:var(--text);outline:none}
.pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));gap:16px}
.pcard{background:var(--surface);border:1px solid var(--border);border-radius:var(--rl);padding:18px}
.pcard h3{font-size:15px;font-weight:600;margin-bottom:2px}
.pcard .role{font-size:12px;color:var(--muted);margin-bottom:10px}
.pcard .quote{font-size:12px;font-style:italic;color:var(--muted);border-left:2px solid var(--border2);
padding-left:9px;margin-bottom:12px;line-height:1.5}
.lab{font-size:10px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;color:var(--faint);margin:10px 0 4px}
.tagbar{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px}
.tag{font-size:10px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;padding:2px 8px;border-radius:4px}
.t-legit{background:var(--blue-bg);color:var(--blue-dark)}
.t-machine{background:var(--teal-bg);color:var(--teal)}
.t-bad{background:var(--red-bg);color:var(--red)}
.t-edge{background:var(--amber-bg);color:var(--amber)}
.t-safe{background:#2d0a0a;color:#fff}
.warnbox{background:var(--amber-bg);border-left:3px solid var(--amber);padding:12px 14px;border-radius:var(--r);
font-size:12px;color:#5c2c00;margin-bottom:14px}
.gapbox{background:var(--amber-bg);border-left:3px solid var(--amber);padding:10px 13px;border-radius:var(--r);
font-size:12px;margin:8px 0}
.gapbox.blocking{background:var(--red-bg);border-left-color:var(--red)}
.stage{border:1px solid var(--border);border-radius:var(--rl);background:var(--surface);padding:20px;margin-bottom:16px}
.stage h3{font-size:15px;margin-bottom:4px}
.stage .sum{font-size:13px;color:var(--muted);margin-bottom:12px}
.kv{display:grid;grid-template-columns:150px 1fr;gap:6px 14px;font-size:12px;margin-bottom:10px}
.kv dt{color:var(--faint);font-weight:500}
small.mono{font-family:var(--mono);font-size:11px;color:var(--faint)}
@media(max-width:820px){.sidebar{display:none}.main{max-width:100vw}.content,.ph{padding:16px}}
"""

NAV = [
    ("index.html", "Personas", "var(--blue)"),
    ("risks.html", "Risks & Metrics", "var(--red)"),
    ("normative.html", "Standards pipeline", "var(--plum)"),
    ("matrix.html", "Cross-reference matrix", "var(--teal)"),
    ("lifecycle.html", "Lifecycle & gaps", "var(--amber)"),
    ("governance.html", "Decisions & acceptances", "var(--green)"),
]


def page(current, title, subtitle, body, meta):
    nav = "".join(
        f'<a href="{href}" class="nav-a{" on" if href == current else ""}">'
        f'<span class="nav-dot" style="background:{colour}"></span>{label}</a>'
        for href, label, colour in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — DTG RAHP</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div class="layout">
<aside class="sidebar">
  <div class="sb-brand"><span class="sb-wordmark">DTG RAHP</span>
  <span class="sb-project">Risk &amp; Harm Prevention</span></div>
  <nav style="padding:10px 0"><div class="nav-group">Navigate</div>{nav}</nav>
  <div class="sb-foot">Toolkit {html.escape(meta['toolkit_version'])}<br>
  Spec {html.escape(meta['spec_version'])} · {html.escape(meta['maintainer'])}<br>
  <em>Generated — do not edit</em></div>
</aside>
<main class="main">
<div class="ph"><h1>{html.escape(title)}</h1><p class="ph-sub">{subtitle}</p>
<p class="gen">generated by tools/build.py from data/ · {meta['counts']}</p></div>
<div class="content">{body}</div>
</main></div></body></html>"""


def pill(idv):
    cls = ("prk" if idv.startswith("RK") else "pct" if idv.startswith("CT")
           else "pgr" if idv.startswith("GR") else "pat" if idv.startswith("AT")
           else "pm" if idv.startswith("M-") else "pu" if idv.startswith("US")
           else "psc" if idv.startswith("SC") else "pm")
    return f'<span class="pill {cls}">{html.escape(idv)}</span>'


def pills(ids):
    return "".join(pill(i) for i in ids) or '<span style="color:var(--faint)">—</span>'


def build_single_file(pages, meta, out):
    """One self-contained HTML file containing every view as a tab. For sharing by
    email or attaching to a working group agenda, where a folder of linked pages
    is awkward."""
    tabs = "".join(
        f'<button class="tabbtn{" on" if i == 0 else ""}" onclick="showTab(\'{k}\',this)">{t}</button>'
        for i, (k, t, _, _) in enumerate(pages))
    panes = "".join(
        f'<section id="pane-{k}" class="pane{" on" if i == 0 else ""}">'
        f'<div class="ph"><h1>{html.escape(t)}</h1><p class="ph-sub">{s}</p>'
        f'<p class="gen">generated by tools/build.py from data/ · {meta["counts"]}</p></div>'
        f'<div class="content">{b}</div></section>'
        for i, (k, t, s, b) in enumerate(pages))
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DTG RAHP Toolkit {html.escape(meta['toolkit_version'])}</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}
.tabbar{{display:flex;gap:3px;padding:10px 40px 0;background:var(--surface);
border-bottom:1px solid var(--border);flex-wrap:wrap;position:sticky;top:0;z-index:20}}
.tabbtn{{padding:9px 15px;border:none;background:none;border-bottom:2px solid transparent;
font-size:13px;font-weight:500;color:var(--muted);cursor:pointer;font-family:var(--font)}}
.tabbtn:hover{{color:var(--text)}}
.tabbtn.on{{color:var(--text);border-bottom-color:var(--text)}}
.pane{{display:none}}.pane.on{{display:block}}
.masthead{{padding:20px 40px 14px;background:var(--surface)}}
.masthead .w{{font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}}
.masthead h2{{font-size:19px;font-weight:600}}
@media(max-width:820px){{.tabbar,.masthead{{padding-left:16px;padding-right:16px}}}}
</style></head><body>
<div class="masthead"><div class="w">DTG RAHP</div><h2>Risk &amp; Harm Prevention Toolkit
<span style="font-size:12px;font-weight:400;color:var(--faint);font-family:var(--mono)">
{html.escape(meta['toolkit_version'])} · spec {html.escape(meta['spec_version'])}</span></h2></div>
<div class="tabbar">{tabs}</div>
{panes}
<script>
function showTab(k,btn){{
  document.querySelectorAll('.pane').forEach(p=>p.classList.remove('on'));
  document.querySelectorAll('.tabbtn').forEach(b=>b.classList.remove('on'));
  document.getElementById('pane-'+k).classList.add('on');
  btn.classList.add('on');
  window.scrollTo(0,0);
}}
</script></body></html>"""
    path = out / "rahp-toolkit.html"
    path.write_text(doc, encoding="utf-8")
    return path


def build_site(records, derived, meta, out):
    site = out / "site"
    site.mkdir(parents=True, exist_ok=True)
    pages = []
    xref = derived["persona_xrefs"]

    # ---- personas -------------------------------------------------------
    tag_cls = {"legitimate_user": ("t-legit", "Legitimate user"),
               "machine_agent": ("t-machine", "Machine agent"),
               "bad_actor": ("t-bad", "Bad actor"),
               "edge_case": ("t-edge", "Extreme user")}
    cards = []
    for p in records["persona"]:
        cls, lbl = tag_cls.get(p.get("type"), ("t-legit", p.get("type", "")))
        tags = f'<span class="tag {cls}">{lbl}</span>'
        if p.get("safeguarding"):
            tags += '<span class="tag t-safe">Safeguarding</span>'
        x = xref.get(p["id"], {})
        sg = (f'<div class="warnbox"><strong>Safeguarding note.</strong> '
              f'{html.escape(p["safeguarding_note"])}</div>') if p.get("safeguarding_note") else ""
        ev = "".join(
            f'<li style="font-size:11px;color:var(--muted);margin-bottom:5px">{html.escape(e["claim"])} '
            f'<a href="{html.escape(e.get("url", "#"))}" style="color:var(--blue)">{html.escape(e["source"])}</a></li>'
            for e in p.get("evidence") or [])
        cards.append(f"""<div class="pcard">
<div class="tagbar">{tags}</div>
<h3>{html.escape(p['name'])} <small class="mono">{html.escape(p['id'])}</small></h3>
<div class="role">{html.escape(p['role'])}</div>
{f'<div class="quote">{html.escape(p["quote"])}</div>' if p.get('quote') else ''}
{sg}
<div class="lab">Risks reaching this persona</div><div>{pills(x.get('risks', []))}</div>
<div class="lab">User stories</div><div>{pills(x.get('user_stories', []))}</div>
<div class="lab">Scenarios</div><div>{pills(x.get('scenarios', []))}</div>
<div class="lab">Metrics</div><div>{pills(x.get('metrics', [])[:14])}</div>
{f'<div class="lab">Evidence</div><ul style="padding-left:16px">{ev}</ul>' if ev else ''}
</div>""")
    body = ('<p style="margin-bottom:18px;color:var(--muted);max-width:760px">Personas are analytical '
            'instruments, not marketing profiles. Every cross-reference on these cards is computed from '
            'the user story, scenario, EPIC and metric records at build time — it cannot drift out of '
            'step with them.</p>'
            f'<div class="pgrid">{"".join(cards)}</div>')
    ptitle, psub = "Personas", "Who participates, who is exposed, and who attacks — including the extreme users who define the requirements."
    (site / "index.html").write_text(page("index.html", ptitle, psub, body, meta), encoding="utf-8")
    pages.append(("personas", ptitle, psub, body))

    # ---- risks ----------------------------------------------------------
    rows = []
    for r in sorted(records["risk"], key=lambda x: (-(risk_score(x) or 99), x["id"])):
        sc = risk_score(r)
        badge = ('<span class="score sev-Critical">CRIT</span>' if sc is None
                 else f'<span class="score sev-{"High" if sc >= 6 else "Medium" if sc >= 3 else "Low"}">{sc}</span>')
        rows.append(f"""<tr>
<td>{pill(r['id'])}</td>
<td><div style="font-weight:500">{html.escape(r['name'])}</div>
<div style="font-size:11px;color:var(--muted)">{html.escape(r.get('category') or '')} · {html.escape(r.get('lifecycle_phase') or '')}</div></td>
<td><span class="pill sev-{r['severity']}">{r['severity']}</span></td>
<td style="color:var(--muted)">{html.escape(r.get('likelihood') or '')}</td>
<td>{badge}</td>
<td>{pills(r.get('guardrails') or [])}</td>
<td>{pills(r.get('affected_metrics') or [])}</td></tr>""")
    mrows = []
    for m in records["metric"]:
        mon = ('<span class="pill sev-Low">defined</span>' if m.get("monitoring")
               else '<span class="pill sev-Medium">not specified</span>')
        mrows.append(f"""<tr><td>{pill(m['id'])}</td>
<td><div style="font-weight:500">{html.escape(m['name'])}</div>
<div style="font-size:11px;color:var(--muted)">{html.escape(m.get('description') or '')}</div></td>
<td>{html.escape(m.get('category') or '')}</td>
<td>{pills(m.get('risks_measured') or [])}</td>
<td>{mon}</td></tr>""")
    body = (f'<div class="sh2"><h2>Risk register</h2><span class="cnt">{len(records["risk"])} risks · '
            'score = severity × likelihood; Critical is unscored by design</span></div>'
            '<div class="card"><table><thead><tr><th>ID</th><th>Risk</th><th>Severity</th>'
            '<th>Likelihood</th><th>Score</th><th>Guardrails</th><th>Metrics</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>'
            f'<div class="sh2"><h2>Trust metrics</h2><span class="cnt">{len(records["metric"])} metrics · '
            'the shared identifier space</span></div>'
            '<div class="card"><table><thead><tr><th>ID</th><th>Metric</th><th>Category</th>'
            '<th>Risks measured</th><th>Runtime monitoring</th></tr></thead>'
            f'<tbody>{"".join(mrows)}</tbody></table></div>')
    ptitle, psub = "Risks & Metrics", "Every risk with severity, likelihood and the guardrails that gate it; every metric with the risks it measures."
    (site / "risks.html").write_text(page("risks.html", ptitle, psub, body, meta), encoding="utf-8")
    pages.append(("risks", ptitle, psub, body))

    # ---- normative pipeline (new view) ----------------------------------
    recs = "".join(f"""<tr><td>{html.escape(r['id'])}</td>
<td><span class="pill {'prk' if r['class'] == 'normative' else 'pgr' if r['class'] == 'recommended' else 'pm'}">{r['class']}</span></td>
<td><div style="font-weight:500">{html.escape(r['title'])}</div>
<div style="font-size:12px;color:var(--muted);margin-top:3px">{html.escape((r.get('statement') or '')[:340])}…</div></td>
<td>{pills((r.get('linked_guardrails') or []) + (r.get('linked_controls') or []))}</td>
<td><span class="pill sev-Medium">{html.escape(r.get('status') or '')}</span></td></tr>""" for r in records["recommendation"])
    n = derived["normative"]
    triage_rows = "".join(f'<tr><td>{pill(e["id"])}</td><td>{html.escape(e["name"] or "")}</td>'
                          f'<td>{e["kind"]}</td></tr>' for e in n["awaiting_triage"][:200])
    body = (f'<div class="warnbox"><strong>{len(n["awaiting_triage"])} of '
            f'{len(n["awaiting_triage"]) + len(n["assigned"])} controls and guardrails have no '
            '<code>standards_status</code> assigned.</strong> Assigning them is a task force decision, not an '
            'editorial one — the importer deliberately left every one unassigned rather than guessing. '
            'This table is the work queue.</div>'
            f'<div class="sh2"><h2>Recommendations</h2><span class="cnt">{len(records["recommendation"])} REC records</span></div>'
            '<div class="card"><table><thead><tr><th>ID</th><th>Class</th><th>Recommendation</th>'
            f'<th>Linked</th><th>Status</th></tr></thead><tbody>{recs}</tbody></table></div>'
            '<div class="sh2"><h2>Awaiting standards triage</h2>'
            f'<span class="cnt">{len(n["awaiting_triage"])} items</span></div>'
            '<div class="card"><table><thead><tr><th>ID</th><th>Name</th><th>Type</th></tr></thead>'
            f'<tbody>{triage_rows}</tbody></table></div>')
    ptitle, psub = "Standards pipeline", "What RAHP is asking the specification to do, and what has not yet been triaged."
    (site / "normative.html").write_text(page("normative.html", ptitle, psub, body, meta), encoding="utf-8")
    pages.append(("normative", ptitle, psub, body))

    # ---- matrix ---------------------------------------------------------
    metrics = [m["id"] for m in records["metric"]]
    head = "".join(f'<th style="font-family:var(--mono);font-size:9px;padding:8px 3px">{m}</th>' for m in metrics)
    def matrix_rows(items, field, label_field="name"):
        out = []
        for it in items:
            have = set(it.get(field) or [])
            cells = "".join('<td style="text-align:center">'
                            + ('<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--plum)"></span>'
                               if m in have else '') + '</td>' for m in metrics)
            out.append(f'<tr><td style="white-space:nowrap">{pill(it["id"])} '
                       f'{html.escape((it.get(label_field) or it.get("function") or "")[:46])}</td>{cells}</tr>')
        return "".join(out)
    body = ('<p style="margin-bottom:16px;color:var(--muted)">User stories, scenarios and EPICs against the '
            'full metric space. Generated from the same records as every other view.</p>'
            '<div class="sh2"><h2>User stories × metrics</h2></div>'
            f'<div class="card" style="overflow-x:auto"><table><thead><tr><th>Item</th>{head}</tr></thead>'
            f'<tbody>{matrix_rows(records["user_story"], "metrics", "function")}</tbody></table></div>'
            '<div class="sh2"><h2>Scenarios × metrics</h2></div>'
            f'<div class="card" style="overflow-x:auto"><table><thead><tr><th>Item</th>{head}</tr></thead>'
            f'<tbody>{matrix_rows(records["scenario"], "metrics")}</tbody></table></div>'
            '<div class="sh2"><h2>EPICs × metrics</h2></div>'
            f'<div class="card" style="overflow-x:auto"><table><thead><tr><th>Item</th>{head}</tr></thead>'
            f'<tbody>{matrix_rows(records["epic"], "metrics")}</tbody></table></div>')
    ptitle, psub = "Cross-reference matrix", "The shared identifier space that links personas, stories, scenarios, EPICs and risks."
    (site / "matrix.html").write_text(page("matrix.html", ptitle, psub, body, meta), encoding="utf-8")
    pages.append(("matrix", ptitle, psub, body))

    # ---- lifecycle ------------------------------------------------------
    life = derived["lifecycle"]
    stages = []
    for s in life["records"]:
        gaps = "".join(
            f'<div class="gapbox{" blocking" if g.get("severity") == "blocking" else ""}">'
            f'<strong>{html.escape(g["id"])}</strong> — {html.escape(g["description"])}'
            + (f'<br><small class="mono">addressed by {html.escape(g["addressed_by"])}</small>'
               if g.get("addressed_by") else '') + '</div>'
            for g in s.get("gaps") or [])
        stages.append(f"""<div class="stage"><h3>{html.escape(s['id'])} · {html.escape(s['name'])}</h3>
<div class="sum">{html.escape(s['summary'])}</div>
<dl class="kv">
<dt>Input artefacts</dt><dd>{html.escape(', '.join(s.get('input_artefacts') or []))}</dd>
<dt>Produces</dt><dd>{html.escape(', '.join(s.get('produces_record_types') or []))}</dd>
<dt>Required outputs</dt><dd>{html.escape('; '.join(s.get('required_outputs') or []))}</dd>
<dt>Evidence required</dt><dd>{html.escape(s.get('evidence_required') or '—')}</dd>
</dl>{gaps}</div>""")
    body = (f'<div class="card"><div class="cb"><strong>Core principle.</strong> '
            f'{html.escape(life["core_principle"])}</div></div>' + "".join(stages))
    ptitle, psub = "Lifecycle & gaps", "The RAHP method across the five stages of standards development, with every known gap as a tracked record."
    (site / "lifecycle.html").write_text(page("lifecycle.html", ptitle, psub, body, meta), encoding="utf-8")
    pages.append(("lifecycle", ptitle, psub, body))

    # ---- governance -----------------------------------------------------
    ra = "".join(f"""<tr><td>{html.escape(a['id'])}</td><td>{pill(a['risk_id'])}</td>
<td><span class="pill {'sev-Medium' if a['decision'] == 'pending' else 'sev-Low'}">{a['decision']}</span></td>
<td>{html.escape(a.get('authority') or '—')}</td>
<td style="font-size:12px;color:var(--muted)">{html.escape((a.get('rationale') or '')[:260])}</td>
<td>{html.escape(a.get('review_date') or '—')}</td></tr>""" for a in records["risk_acceptance"])
    gp = "".join(f"""<tr><td>{html.escape(g['id'])}</td>
<td><div style="font-weight:500">{html.escape(g['title'])}</div>
<div style="font-size:12px;color:var(--muted);margin-top:3px">{html.escape(g['rationale'][:300])}</div></td>
<td>{pills((g.get('linked_risks') or []) + (g.get('linked_guardrails') or []))}</td>
<td><span class="pill sev-Medium">{html.escape(g['status'])}</span></td></tr>""" for g in records["governance_precedent"])
    body = ('<div class="warnbox"><strong>No risk has been formally accepted.</strong> Every acceptance record '
            'below is <code>pending</code> because the working group has not yet decided who may accept a risk, '
            'under what authority, or against what evidence threshold. That decision (roadmap Q3 and Q4) blocks '
            'assurance test AT-17 from ever passing.</div>'
            f'<div class="sh2"><h2>Risk acceptances</h2><span class="cnt">{len(records["risk_acceptance"])} records</span></div>'
            '<div class="card"><table><thead><tr><th>ID</th><th>Risk</th><th>Decision</th><th>Authority</th>'
            f'<th>Rationale</th><th>Review</th></tr></thead><tbody>{ra}</tbody></table></div>'
            f'<div class="sh2"><h2>Governance precedents</h2><span class="cnt">{len(records["governance_precedent"])} records</span></div>'
            '<div class="card"><table><thead><tr><th>ID</th><th>Precedent</th><th>Linked</th>'
            f'<th>Status</th></tr></thead><tbody>{gp}</tbody></table></div>')
    ptitle, psub = "Decisions & acceptances", "Formal risk acceptances and the governance precedents that explain why the toolkit looks the way it does."
    (site / "governance.html").write_text(page("governance.html", ptitle, psub, body, meta), encoding="utf-8")
    pages.append(("governance", ptitle, psub, body))

    return site, pages


def build_normative_md(records, derived, out):
    lines = ["# Standards action set", "",
             "Generated by `tools/build.py`. Do not edit.", "",
             "## Recommendations", ""]
    for r in records["recommendation"]:
        lines += [f"### {r['id']} — {r['title']} ({r['class']}, {r['status']})", "",
                  r["statement"], "",
                  f"Linked: {', '.join((r.get('linked_guardrails') or []) + (r.get('linked_controls') or [])) or '—'}", ""]
    n = derived["normative"]
    lines += ["## Awaiting standards triage", "",
              f"{len(n['awaiting_triage'])} controls and guardrails have no `standards_status`.", "",
              "| ID | Name | Type |", "|---|---|---|"]
    for e in n["awaiting_triage"]:
        lines.append(f"| {e['id']} | {e['name']} | {e['kind']} |")
    (out / "normative.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "build"))
    ap.add_argument("--data", default=str(ROOT / "data"))
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    data_dir = pathlib.Path(a.data)
    instance = load(data_dir / "instance.yaml")
    records = load_all(data_dir, instance)
    lifecycle = load(ROOT / "method" / "lifecycle.yaml")

    derived = {
        "persona_xrefs": derive_persona_xrefs(records),
        "coverage": derive_coverage(records),
        "normative": derive_normative_set(records),
        "lifecycle": lifecycle,
    }

    (out / "jsonld").mkdir(parents=True, exist_ok=True)
    (out / "derived").mkdir(parents=True, exist_ok=True)

    for rtype, recs in records.items():
        if rtype not in TYPE_MAP or not recs:
            continue
        (out / "jsonld" / f"{rtype}.jsonld").write_text(
            json.dumps(to_jsonld(rtype, recs), indent=2, ensure_ascii=False), encoding="utf-8")

    (out / "rahp.json").write_text(json.dumps({
        "instance": instance["instance"], "records": records}, indent=2, ensure_ascii=False), encoding="utf-8")

    for name in ("persona_xrefs", "coverage", "normative"):
        (out / "derived" / f"{name}.json").write_text(
            json.dumps(derived[name], indent=2, ensure_ascii=False), encoding="utf-8")

    counts = " · ".join(f"{len(v)} {k}" for k, v in records.items() if v)
    meta = {
        "toolkit_version": instance["instance"]["toolkit_version"],
        "spec_version": instance["instance"]["target_specification"]["version_assessed"],
        "maintainer": "RAHP Task Force",
        "counts": counts,
    }
    site, pages = build_site(records, derived, meta, out)
    single = build_single_file(pages, meta, out)
    build_normative_md(records, derived, out)

    print("Built:")
    print(f"  {out/'rahp.json'}")
    print(f"  {out/'jsonld'}/ ({len([1 for k, v in records.items() if v and k in TYPE_MAP])} files)")
    print(f"  {out/'derived'}/")
    print(f"  {site}/ ({len(NAV)} pages)")
    print(f"  {single}")
    print(f"  {out/'normative.md'}")
    print(f"  {counts}")


if __name__ == "__main__":
    main()

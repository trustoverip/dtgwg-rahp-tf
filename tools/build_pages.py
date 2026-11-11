#!/usr/bin/env python3
"""build_pages.py — build the RAHP toolkit GitHub Pages site from data/ and method/.

The pages are generated, never edited by hand. If a fact is wrong on a page, fix it in
data/ or method/ (or in site/ for the front door and the examples) and build again.

Inputs:
    data/, method/            the catalogue and method (the source of truth)
    review/examples/          the upstream worked examples
    site/home.src.html        the front door template; its <style> is the design system for every page
    site/examples/            example inputs that are not review records in this repository
    site/manifests/           "who did what" steps for some examples

Plain words first; file codes (RK-, CT-, GR-, ...) only inside each item's details.

Usage:
    python3 tools/build_pages.py [--out _site]
"""
import sys, os, re, html, yaml, base64, json, shutil, subprocess, argparse, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
_ap.add_argument('--out', default=os.path.join(ROOT, '_site'), help='output directory (default: _site)')
_args = _ap.parse_args()
REPO, OUT = ROOT, _args.out
EXDIR = os.path.join(ROOT, 'site', 'examples')
MANIFESTS = os.path.join(ROOT, 'site', 'manifests')
HOME = os.path.join(OUT, 'index.html')
os.makedirs(OUT, exist_ok=True)
shutil.copyfile(os.path.join(ROOT, 'site', 'home.src.html'), HOME)  # the front door is edited in place below


def _git(*a):
    try:
        return subprocess.check_output(['git', '-C', ROOT, *a], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ''


COMMIT = os.environ.get('GITHUB_SHA') or _git('rev-parse', 'HEAD') or 'main'
_cdate = _git('show', '-s', '--format=%cs', COMMIT)
COMMIT_DATE = (datetime.date.fromisoformat(_cdate).strftime('%-d %B %Y') if _cdate else '')

def L(p): return yaml.safe_load(open(os.path.join(REPO, p)))
def recs(p): return L(p)['records']
E = html.escape

personas = recs('data/personas.yaml'); risks = recs('data/risks.yaml'); scen = recs('data/scenarios.yaml')
stories = recs('data/user-stories.yaml'); controls = recs('data/controls.yaml'); guards = recs('data/guardrails.yaml')
tests = recs('data/assurance-tests.yaml'); metrics = recs('data/metrics.yaml'); recsn = recs('data/recommendations.yaml')
accepts = recs('data/risk-acceptances.yaml'); precs = recs('data/governance-precedents.yaml')
life = L('method/lifecycle.yaml'); vocab = L('method/vocabularies.yaml')
P = {x['id']: x for x in personas}; R = {x['id']: x for x in risks}; S = {x['id']: x for x in scen}
C = {x['id']: x for x in controls}; G = {x['id']: x for x in guards}; T = {x['id']: x for x in tests}; M = {x['id']: x for x in metrics}

STAGE_MAP = {  # proposed mapping of the review journey (front door) onto the five lifecycle stages
 'STAGE-1': ('Steps 0 to 3', 'Choose a way in, pick the people and situations, gather the catalogue. The people and situations come from this stage.', ['na1','na2'], ['ai1']),
 'STAGE-2': ('Steps 4 to 12', 'Pin the exact version of the draft, read it with the person\'s eyes, draft and review findings, build and check the record.', ['na3','na4','na5','na6','na7','na8'], ['ai2','ai3','ai4','ai5','ai6','ai7','ai8','ai9']),
 'STAGE-3': ('Steps 13 to 15', 'Find themes across specifications, examine independently, and decide: where fixes go, how serious, what to accept.', ['na9'], ['ai10']),
 'STAGE-4': ('Step 16', 'Share and feed back: the published review shows what was found and what is still open.', ['na10'], ['ai11']),
 'STAGE-5': ('Step 17', 'Reassess after the specification changes, with a new review record at the new version.', [], []),
}
STEP_STAGE = {sid: st for st, v in STAGE_MAP.items() for sid in v[2] + v[3]}
DATA_NOTE = (f'Built from the toolkit repository at commit <a href="https://github.com/trustoverip/dtgwg-rahp-tf/commit/{COMMIT}">{COMMIT[:7]}</a>'
             + (f' ({COMMIT_DATE}).' if COMMIT_DATE else '.'))

# ---------- plain-language labels ----------
PTYPE = {'legitimate_user': ('People the system serves', 'served'), 'edge_case': ('Edge cases', 'edge'),
         'machine_agent': ('AI agents', 'machine'), 'bad_actor': ('People who cause harm', 'harm')}
CAT = {'Human Experience': "People's experience", 'Schemas': 'Data formats', 'Systemic': 'Whole system',
       'Network Managers': 'Network operators', 'External': 'Law and outside world'}
def cat(c): return CAT.get(c, c)
SEV_ORDER = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
SCORE = {'High': 3, 'Medium': 2, 'Low': 1}
def score(r):
    if r['severity'] == 'Critical': return None
    return SCORE[r['severity']] * SCORE[r['likelihood']]
PRIORITY = {'must_address': 'Must be addressed before the stage opens', 'should_address': 'Should be addressed'}
CTYPE = {'Technical': 'Technical', 'Governance': 'Governance', 'Procedural': 'Process', 'UX': 'User experience', 'Legal': 'Legal'}
MALIGN = {'M2'}

# ---------- relations ----------
st_by_p = {}
for s in stories: st_by_p.setdefault(s['persona'], set()).add(s['id'])
sc_by_p = {}
for s in scen:
    for p in (s.get('legitimate_personas') or []) + (s.get('adversarial_personas') or []): sc_by_p.setdefault(p, set()).add(s['id'])
def role(pid, rk):
    p = P[pid]
    if p['type'] == 'bad_actor' or pid in MALIGN: return 'causes'
    for sid in rk.get('scenarios') or []:
        if pid in (S.get(sid, {}).get('adversarial_personas') or []): return 'causes'
    return 'affected'
risk_people = {}
for r in risks:
    for pid in P:
        if set(r.get('user_stories') or []) & st_by_p.get(pid, set()) or set(r.get('scenarios') or []) & sc_by_p.get(pid, set()):
            risk_people.setdefault(r['id'], []).append(pid)
people_risks = {pid: [r for r in risks if pid in risk_people.get(r['id'], [])] for pid in P}
scen_risks = {sid: [r for r in risks if sid in (r.get('scenarios') or [])] for sid in S}
test_by_g = {}
for t in tests: test_by_g.setdefault(t['guardrail'], []).append(t)

# ---------- glossary ----------
GLOSS = [
 ('dtg', 'Decentralized Trust Graph', 'A web of verifiable trust relationships between people, groups, organisations and AI agents, with no central database. Each party controls its own part.', ['DTG', 'trust graph']),
 ('vtc', 'Trust community (VTC)', 'A Verifiable Trust Community: an online group whose members are verified, whose relationships can be checked, and which has its own rules for membership.', ['VTC']),
 ('initiator', 'Founder (initiator)', 'The first person to set up a trust community. They become its first member and set the first rules. Their power should be time-limited.', ['initiator', 'Initiator']),
 ('anchor', 'Trust anchor', 'A trusted member allowed to invite and vouch for new members.', ['anchor', 'Anchor']),
 ('phases', 'The four phases of a trust community', 'Phase 1: founding (genesis). Phase 2: inviting the first trust anchors. Phase 3: anchors vouch for new members. Phase 4: members vouch for each other, with an identity check.', ['Phase']),
 ('did', 'Decentralized identifier (DID)', 'An identifier that a person, organisation or community controls itself, without a central registry. A community has one (C-DID), and each member has one per community (M-DID).', ['DID']),
 ('vta', 'Community agent (VTA)', "A Verifiable Trust Agent: software that acts for the community. It applies the community's rules (through a policy enforcement point, PEP), issues membership credentials and writes to the trust registry.", ['VTA', 'PEP']),
 ('credential', 'Verifiable credential', 'A digital statement, such as "this person is a member", that can be checked without asking the issuer each time.', ['credential', 'Credential']),
 ('vmc', 'Membership credential (VMC)', "A Verifiable Membership Credential: issued by the community's agent to say someone is a member, and in what role.", ['VMC']),
 ('vrc', 'Relationship credential (VRC)', 'A Verifiable Relationship Credential: exchanged between two people to prove they know and trust each other.', ['VRC']),
 ('phc', 'Personhood credential (PHC)', 'A credential that shows its holder is a real, unique person, without saying who.', ['PHC', 'personhood']),
 ('idvp', 'Identity checker (IDVP) and ID credential (IDVC)', 'An Identity Verification Provider is an approved organisation that checks who someone is and issues an Identity Verification Credential.', ['IDVP', 'IDVC']),
 ('registry', 'Trust registry', 'A record of who is trusted to do what in a community, for example which identity checkers are approved.', ['registry', 'Registry']),
 ('revocation', 'Revocation', 'Withdrawing a credential, for example when someone leaves or is removed from a community.', ['revocation', 'Revocation', 'revoke']),
 ('zkp', 'Zero-knowledge proof (ZKP)', 'A way to prove something, such as "over 18", without revealing the underlying data.', ['ZKP', 'zero-knowledge']),
 ('sybil', 'Sybil attack', 'One person creating many fake identities to gain unfair influence.', ['Sybil', 'sybil']),
 ('cib', 'Coordinated inauthentic behaviour (CIB)', 'Organised groups of accounts acting together while hiding that they are coordinated, for example to flood a community\'s processes.', ['CIB', 'coordinated']),
 ('nhi', 'Non-human identity (NHI)', 'An AI agent or automated system that holds and presents its own credentials.', ['NHI', 'agent']),
 ('sdm', 'Supported decision-making', 'A person makes their own decisions with help to understand and communicate them. Different from an attorney deciding for them.', ['supported decision', 'Supported Decision']),
 ('lpa', 'Lasting Power of Attorney (LPA)', 'A legal document, registered in England and Wales, that lets a named attorney make decisions for someone who has lost capacity.', ['LPA', 'attorney']),
 ('safeguard', 'Safeguard (control)', 'A measure that reduces a risk. In the files: a control, with a code starting CT-.', []),
 ('musthave', 'Must-have (guardrail)', 'A condition that must be met before a stage of a community can open. It is a yes-or-no gate, not a matter of degree. In the files: a guardrail, GR-.', ['guardrail', 'Guardrail']),
 ('test', 'Test (assurance test)', 'Evidence that a must-have has been met. In the files: an assurance test, AT-.', []),
 ('measure', 'Measure (metric)', 'Something you can track to see whether a safeguard is working. In the files: a metric, M-.', []),
 ('acceptance', 'Risk acceptance', 'A recorded decision, by someone with authority, to live with a risk that has not been fully reduced. Critical risks may never be accepted.', []),
 ('normative', 'Normative language: MUST, SHOULD, MAY', 'Words with fixed meanings in standards. MUST is a requirement. SHOULD is strongly recommended, but there may be good reasons not to. MAY is optional.', ['MUST', 'normative', 'SHOULD']),
]
def gloss_links(*texts):
    t = ' '.join(x for x in texts if x)
    out = []
    for gid, name, _, keys in GLOSS:
        if keys and any(re.search(r'\b' + re.escape(k), t) for k in keys): out.append((gid, name))
    if not out: return ''
    return '<p class="terms"><span>Words used here:</span> ' + ' '.join(f'<a href="glossary.html#{g}">{E(n)}</a>' for g, n in out) + '</p>'

# ---------- shared shell ----------
home = open(HOME).read()
CSS = re.search(r'<style>(.*?)</style>', home, re.S).group(1)
TOIP = re.search(r'<span class="plate"><img src="([^"]+)"', home).group(1)
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">'

NAV = [('index.html', 'Home', 'home'), ('index.html#journey', 'The journey', 'journey'), ('index.html#guides', 'Guides', 'guides'), ('examples.html', 'Examples', 'examples'), ('people.html', 'People', 'people'),
       ('situations.html', 'Situations', 'situations'), ('risks.html', 'Risks', 'risks'), ('safeguards.html', 'Safeguards', 'safeguards'),
       ('affected.html', 'Who is affected', 'affected'), ('lifecycle.html', 'Lifecycle', 'lifecycle'), ('decisions.html', 'Decisions', 'decisions'),
       ('glossary.html', 'Words', 'glossary')]
def header(active, home_page=False):
    items = []
    for href, label, key in NAV:
        h = href
        if home_page and href.startswith('index.html'): h = href.replace('index.html', '') or '#top'
        cur = ' aria-current="page"' if key == active else ''
        items.append(f'<li><a href="{h}"{cur}>{label}</a></li>')
    return f'''<header class="site">
  <div class="wrap">
    <a class="mark" href="{'#top' if home_page else 'index.html'}" aria-label="RAHP Toolkit home">
      <span class="plate"><img src="{TOIP}" alt="Trust over IP Foundation"></span>
      <span class="words">
        <span class="org">Decentralized Trust Graph Working Group</span>
        <span class="name"><b>RAHP</b> <span>Toolkit</span></span>
      </span>
    </a>
    <nav class="main" aria-label="Main">
      <ul>
        {''.join(items)}
      </ul>
    </nav>
  </div>
</header>'''

STATUS = '''<div class="status" role="note" aria-label="Page status">
  <div class="wrap">
    <span class="pill draft">Draft</span>
    <span>Draft for review by the RAHP Task Force. Not an official Trust over IP Foundation page until approved. ''' + DATA_NOTE + '''</span>
  </div>
</div>'''

FOOTER = '''<footer class="site">
  <div class="wrap">
    <div>
      <p><b style="color:var(--fg)">RAHP Task Force</b>, Decentralized Trust Graph Working Group, Trust over IP Foundation.</p>
      <p><a href="https://github.com/trustoverip/dtgwg-rahp-tf" rel="noopener">Repository on GitHub</a> · Content CC-BY 4.0 · Code Apache 2.0</p>
      <p>''' + DATA_NOTE + ''' People in the catalogue are fictional.</p>
    </div>
    <div>
      <p><b style="color:var(--fg)">AI use.</b> This draft was designed and written with Claude (claude-opus-5-5, Anthropic) as drafting author, from the toolkit's own data. Nicky Hickman is author of record and approves anything published. EU AI Act, Article 50 transparency.</p>
    </div>
  </div>
</footer>'''

PAGE_CSS = r'''
.page-head .wrap{padding-block:clamp(1.8rem,4vw,2.8rem)}
.page-head h1{font-weight:300;font-size:clamp(1.9rem,4vw,2.8rem);letter-spacing:.04em;text-transform:uppercase;margin:.3rem 0 0}
.page-head .lead{font-size:1.05rem}
.crumbs{font-size:.88rem;color:var(--muted);margin:0}
.crumbs a{color:var(--muted)}
.toolbar{display:flex;flex-wrap:wrap;gap:.6rem 1.2rem;align-items:center;margin:0 0 1.2rem}
.chips{display:flex;flex-wrap:wrap;gap:.4rem}
.chip{font:inherit;font-family:var(--font-display);font-weight:600;font-size:.84rem;border:1.5px solid var(--line);background:var(--bg);color:var(--fg);border-radius:999px;padding:.35rem .85rem;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--brand);border-color:var(--brand);color:var(--on-brand)}
.chip .c{font-variant-numeric:tabular-nums;opacity:.8;margin-left:.3rem}
.search{font:inherit;border:1.5px solid var(--line);border-radius:var(--radius);padding:.45rem .7rem;background:var(--bg);color:var(--fg);min-width:min(100%,260px)}
.count-line{font-size:.9rem;color:var(--muted);margin:0 0 .8rem}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,330px),1fr));gap:1rem}
.card{border:1px solid var(--line);border-radius:var(--radius);background:var(--bg);padding:1.1rem 1.2rem;display:flex;flex-direction:column;gap:.55rem;min-width:0;scroll-margin-top:90px}
.card h3{font-size:1.12rem;font-weight:800;line-height:1.25}
.card .role{margin:0;color:var(--muted);font-size:.93rem}
.card blockquote{margin:0;font-style:italic;border-left:3px solid var(--mint);padding-left:.8rem;font-size:.97rem}
.card details{border-top:1px dashed var(--line);padding-top:.5rem}
.card summary,.item summary{cursor:pointer;color:var(--brand);font-weight:700}
.kv{display:grid;gap:.6rem;margin-top:.7rem;font-size:.94rem}
.kv h4{font-family:var(--font-display);font-weight:800;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--mid);margin:0 0 .2rem}
.kv ul{margin:0;padding-left:1.15rem;display:grid;gap:.15rem}
.kv p{margin:0}
.ref{font-family:var(--font-mono);font-size:.8rem;color:var(--muted);margin:.4rem 0 0}
.terms{font-size:.85rem;color:var(--muted);margin:.4rem 0 0}
.terms span{font-weight:700}
.terms a{margin-right:.5rem}
.ptype{display:inline-flex;align-items:center;gap:.4rem;font-family:var(--font-display);font-weight:800;font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;padding:.2rem .55rem;border-radius:4px;align-self:flex-start;border:1.5px solid currentColor}
.ptype::before{content:"";width:.6rem;height:.6rem;display:inline-block}
.ptype.served{color:var(--brand)} .ptype.served::before{background:currentColor;border-radius:50%}
.ptype.edge{color:var(--mid)} .ptype.edge::before{border:2px solid currentColor;border-radius:50%}
.ptype.machine{color:var(--muted)} .ptype.machine::before{border:2px solid currentColor;transform:rotate(45deg)}
.ptype.harm{color:var(--alert)} .ptype.harm::before{width:0;height:0;border-left:.35rem solid transparent;border-right:.35rem solid transparent;border-bottom:.6rem solid currentColor}
.flag{font-size:.86rem;background:var(--draft-bg);border-left:4px solid var(--draft);padding:.5rem .7rem}
.links a{white-space:normal}
.items{display:grid;gap:.6rem}
.item{border:1px solid var(--line);border-radius:var(--radius);background:var(--bg);scroll-margin-top:90px}
.item>summary{list-style:none;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.4rem 1rem;align-items:center;padding:.85rem 1rem;color:var(--fg);font-weight:400}
.item>summary::-webkit-details-marker{display:none}
.item>summary .t{font-weight:700;color:var(--fg)}
.item>summary .t::before{content:"+";display:inline-block;width:1.1rem;color:var(--brand);font-weight:800}
.item[open]>summary .t::before{content:"\2212"}
.item>summary .sub{grid-column:1;font-size:.88rem;color:var(--muted);padding-left:1.1rem}
.item>summary .tags{grid-row:1 / span 2;grid-column:2;display:flex;gap:.35rem;flex-wrap:wrap;justify-content:flex-end}
.item .body{padding:0 1rem 1rem 2.1rem}
.sev{font-family:var(--font-display);font-weight:800;font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;padding:.2rem .5rem;border-radius:4px;white-space:nowrap;border:1.5px solid currentColor}
.sev.Critical{background:var(--alert);color:#fff;border-color:var(--alert)}
.sev.High{color:var(--alert)}
.sev.Medium{color:var(--draft)}
.sev.Low{color:var(--muted)}
.pri{font-family:var(--font-display);font-weight:800;font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;padding:.2rem .5rem;border-radius:4px;background:var(--surface-2);color:var(--fg);white-space:nowrap}
.heat{display:grid;grid-template-columns:auto repeat(3,minmax(0,1fr));gap:4px;max-width:520px;font-size:.88rem}
.heat .hd{font-family:var(--font-display);font-weight:800;font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;justify-content:center;padding:.3rem;text-align:center}
.heat .rh{justify-content:flex-end}
.heat button{font:inherit;font-family:var(--font-display);font-weight:800;font-size:1.2rem;border:1.5px solid var(--line);border-radius:4px;min-height:3rem;cursor:pointer;background:var(--bg);color:var(--fg)}
.heat button[data-n="0"]{color:var(--muted);font-weight:400;cursor:default}
.heat button.s9{background:#fbe2dc;border-color:var(--alert)} .heat button.s6{background:#fdeee6} .heat button.s4{background:var(--draft-bg)} .heat button.s3{background:var(--surface)} .heat button.s2{background:var(--surface)}
.heat button[aria-pressed="true"]{outline:3px solid var(--brand);outline-offset:1px}
.heat .crit{grid-column:2 / -1;background:var(--alert);color:#fff;border-color:var(--alert)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .heat button.s9{background:#4a1d17} :root:not([data-theme="light"]) .heat button.s6{background:#3b2318}}
:root[data-theme="dark"] .heat button.s9{background:#4a1d17} :root[data-theme="dark"] .heat button.s6{background:#3b2318}
.layout2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:2rem;align-items:start}
.subnav{display:flex;flex-wrap:wrap;gap:.5rem;margin:0 0 1.5rem;padding:0;list-style:none}
.subnav a{display:block;border:1.5px solid var(--line);border-radius:999px;padding:.35rem .9rem;text-decoration:none;font-family:var(--font-display);font-weight:600;font-size:.88rem}
.subnav a:hover{border-color:var(--brand)}
h2.sec{font-family:var(--font-display);font-weight:300;font-size:1.6rem;letter-spacing:.05em;text-transform:uppercase;margin:2.2rem 0 .4rem;scroll-margin-top:90px}
.mx-wrap{overflow:auto;max-height:80vh;border:1px solid var(--line);border-radius:var(--radius);background:var(--bg)}
table.mx{border-collapse:separate;border-spacing:0;font-size:.86rem}
table.mx th,table.mx td{border-bottom:1px solid var(--line);border-right:1px solid var(--line);padding:.35rem .45rem}
table.mx thead th{position:sticky;top:0;background:var(--surface);z-index:2;vertical-align:bottom;min-width:5.6rem;font-weight:700;text-align:left}
table.mx thead th small{display:block;font-weight:400;color:var(--muted)}
table.mx tbody th{position:sticky;left:0;background:var(--bg);z-index:1;text-align:left;min-width:16rem;max-width:20rem;font-weight:400}
table.mx thead th:first-child{left:0;z-index:3}
table.mx td{text-align:center;font-size:1rem;position:relative}
table.mx tr.grp th{background:var(--surface-2);font-family:var(--font-display);font-weight:800;font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
table.mx td.a{color:var(--brand)} table.mx td.c{color:var(--alert)}
.colgrp{font-family:var(--font-display);font-weight:800;font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.stepper{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.6rem;list-style:none;margin:0 0 2rem;padding:0;counter-reset:s}
.stepper li{counter-increment:s;border-top:6px solid var(--brand);background:var(--bg);border-left:1px solid var(--line);border-right:1px solid var(--line);border-bottom:1px solid var(--line);border-radius:0 0 var(--radius) var(--radius);padding:.8rem .9rem}
.stepper li a{text-decoration:none;color:var(--fg);font-weight:800;font-family:var(--font-display)}
.stepper li a::before{content:counter(s) ". ";color:var(--brand)}
.stepper li p{margin:.3rem 0 0;font-size:.88rem;color:var(--muted)}
.stage{border:1px solid var(--line);border-radius:var(--radius);background:var(--bg);padding:1.3rem;margin-bottom:1.2rem;scroll-margin-top:90px}
.stage h3{font-size:1.3rem;font-weight:800}
.stage .grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin-top:1rem}
.substeps{list-style:none;margin:.8rem 0 0;padding:0;display:grid;gap:.5rem;counter-reset:ss}
.substeps li{counter-increment:ss;display:grid;grid-template-columns:2rem minmax(0,1fr);gap:.6rem}
.substeps li::before{content:counter(ss);font-family:var(--font-display);font-weight:800;font-size:.8rem;color:var(--brand);background:var(--surface-2);border-radius:50%;width:2rem;height:2rem;display:grid;place-items:center}
.gap{border-left:4px solid var(--draft);background:var(--draft-bg);padding:.6rem .8rem;font-size:.93rem;margin-top:.5rem}
.gap.blocking{border-left-color:var(--alert)}
.gap b{font-family:var(--font-display);font-size:.68rem;letter-spacing:.1em;text-transform:uppercase}
.banner{background:var(--draft-bg);border:1px solid var(--line);border-left:6px solid var(--alert);border-radius:var(--radius);padding:1rem 1.2rem;margin-bottom:1.5rem}
.banner h2{font-size:1.15rem;font-weight:800;margin:0 0 .3rem}
.banner p{margin:0}
.dl{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr));gap:1rem}
.gloss{display:grid;gap:.8rem}
.gloss>div{border:1px solid var(--line);border-radius:var(--radius);padding:.9rem 1.1rem;background:var(--bg);scroll-margin-top:90px}
.gloss h3{font-size:1.02rem;font-weight:800}
.gloss p{margin:.3rem 0 0}
.wordmap{width:100%;border-collapse:collapse;font-size:.95rem}
.wordmap th,.wordmap td{text-align:left;padding:.55rem .7rem;border-bottom:1px solid var(--line)}
.wordmap th{font-family:var(--font-display);font-weight:800;font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
:target{outline:3px solid var(--mid);outline-offset:2px}
@media (max-width:900px){.stepper{grid-template-columns:repeat(2,minmax(0,1fr))}.stage .grid3,.layout2{grid-template-columns:minmax(0,1fr)}}
@media (max-width:560px){.item>summary{grid-template-columns:minmax(0,1fr)}.item>summary .tags{grid-row:auto;grid-column:1;justify-content:flex-start;padding-left:1.1rem}.item .body{padding-left:1rem}.stepper{grid-template-columns:minmax(0,1fr)}}
'''

COMMON_JS = r'''<script>
(function(){
  function openHash(){
    var id=decodeURIComponent(location.hash.slice(1)); if(!id) return;
    var el=document.getElementById(id); if(!el) return;
    var d=el.tagName==='DETAILS'?el:el.querySelector('details');
    if(d) d.open=true;
    var p=el.closest('[hidden]'); if(p) p.hidden=false;
    el.scrollIntoView({block:'start'});
  }
  window.addEventListener('hashchange',openHash); openHash();
})();
</script>'''

def page(fname, title, active, crumb, h1, lead, body, js='', tint=False):
    out = f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
{FONTS}
<style>{CSS}
{PAGE_CSS}
html{{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to the main content</a>
{STATUS}
{header(active)}
<main id="main">
  <section class="page-head"><div class="wrap">
    <p class="crumbs"><a href="index.html">Home</a> · {E(crumb)}</p>
    <h1>{E(h1)}</h1>
    <p class="lead">{lead}</p>
  </div></section>
  <section class="band{' tint' if tint else ' tint'}" style="border-top:1px solid var(--line)"><div class="wrap">
{body}
  </div></section>
</main>
{FOOTER}
{COMMON_JS}
{js}
</body>
</html>'''
    open(os.path.join(OUT, fname), 'w').write(out)

def plink(pid, page='people.html'):
    p = P[pid]; return f'<a href="{page}#{pid}">{E(p["name"])}</a>'
def rlink(rid): return f'<a href="risks.html#{rid}">{E(R[rid]["name"])}</a>' if rid in R else E(rid)
def slink(sid): return f'<a href="situations.html#{sid}">{E(S[sid]["name"])}</a>' if sid in S else E(sid)
def glink(gid): return f'<a href="safeguards.html#{gid}">{E(G[gid]["name"])}</a>' if gid in G else E(gid)
def clink(cid): return f'<a href="safeguards.html#{cid}">{E(C[cid]["name"])}</a>' if cid in C else E(cid)
def mlink(mid): return f'<a href="safeguards.html#{mid}">{E(M[mid]["name"])}</a>' if mid in M else E(mid)
def ul(items):
    items = [i for i in items if i]
    return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>' if items else '<p>None recorded.</p>'
def kvsec(title, inner): return f'<div><h4>{E(title)}</h4>{inner}</div>'
def ptag(pid):
    t, cls = PTYPE[P[pid]['type']]
    if pid in MALIGN: t, cls = 'AI agent causing harm', 'harm'
    elif P[pid]['type'] == 'machine_agent': t = 'AI agent'
    return f'<span class="ptype {cls}">{E(t)}</span>'

# ================= people.html =================
groups = [('served', 'People the system serves'), ('edge', 'Edge cases'), ('machine', 'AI agents'), ('harm', 'People and agents who cause harm')]
def pgroup(p):
    if p['id'] in MALIGN or p['type'] == 'bad_actor': return 'harm'
    return PTYPE[p['type']][1]
cards = []
for p in personas:
    ctx = p.get('context') or {}
    ctxl = [f'<b>{E(k.replace("_", " ").capitalize())}:</b> {E(str(v))}' for k, v in ctx.items()]
    sc = sorted(sc_by_p.get(p['id'], set()), key=lambda x: int(re.sub(r'\D', '', x)))
    rk = people_risks[p['id']]
    rk_aff = [rlink(r['id']) for r in rk if role(p['id'], r) == 'affected']
    rk_cau = [rlink(r['id']) for r in rk if role(p['id'], r) == 'causes']
    ev = [f'{E(e["claim"])} <a href="{E(e["url"])}" rel="noopener">{E(e["source"])}</a>' if e.get('url') else f'{E(e["claim"])} ({E(e.get("source",""))})' for e in (p.get('evidence') or [])]
    inner = ''.join([
        kvsec('About them', ul(ctxl)),
        kvsec('What they want', ul([E(x) for x in p.get('goals') or []])),
        kvsec('What worries them', ul([E(x) for x in p.get('risk_context') or []])) if p.get('risk_context') else '',
        kvsec('What helps them take part', ul([E(x) for x in p.get('inclusion_drivers') or []])) if p.get('inclusion_drivers') else '',
        kvsec('What keeps them out', ul([E(x) for x in p.get('exclusion_risks') or []])) if p.get('exclusion_risks') else '',
        kvsec('Situations they appear in', ul([slink(s) for s in sc])),
        kvsec('Risks that could harm them', ul(rk_aff)) if rk_aff else '',
        kvsec('Risks they could cause', ul(rk_cau)) if rk_cau else '',
        kvsec('Evidence', ul(ev)) if ev else '',
    ])
    terms = gloss_links(p.get('role'), ' '.join(p.get('goals') or []), ' '.join(p.get('risk_context') or []))
    flag = f'<p class="flag"><b>Safeguarding:</b> {E(p["safeguarding_note"])}</p>' if p.get('safeguarding') else ''
    cards.append(f'''<article class="card" id="{p['id']}" data-group="{pgroup(p)}">
  {ptag(p['id'])}
  <h3>{E(p['name'])}</h3>
  <p class="role">{E(p['role'])}</p>
  <blockquote>{E(p.get('quote') or '')}</blockquote>
  {flag}
  <details><summary>More about {E(p['name'].split(' ')[0] if p['type'] in ('legitimate_user','edge_case') else p['name'])}</summary>
    <div class="kv">{inner}</div>{terms}
    <p class="ref">Reference in the files: {p['id']}</p>
  </details>
</article>''')
cnt = {g: sum(1 for p in personas if pgroup(p) == g) for g, _ in groups}
chips = '<button type="button" class="chip" data-f="all" aria-pressed="true">All<span class="c">' + str(len(personas)) + '</span></button>' + ''.join(
    f'<button type="button" class="chip" data-f="{g}" aria-pressed="false">{E(t)}<span class="c">{cnt[g]}</span></button>' for g, t in groups)
body = f'''<div class="toolbar"><div class="chips" role="group" aria-label="Show">{chips}</div></div>
<p class="count-line" id="count" aria-live="polite">Showing all {len(personas)} people.</p>
<div class="cards">{''.join(cards)}</div>'''
filter_js = r'''<script>
(function(){
  var chips=document.querySelectorAll('.chip'), cards=document.querySelectorAll('[data-group]'), out=document.getElementById('count');
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.setAttribute('aria-pressed',x===c?'true':'false');});
    var f=c.dataset.f,n=0; cards.forEach(function(k){var show=f==='all'||k.dataset.group===f;k.hidden=!show;if(show)n++;});
    out.textContent='Showing '+n+' of '+cards.length+(f==='all'?'.':': '+c.firstChild.textContent+'.');
  });});
})();
</script>'''
page('people.html', 'RAHP People', 'people', 'People',
     'People', 'The people, organisations and AI agents in this catalogue. They are fictional, but each is built from evidence. They include people the system serves, people at the edges, and people who try to cause harm. Open a card to see their situations and the risks that reach them.',
     body, filter_js)

# ================= situations.html =================
def phase_key(s):
    m = re.search(r'Phase (\d)', s.get('lifecycle_phase') or '')
    return int(m.group(1)) if m else 9
by_phase = {}
for s in scen: by_phase.setdefault(s.get('lifecycle_phase') or 'Other', []).append(s)
order = sorted(by_phase.keys(), key=lambda k: (phase_key({'lifecycle_phase': k}), k))
blocks = []
for ph in order:
    items = []
    for s in by_phase[ph]:
        qs = [re.sub(r'^\d+\.\s*', '', q).strip() for q in (s.get('governance_decisions') or '').split('\n') if q.strip()]
        name = s['name']; main, _, subt = name.partition(' — ')
        lp = [plink(x) for x in s.get('legitimate_personas') or [] if x in P]
        ap = [plink(x) for x in s.get('adversarial_personas') or [] if x in P]
        rk = [rlink(r['id']) for r in scen_risks[s['id']]]
        items.append(f'''<details class="item" id="{s['id']}"><summary><span class="t">{E(main)}</span><span class="sub">{E(subt or s.get('lifecycle_phase',''))}</span><span class="tags">{f'<span class="pri">{len(rk)} risks</span>' if rk else ''}</span></summary>
<div class="body"><p>{E(s.get('description',''))}</p><div class="kv">
{kvsec('People it involves', ul(lp))}
{kvsec('Who could cause harm', ul(ap)) if ap else ''}
{kvsec('Questions the community must decide', '<ol>' + ''.join(f'<li>{E(q)}</li>' for q in qs) + '</ol>' if qs else '<p>None recorded.</p>')}
{kvsec('Risks this situation tests', ul(rk))}
</div>{gloss_links(s.get('description'), s.get('governance_decisions'))}<p class="ref">Reference in the files: {s['id']} · {E(s.get('lifecycle_phase',''))}</p></div></details>''')
    blocks.append(f'<h2 class="sec">{E(ph)}</h2><div class="items">{"".join(items)}</div>')
page('situations.html', 'RAHP Situations', 'situations', 'Situations', 'Situations',
     f'{len(scen)} situations that test a trust community, from founding to leaving. Each one names the people involved, who could cause harm, and the questions the community has to decide. They are grouped by the <a href="glossary.html#phases">phase of the community</a> they happen in.',
     ''.join(blocks))

# ================= risks.html =================
def rsort(r): return (0 if r['severity'] == 'Critical' else 1, -(score(r) or 0), r['name'])
ritems = []
for r in sorted(risks, key=rsort):
    sc = score(r)
    pr = 'Critical' if sc is None else f'Priority {sc} of 9'
    aff = [plink(p) for p in risk_people.get(r['id'], []) if role(p, r) == 'affected']
    cau = [plink(p) for p in risk_people.get(r['id'], []) if role(p, r) == 'causes']
    tst = [f'{E(T[t]["pass_criterion"])} <span style="color:var(--muted)">({"automated" if T[t].get("automated") else "checked by a person"})</span>' for t in r.get('assurance_tests') or [] if t in T]
    codes = ' · '.join([r['id']] + (r.get('guardrails') or []) + (r.get('controls') or []) + (r.get('affected_metrics') or []))
    ritems.append(f'''<details class="item" id="{r['id']}" data-sev="{r['severity']}" data-lik="{r['likelihood']}" data-cat="{E(cat(r['category']))}" data-text="{E((r['name']+' '+r['description']+' '+r.get('harm_description','')).lower())}">
<summary><span class="t">{E(r['name'])}</span><span class="sub">{E(cat(r['category']))} · {E(r.get('lifecycle_phase',''))}</span><span class="tags"><span class="sev {r['severity']}">{r['severity']}</span><span class="pri">{'Likelihood ' + r['likelihood'].lower() if sc is not None else 'Must be prevented'}</span></span></summary>
<div class="body"><p>{E(r['description'])}</p><div class="kv">
{kvsec('The harm', '<p>' + E(r.get('harm_description','')) + '</p><p style="color:var(--muted);margin-top:.3rem">Kinds of harm: ' + E(', '.join(r.get('harm_types') or [])) + '</p>')}
{kvsec('How serious, and how likely', f'<p><b>{r["severity"]}</b>' + (f', likelihood {r["likelihood"].lower()}: {pr}.' if sc is not None else ': must be prevented by a must-have and can never be accepted.') + (f' {PRIORITY.get(r.get("standards_priority"), "")}.' if r.get('standards_priority') else '') + '</p>')}
{kvsec('People it could harm', ul(aff)) if aff else ''}
{kvsec('People who could cause it', ul(cau)) if cau else ''}
{kvsec('Must-haves that guard against it', ul([glink(g) for g in r.get('guardrails') or []]))}
{kvsec('Safeguards that reduce it', ul([clink(c) for c in r.get('controls') or []]))}
{kvsec('Tests', ul(tst)) if tst else ''}
{kvsec('How you would know', ul([mlink(m) for m in r.get('affected_metrics') or []]))}
{kvsec('Situations that test it', ul([slink(s) for s in r.get('scenarios') or [] if s in S]))}
</div>{gloss_links(r['name'], r['description'], r.get('harm_description'))}<p class="ref">Reference in the files: {E(codes)}</p></div></details>''')
# heat map
cells = {}
for r in risks:
    if r['severity'] != 'Critical': cells[(r['severity'], r['likelihood'])] = cells.get((r['severity'], r['likelihood']), 0) + 1
ncrit = sum(1 for r in risks if r['severity'] == 'Critical')
heat = ['<div class="hd"></div>'] + [f'<div class="hd">{l} likelihood</div>' for l in ('Low', 'Medium', 'High')]
heat += ['<div class="hd rh">Critical</div>', f'<button type="button" class="crit" data-sev="Critical" data-lik="" data-n="{ncrit}" aria-pressed="false" aria-label="Show the {ncrit} critical risk{"s" if ncrit!=1 else ""}">{ncrit}</button>']
for sv in ('High', 'Medium', 'Low'):
    heat.append(f'<div class="hd rh">{sv} severity</div>')
    for lk in ('Low', 'Medium', 'High'):
        n = cells.get((sv, lk), 0); s_ = SCORE[sv] * SCORE[lk]
        heat.append(f'<button type="button" class="s{s_}" data-sev="{sv}" data-lik="{lk}" data-n="{n}" aria-pressed="false" aria-label="Show {n} risks with {sv.lower()} severity and {lk.lower()} likelihood"{" disabled" if n==0 else ""}>{n}</button>')
cats = sorted(set(cat(r['category']) for r in risks))
catchips = '<button type="button" class="chip" data-c="all" aria-pressed="true">All areas</button>' + ''.join(f'<button type="button" class="chip" data-c="{E(c)}" aria-pressed="false">{E(c)}</button>' for c in cats)
body = f'''<div class="layout2">
<div><h2 class="sec" style="margin-top:0">How serious, how likely</h2><p class="count-line">Choose a square to show those risks. Critical risks have no score: they must be prevented, whatever their likelihood.</p><div class="heat" role="group" aria-label="Risks by severity and likelihood">{''.join(heat)}</div></div>
<div><h2 class="sec" style="margin-top:0">Find a risk</h2>
<label for="q" class="count-line" style="display:block">Search the names and descriptions</label>
<input id="q" class="search" type="search" placeholder="For example: revocation, child, agent">
<div class="chips" role="group" aria-label="Area" style="margin-top:.8rem">{catchips}</div></div>
</div>
<p class="count-line" id="count" aria-live="polite" style="margin-top:1.5rem">Showing all {len(risks)} risks, most serious first.</p>
<div class="items" id="list">{''.join(ritems)}</div>'''
risk_js = r'''<script>
(function(){
  var items=[].slice.call(document.querySelectorAll('#list .item')), q=document.getElementById('q'), out=document.getElementById('count');
  var state={sev:null,lik:null,cat:'all',q:''};
  function apply(){
    var n=0; items.forEach(function(it){
      var ok=(!state.sev||it.dataset.sev===state.sev)&&(state.lik===null||state.lik===''||it.dataset.lik===state.lik)&&(state.cat==='all'||it.dataset.cat===state.cat)&&(!state.q||it.dataset.text.indexOf(state.q)>-1);
      it.hidden=!ok; if(ok)n++;});
    var bits=[]; if(state.sev)bits.push(state.sev.toLowerCase()+' severity'+(state.lik?', '+state.lik.toLowerCase()+' likelihood':'')); if(state.cat!=='all')bits.push(state.cat); if(state.q)bits.push('matching "'+state.q+'"');
    out.textContent='Showing '+n+' of '+items.length+' risks'+(bits.length?': '+bits.join('; '):', most serious first')+'.';
  }
  document.querySelectorAll('.heat button').forEach(function(b){b.addEventListener('click',function(){
    if(b.dataset.n==='0')return; var on=b.getAttribute('aria-pressed')!=='true';
    document.querySelectorAll('.heat button').forEach(function(x){x.setAttribute('aria-pressed','false');});
    if(on){b.setAttribute('aria-pressed','true');state.sev=b.dataset.sev;state.lik=b.dataset.lik;}else{state.sev=null;state.lik=null;}
    apply();});});
  document.querySelectorAll('[data-c]').forEach(function(c){c.addEventListener('click',function(){
    document.querySelectorAll('[data-c]').forEach(function(x){x.setAttribute('aria-pressed',x===c?'true':'false');}); state.cat=c.dataset.c; apply();});});
  q.addEventListener('input',function(){state.q=q.value.trim().toLowerCase();apply();});
})();
</script>'''
page('risks.html', 'RAHP Risks', 'risks', 'Risks', 'Risks',
     f'{len(risks)} things that could go wrong in a trust community, and for whom. Each risk shows the harm, how serious and how likely it is, who it reaches, and the safeguards and must-haves that answer it.',
     body, risk_js)

# ================= safeguards.html =================
gitems = []
for g in guards:
    tl = [f'{E(t["pass_criterion"])}. <span style="color:var(--muted)">How: {E(t.get("verification_method") or "")}</span>' for t in test_by_g.get(g['id'], [])]
    gitems.append(f'''<details class="item" id="{g['id']}"><summary><span class="t">{E(g['name'])}</span><span class="sub">{E(g.get('applies_to_phase',''))} · Owner: {E(g.get('owner',''))}</span><span class="tags"><span class="pri">Not yet triaged</span></span></summary>
<div class="body"><p>{E(g['requirement'])}</p><div class="kv">
{kvsec('Risks it guards against', ul([rlink(x) for x in g.get('risks_addressed') or []]))}
{kvsec('Safeguards that deliver it', ul([clink(x) for x in g.get('controls') or []]))}
{kvsec('How it is tested', ul(tl))}
</div>{gloss_links(g['requirement'])}<p class="ref">Reference in the files: {g['id']} · tests {', '.join(t['id'] for t in test_by_g.get(g['id'], [])) or 'none'}</p></div></details>''')
by_type = {}
for c in controls: by_type.setdefault(CTYPE.get(c['type'], c['type']), []).append(c)
cblocks = []
for t in ('Technical', 'Governance', 'Process', 'User experience', 'Legal'):
    its = []
    for c in by_type.get(t, []):
        its.append(f'''<details class="item" id="{c['id']}"><summary><span class="t">{E(c['name'])}</span><span class="sub">{E(t)} safeguard · relevance to standards: {E(str(c.get('standards_relevance') or 'not set').lower())}</span></summary>
<div class="body"><p>{E(c.get('description',''))}</p><div class="kv">
{kvsec('Risks it reduces', ul([rlink(x) for x in c.get('linked_risks') or []]))}
{kvsec('Must-haves it helps deliver', ul([glink(x) for x in c.get('guardrails') or []])) if c.get('guardrails') else ''}
</div>{gloss_links(c.get('description'))}<p class="ref">Reference in the files: {c['id']}</p></div></details>''')
    if its: cblocks.append(f'<h3 class="label" style="color:var(--mid);margin:1.4rem 0 .6rem">{E(t)} ({len(its)})</h3><div class="items">{"".join(its)}</div>')
mitems = []
for m in metrics:
    hi = [plink(x) for x in m.get('personas_want_high') or [] if x in P]; lo = [plink(x) for x in m.get('personas_want_suppressed') or [] if x in P]
    mitems.append(f'''<details class="item" id="{m['id']}"><summary><span class="t">{E(m['name'])}</span><span class="sub">{E(cat(m.get('category','')))}</span></summary>
<div class="body"><p>{E(m.get('description',''))}</p><div class="kv">
{kvsec('Who wants to see it', ul(hi)) if hi else ''}
{kvsec('Who would rather hide it', ul(lo)) if lo else ''}
{kvsec('Risks it measures', ul([rlink(x) for x in m.get('risks_measured') or []]))}
</div><p class="ref">Reference in the files: {m['id']}</p></div></details>''')
ritems2 = []
for x in recsn:
    linked = [glink(g) for g in x.get('linked_guardrails') or []] + [clink(c) for c in x.get('linked_controls') or []] + [rlink(r) for r in x.get('linked_risks') or []]
    ritems2.append(f'''<details class="item" id="{x['id']}"><summary><span class="t">{E(x['title'])}</span><span class="sub">{E((x.get('class') or '').capitalize())} · status: {E(x.get('status',''))}</span></summary>
<div class="body"><p>{E(x['statement'])}</p><div class="kv">{kvsec('Linked to', ul(linked))}</div>{gloss_links(x['statement'])}<p class="ref">Reference in the files: {x['id']}</p></div></details>''')
nun = sum(1 for x in controls + guards if x.get('standards_status') == 'unassigned')
body = f'''<ul class="subnav"><li><a href="#musthaves">Must-haves ({len(guards)})</a></li><li><a href="#safeguards">Safeguards ({len(controls)})</a></li><li><a href="#measures">Measures ({len(metrics)})</a></li><li><a href="#asks">What we ask of specifications ({len(recsn)})</a></li></ul>
<div class="banner" style="border-left-color:var(--draft)"><h2>{nun} of {len(controls)+len(guards)} safeguards and must-haves are not yet triaged</h2><p>Nobody has yet decided which should become requirements in a specification and which belong elsewhere. That is a task force decision, not an editorial one, so the toolkit leaves them all open rather than guessing.</p></div>
<h2 class="sec" id="musthaves">Must-haves</h2><p class="lead" style="margin:0 0 1rem">Yes-or-no conditions that must be met before a stage of a community can open. Each has at least one test.</p><div class="items">{''.join(gitems)}</div>
<h2 class="sec" id="safeguards">Safeguards</h2><p class="lead" style="margin:0 0 1rem">Measures that reduce risks. Many belong in governance, process or design, not in a specification.</p>{''.join(cblocks)}
<h2 class="sec" id="measures">Measures</h2><p class="lead" style="margin:0 0 1rem">What you would track to see whether safeguards are working, and who wants each one seen or hidden.</p><div class="items">{''.join(mitems)}</div>
<h2 class="sec" id="asks">What we ask of specifications</h2><p class="lead" style="margin:0 0 1rem">The task force's recommendations to the specification editors. All are proposals.</p><div class="items">{''.join(ritems2)}</div>'''
page('safeguards.html', 'RAHP Safeguards', 'safeguards', 'Safeguards', 'Safeguards and must-haves',
     'What answers the risks: must-haves that gate each stage, safeguards that reduce risk, measures that show whether they work, and what the task force asks of specifications.', body)

# ================= affected.html =================
SHORT={'served':'Served','edge':'Edge case','machine':'AI agent','harm':'Causes harm'}
pcols = [p for g, _ in groups for p in personas if pgroup(p) == g]
head = '<th scope="col">Risk</th>' + ''.join(f'<th scope="col"><a href="people.html#{p["id"]}">{E(p["name"])}</a><small>{E(SHORT[pgroup(p)])}</small></th>' for p in pcols)
rows = []
for c in sorted(set(cat(r['category']) for r in risks)):
    rows.append(f'<tr class="grp"><th scope="rowgroup" colspan="{len(pcols)+1}">{E(c)}</th></tr>')
    for r in sorted([r for r in risks if cat(r['category']) == c], key=rsort):
        tds = []
        for p in pcols:
            if p['id'] in risk_people.get(r['id'], []):
                ro = role(p['id'], r)
                tds.append(f'<td class="{"a" if ro=="affected" else "c"}"><span aria-hidden="true">{"&#9679;" if ro=="affected" else "&#9650;"}</span><span class="vh">{"Could be harmed" if ro=="affected" else "Could cause it"}</span></td>')
            else: tds.append('<td><span class="vh">No link</span></td>')
        rows.append(f'<tr><th scope="row"><a href="risks.html#{r["id"]}">{E(r["name"])}</a> <span class="sev {r["severity"]}" style="font-size:.58rem">{r["severity"]}</span></th>{"".join(tds)}</tr>')
body = f'''<ul class="legend" aria-label="Key"><li><span style="color:var(--brand);font-size:1.1rem" aria-hidden="true">&#9679;</span><span><b>Could be harmed</b> by this risk</span></li><li><span style="color:var(--alert)" aria-hidden="true">&#9650;</span><span><b>Could cause</b> this risk, or exploit it</span></li></ul>
<p class="count-line">Rows are risks, grouped by area. Columns are people, from those the system serves to those who cause harm. Scroll sideways and down; the names stay in view. Choose a name to see the full record.</p>
<div class="mx-wrap" tabindex="0" role="region" aria-label="Who is affected by what, scrolls in both directions"><table class="mx"><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p class="count-line" style="margin-top:1rem">A person is linked to a risk when the risk appears in their stories or in a situation they take part in. The links are worked out from the data each time the site is built.</p>'''
page('affected.html', 'RAHP Who Is Affected', 'affected', 'Who is affected', 'Who is affected by what',
     'Every risk against every person in the catalogue: who could be harmed, and who could cause the harm. This replaces the old cross-reference matrix of stories and metrics.', body)

# ================= lifecycle.html =================
st = life['records']
step = ''.join(f'<li><a href="#{s["id"]}">{E(s["name"])}</a><p>{E(s["summary"].split(".")[0])}.</p></li>' for s in st)
SEVG = {'blocking': 'Blocking', 'method': 'Method gap', 'deferred_by_design': 'Deferred by design'}
blocks = []
for s in st:
    sub = s.get('phases') or s.get('stations') or s.get('tracks') or []
    subl = ''.join(f'<li><span><b>{E(x["name"])}</b>' + (f'. {E(x["note"])}' if x.get('note') else '') + (f' Compared against: {E(", ".join(x["compare_against"]))}.' if x.get('compare_against') else '') + '</span></li>' for x in sub)
    extra = ''
    if s.get('invariants'): extra += kvsec('Rules that always apply', ul([E(i) for i in s['invariants']]))
    if s.get('trigger_streams'): extra += kvsec('What triggers a review', ul([E(i['name']) for i in s['trigger_streams']]))
    if s.get('required_components'): extra += kvsec('Required parts', ul([f'<b>{E(i["name"])}</b>. {E(i.get("note",""))}' for i in s['required_components']]))
    gaps = ''.join(f'<div class="gap {g.get("severity","")}"><b>{SEVG.get(g.get("severity"), g.get("severity",""))}</b> {E(g["description"])}' + (f'<br><span style="color:var(--muted)">Being addressed by: {E(g["addressed_by"])}</span>' if g.get('addressed_by') else '') + f'<span class="ref" style="display:block">Reference: {g["id"]}</span></div>' for g in s.get('gaps') or [])
    blocks.append(f'''<article class="stage" id="{s['id']}"><p class="label" style="color:var(--mid);margin:0">Stage {s['id'].split('-')[1]}</p><h3>{E(s['name'])}</h3><p>{E(s['summary'])}</p>
<p class="note" style="margin-top:.6rem"><b>In the review journey:</b> {E(STAGE_MAP[s['id']][0])}. {E(STAGE_MAP[s['id']][1])} {('Guides: ' + ', '.join([f'<a href="guide-without-ai.html#{x}">without AI, step {x[2:]}</a>' for x in STAGE_MAP[s['id']][2]][:1] + [f'<a href="guide-with-ai.html#{x}">with AI, step {x[2:]}</a>' for x in STAGE_MAP[s['id']][3]][:1]) + '.') if STAGE_MAP[s['id']][2] else '<a href="index.html#journey">See step 17 in the journey</a>.'}</p>
{'<ol class="substeps">'+subl+'</ol>' if subl else ''}
<div class="grid3 kv">{kvsec('Starts from', ul([E(i) for i in s.get('input_artefacts') or []]))}{kvsec('Must produce', ul([E(i) for i in s.get('required_outputs') or []]))}{kvsec('Evidence needed', '<p>'+E(s.get('evidence_required',''))+'</p>')}</div>
<div class="kv">{extra}</div>
<h4 class="label" style="color:var(--mid);margin:1.2rem 0 .2rem">Known gaps in the method</h4>{gaps}</article>''')
body = f'''<div class="banner" style="border-left-color:var(--brand);background:var(--mint-soft)"><h2>People and context drive everything</h2><p>{E(life['core_principle'])}</p></div>
<h2 class="sec" style="margin-top:0">Where a specification review fits</h2><p class="lead" style="margin:0 0 1rem">A review of a specification runs across the five stages. The table maps the <a href="index.html#journey">review journey</a> and the step-by-step guides (<a href="guide-without-ai.html">without AI</a>, <a href="guide-with-ai.html">with AI</a>) onto the stages. This mapping is a proposal for the task force.</p>
<div class="table-wrap" style="margin-bottom:2rem"><table class="wordmap"><thead><tr><th scope="col">Stage</th><th scope="col">Journey steps</th><th scope="col">What you do in the review</th></tr></thead><tbody>{''.join(f'<tr><td><a href="#{x["id"]}">{x["id"].split("-")[1]}. {E(x["name"])}</a></td><td>{E(STAGE_MAP[x["id"]][0])}</td><td>{E(STAGE_MAP[x["id"]][1])}</td></tr>' for x in st)}</tbody></table></div>
<ol class="stepper">{step}</ol>{''.join(blocks)}'''
page('lifecycle.html', 'RAHP Lifecycle', 'lifecycle', 'Lifecycle', 'The five stages',
     'How RAHP runs across the five stages of developing a standard, what each stage must produce, and the gaps in the method that are still open.', body)

# ================= decisions.html =================
arows = []
for a in accepts:
    arows.append(f'''<details class="item" id="{a['id']}" open><summary><span class="t">{E(a['title'])}</span><span class="sub">Risk: {E(R[a['risk_id']]['name']) if a['risk_id'] in R else E(a['risk_id'])}</span><span class="tags"><span class="pill todo">{E(a['decision'].capitalize())}</span></span></summary>
<div class="body"><p>{E(a.get('rationale') or '')}</p><div class="kv">
{kvsec('Risk', '<p>'+rlink(a['risk_id'])+'</p>')}
{kvsec('Who decides', '<p>Not yet decided. The working group has not agreed who may accept a risk.</p>' if not a.get('authority') else '<p>'+E(a['authority'])+'</p>')}
{kvsec('Conditions', ul([E(c) for c in a.get('conditions') or []])) if a.get('conditions') else ''}
{kvsec('What it is waiting for', ul([E(b) for b in (a.get('blocked_by') if isinstance(a.get('blocked_by'), list) else [a.get('blocked_by')]) if b])) if a.get('blocked_by') else ''}
{kvsec('Evidence', '<p>'+E(a['evidence'])+'</p>') if a.get('evidence') else ''}
</div><p class="ref">Reference in the files: {a['id']} · {a['risk_id']}</p></div></details>''')
prows = []
for g in precs:
    linked = [rlink(r) for r in g.get('linked_risks') or []] + [glink(x) for x in g.get('linked_guardrails') or []] + [clink(x) for x in g.get('linked_controls') or []]
    prows.append(f'''<details class="item" id="{g['id']}"><summary><span class="t">{E(g['title'])}</span><span class="sub">{E(str(g.get('decision_date') or ''))}</span><span class="tags"><span class="pill todo">{E(g['status'].capitalize())}</span></span></summary>
<div class="body"><div class="kv">{kvsec('Background', '<p>'+E(g.get('context',''))+'</p>')}{kvsec('Why', '<p>'+E(g.get('rationale',''))+'</p>')}{kvsec('Linked to', ul(linked))}</div>{gloss_links(g.get('context'), g.get('rationale'))}<p class="ref">Reference in the files: {g['id']}</p></div></details>''')
body = f'''<div class="banner"><h2>No risk has been formally accepted</h2><p>All {len(accepts)} decisions below are pending. The working group has not yet agreed who may accept a risk, under what authority, or on what evidence. Until it does, one of the toolkit's own tests cannot pass. Critical risks can never be accepted.</p></div>
<h2 class="sec">Risk decisions</h2><p class="lead" style="margin:0 0 1rem">Risks the specification cannot yet reduce, waiting for a decision to accept them or to require a fix.</p><div class="items">{''.join(arows)}</div>
<h2 class="sec">Precedents</h2><p class="lead" style="margin:0 0 1rem">Earlier decisions that explain why the toolkit looks the way it does. All are still proposals.</p><div class="items">{''.join(prows)}</div>'''
page('decisions.html', 'RAHP Decisions', 'decisions', 'Decisions', 'Decisions',
     'Who decides about risk, and what has been decided so far. Deciding is a step for people by rule: no tool or AI can do it.', body)

# ================= glossary.html =================
wm = [('Person', 'Persona', 'D, M, B, EC'), ('Situation', 'Scenario', 'SC-'), ('Risk', 'Risk', 'RK-'), ('Safeguard', 'Control', 'CT-'),
      ('Must-have', 'Guardrail', 'GR-'), ('Test', 'Assurance test', 'AT-'), ('Measure', 'Metric', 'M-'), ('Story', 'User story', 'US-'),
      ('Group of stories', 'Epic', 'EPIC-'), ('Ask of a specification', 'Recommendation', 'REC-'), ('Risk decision', 'Risk acceptance', 'RA-'), ('Precedent', 'Governance precedent', 'GP-')]
sevs = ''.join(f'<div id="sev-{v["value"].lower()}"><h3>{E(v["value"])}</h3><p>{E(v["definition"])}</p></div>' for v in vocab['severity']['values'])
gl = ''.join(f'<div id="{g}"><h3>{E(n)}</h3><p>{E(d)}</p></div>' for g, n, d, _ in sorted(GLOSS, key=lambda x: x[1].lower()))
body = f'''<h2 class="sec" style="margin-top:0">Words on this site, and in the files</h2><p class="lead" style="margin:0 0 1rem">This site uses plain words. The toolkit's files use standard terms and short codes. This table matches them up.</p>
<div class="table-wrap"><table class="wordmap"><thead><tr><th scope="col">On this site</th><th scope="col">In the files</th><th scope="col">Code starts with</th></tr></thead><tbody>{''.join(f'<tr><td>{a}</td><td>{b}</td><td class="mono">{c}</td></tr>' for a,b,c in wm)}</tbody></table></div>
<h2 class="sec">How serious a risk is</h2><div class="gloss">{sevs}</div>
<h2 class="sec">Terms</h2><div class="gloss">{gl}</div>
<p class="count-line" style="margin-top:1rem">Definitions are drawn from the toolkit's key terms and sources, in plain words. See the User Stories Framework and the VTC Bootstrapping Draft for the originals.</p>'''
page('glossary.html', 'RAHP Words', 'glossary', 'Words', 'Words and codes',
     'Plain explanations of the terms used across the toolkit, and how the words on this site match the terms and codes in the files.', body)

print('pages built; persona D1 risks:', sorted(r['id'] for r in people_risks['D1']))

# ================= examples =================
# Sources (see BRIEF_ClaudeWin_RAHP_Pages_Examples_v0.1.md): examples/EXAMPLES_STATUS.md, examples/linux-case/findings.json,
# site/examples/arthur-margaret/ (the public version; the private source is never published), review-reports manifests, and upstream review/examples/.
import json as _json
EX_PAGES = []
if EXDIR:
    STATES = [('AI draft', 'An AI drafted the findings. No person has reviewed them yet.'),
              ('Checked by a person', 'The accountable reviewer has reviewed the findings.'),
              ('Independently examined', "Someone who didn't prepare the review has tried to disprove each inference."),
              ('Accepted by the task force', 'The task force has decided what to do with the findings.')]
    CHECK_NOTE = 'Passing the toolkit\'s checks means a record is well formed, not that its findings are right.'
    PLANES = ['Technical standards', 'Implementation', 'Configuration', 'Governance', 'User experience']
    CP = {'specification': 'Technical standards', 'companion-specification': 'Technical standards', 'implementation-guidance': 'Implementation',
          'runtime-control': 'Configuration', 'governance': 'Governance', 'operational-policy': 'Governance', 'none': 'Governance'}
    BUCKET = {'technical standards': 'Technical standards', 'implementation': 'Implementation', 'governance': 'Governance', 'UX': 'User experience'}
    WHO = {'H': ('h', 'Person'), 'H*': ('r', 'Person, by rule'), 'AI': ('ai', 'AI'), 'M': ('m', 'Machine'), 'H+AI': ('h', 'Person with AI'),
           'M/AI, H checks': ('m', 'Machine and AI; a person checks'), 'H+AI, M': ('h', 'Person with AI; machine')}
    LXS = {'SAYS': ('&#9679;', 'Addressed', 'done'), 'PARTIAL': ('&#9680;', 'Partly addressed', 'partly'), 'MISSING': ('&#9675;', 'Missing', 'notyet'),
           'DEFERRED': ('&#8594;', 'Handed elsewhere', 'na'), 'CONTRADICTS': ('&#10005;', 'Contradicts', 'notyet')}
    PATHS = {'A': 'Dewi (honest contributor)', 'B': 'Kestrel (patient insider)', 'C': 'AI agents', 'all': 'All paths'}
    EXCSS = '''<style>
.stateline{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0}
.stateline li{border-top:6px solid var(--line);padding:.6rem .8rem .2rem;font-size:.9rem;color:var(--muted)}
.stateline li b{display:block;color:var(--fg);font-family:var(--font-display);font-size:.85rem}
.stateline li.done{border-top-color:var(--brand)}
.stateline li.now{border-top-color:var(--brand);background:var(--mint-soft)}
.stateline li.now b::after{content:" \\2190  here";color:var(--brand)}
.statebox{border:1px solid var(--line);border-left:6px solid var(--draft);background:var(--draft-bg);border-radius:var(--radius);padding:1rem 1.2rem;margin-bottom:1rem}
.statebox h2{font-size:1.15rem;font-weight:800;margin:0 0 .3rem}
.statebox p{margin:.3rem 0 0}
.facts{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,260px),1fr));gap:.8rem;margin:1rem 0}
.facts>div{background:var(--bg);border:1px solid var(--line);border-radius:var(--radius);padding:.8rem 1rem;min-width:0}
.facts h4{font-family:var(--font-display);font-weight:800;font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:var(--mid);margin:0 0 .3rem}
.facts p{margin:0;font-size:.95rem}
.whodid{list-style:none;margin:0;padding:0;display:grid;gap:.4rem}
.whodid li{display:grid;grid-template-columns:1.6rem minmax(0,1fr) auto;gap:.6rem;align-items:center;background:var(--bg);border:1px solid var(--line);border-radius:var(--radius);padding:.5rem .8rem}
.whodid .who{font-size:.85rem;color:var(--muted)}
.lxs{font-weight:800}
.themes{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr));gap:1rem}
.theme{border:1px solid var(--line);border-radius:var(--radius);background:var(--bg);padding:1rem 1.1rem;display:grid;gap:.4rem;min-width:0;scroll-margin-top:90px}
.theme h3{font-size:1.05rem;font-weight:800}
.theme .verdict{font-weight:700;color:var(--alert)}
.theme p{margin:0;font-size:.94rem}
.excards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr));gap:1rem}
.excard{border:1px solid var(--line);border-radius:var(--radius);background:var(--bg);padding:1.1rem 1.2rem;display:flex;flex-direction:column;gap:.6rem;min-width:0}
.excard h3{font-size:1.1rem;font-weight:800}
.excard p{margin:0;font-size:.95rem}
.excard .q{font-style:italic}
.excard .go{margin-top:auto;font-family:var(--font-display);font-weight:800;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase}
.minisl{display:flex;gap:3px;margin:0;padding:0;list-style:none}
.minisl li{flex:1;height:6px;background:var(--line);border-radius:2px}
.minisl li.on{background:var(--brand)}
@media (max-width:640px){.stateline{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>'''

    def stateline(n, training=False):
        if training:
            return '<p class="flag"><b>Training only.</b> A fictional exercise to show how to apply RAHP. It is not an assessment, so it has no review state.</p>'
        lis = ''.join(f'<li class="{"now" if i == n else ("done" if i < n else "")}"><b>{i}. {E(t)}</b>{E(d)}</li>' for i, (t, d) in enumerate(STATES, 1))
        return f'<ol class="stateline" aria-label="Review state: {n} of 4, {E(STATES[n-1][0])}">{lis}</ol>'
    def minisl(n):
        return '<ul class="minisl" aria-hidden="true">' + ''.join(f'<li class="{"on" if i <= n else ""}"></li>' for i in range(1, 5)) + '</ul>'
    def whodid(steps):
        out = []
        for st in steps:
            k, lab = WHO.get(st['who'], ('h', st['who']))
            d = str(st.get('done')).lower()
            stt = {'yes': ('done', 'Done'), 'true': ('done', 'Done'), 'no': ('notyet', 'Not done'), 'false': ('notyet', 'Not done'),
                   'drafted': ('after', 'Drafted afterwards')}.get(d, ('na', d))
            out.append(f'<li><span class="mk {k}" aria-hidden="true"></span><span>{E(st["step"])}<br><span class="who">{E(lab)}</span></span><span class="st {stt[0]}">{stt[1]}</span></li>')
        return '<ul class="whodid">' + ''.join(out) + '</ul><p class="count-line" style="margin-top:.6rem">Shapes: circle, a person; dark bar, a person by rule; diamond, AI; hatched square, a machine. See <a href="index.html#journey">the journey</a> for every step.</p>'
    def rlinks(ids):
        return ', '.join(rlink(r) if r in R else f'{E(r)} <span style="color:var(--muted)">(proposed, not in the catalogue)</span>' for r in ids) or 'None'
    def plane_groups(items, plane_of, render):
        html = ''
        for pl in PLANES:
            its = [x for x in items if plane_of(x) == pl]
            if not its: continue
            html += f'<h3 class="label" style="color:var(--mid);margin:1.4rem 0 .6rem">{pl} ({len(its)})</h3><div class="items">' + ''.join(render(x) for x in its) + '</div>'
        return html
    def commit_link(repo, rev):
        repo_url = repo if repo.startswith('http') else f'https://github.com/{repo}'
        return f'<a href="{E(repo_url)}/commit/{E(rev)}" rel="noopener">{E(rev[:7])}</a>'
    def sec(title, inner, id_=''):
        return f'<h2 class="sec"{f" id={chr(34)}{id_}{chr(34)}" if id_ else ""}>{E(title)}</h2>{inner}'
    def manifest(name):
        if not MANIFESTS: return {}
        p = os.path.join(MANIFESTS, f'manifest-{name}.yaml')
        return yaml.safe_load(open(p)) if os.path.exists(p) else {}

    def expage(fname, title, h1, lead, n, statebox, body, training=False):
        EX_PAGES.append(fname)
        page(fname, title, 'examples', 'Examples', h1, lead,
             EXCSS + f'<p class="crumbs" style="margin:0 0 1rem"><a href="examples.html">All examples</a></p>{stateline(n, training)}<div style="height:1rem"></div>{statebox}{body}')

    cards = []
    # ---- Linux case ----
    lx = _json.load(open(os.path.join(EXDIR, 'linux-case', 'findings.json')))
    meta = lx['meta']; mlx = manifest('linux-case')
    reviewed = ''.join(f'<li><b>{E(s_["name"])}</b>, {E(s_["status"])}, commit <span class="mono">{E(s_["commit"])}</span> <span class="ref" style="display:inline">({E(s_["review"])})</span></li>' for s_ in meta['specs'])
    commits = ', '.join(f'{s_["name"]} {s_["commit"]}' for s_ in meta['specs'])
    label_lx = f'AI draft, not yet reviewed by Nicky Hickman. {E(meta["date"])}. Specification commits: {E(commits)}.'
    def lxf(f):
        sym, txt, cls = LXS[f['status_label']]
        return (f'<details class="item" id="{f["id"]}" data-spec="{E(f["spec"])}" data-path="{E(f["path"])}"><summary><span class="t">{E(f["finding"])}</span>'
                f'<span class="sub">{E(f["spec"])} · {E(PATHS.get(f["path"], f["path"]) if f["path"] in PATHS else ", ".join(PATHS.get(x.strip(), x) for x in f["path"].split(",")))}</span>'
                f'<span class="tags"><span class="st {cls}"><span class="lxs" aria-hidden="true">{sym}</span> {txt}</span></span></summary>'
                f'<div class="body"><div class="kv">{kvsec("Where in the specification", "<p class=mono>" + E(f["evidence"].replace("`", "")) + "</p>")}'
                f'{kvsec("Risks", "<p>" + rlinks(f["risks"]) + "</p>")}{kvsec("Who must act", "<p>" + E(f["who_must_act"]) + "</p>")}'
                f'{kvsec("Where the fix belongs", "<p>" + E(f["bucket"]) + "</p>")}{kvsec("How sure the AI was", "<p>" + E(f["confidence"].capitalize()) + "</p>")}</div>'
                f'<p class="ref">AI draft, not yet reviewed by Nicky Hickman · Reference: {f["id"]}</p></div></details>')
    def lxplane(f): return BUCKET.get(re.split(r'\s*[/+]\s*', f['bucket'])[0], 'Governance')
    specs = sorted(set(f['spec'] for f in lx['findings']), key=lambda x: [s_['name'] for s_ in meta['specs']].index(x) if x in [s_['name'] for s_ in meta['specs']] else 9)
    specs = [s_['name'] for s_ in meta['specs']]
    fspec = sorted(set(f['spec'] for f in lx['findings']))
    chips_s = '<button type="button" class="chip" data-k="spec" data-v="all" aria-pressed="true">All specifications</button>' + ''.join(f'<button type="button" class="chip" data-k="spec" data-v="{E(x)}" aria-pressed="false">{E(x)}</button>' for x in fspec)
    chips_p = '<button type="button" class="chip" data-k="path" data-v="all" aria-pressed="true">All paths</button>' + ''.join(f'<button type="button" class="chip" data-k="path" data-v="{k}" aria-pressed="false">{E(v)}</button>' for k, v in [('A', 'Dewi'), ('B', 'Kestrel'), ('C', 'AI agents')])
    counts = {}
    for f in lx['findings']: counts.setdefault(f['status_label'], {}).setdefault(f['spec'], 0); counts[f['status_label']][f['spec']] += 1
    ctab = '<div class="table-wrap"><table class="wordmap"><thead><tr><th scope="col">What the specification does</th>' + ''.join(f'<th scope="col">{E(x)}</th>' for x in fspec) + '<th scope="col">Total</th></tr></thead><tbody>' + ''.join(
        f'<tr><td><span aria-hidden="true">{LXS[k][0]}</span> {LXS[k][1]}</td>' + ''.join(f'<td>{counts.get(k, {}).get(x, 0)}</td>' for x in fspec) + f'<td><b>{sum(counts.get(k, {}).values())}</b></td></tr>' for k in LXS) + '</tbody></table></div>'
    themes = ''.join(f'''<article class="theme" id="{t['id']}"><p class="label" style="color:var(--mid);margin:0">Theme {t['id'][1:]} · {E(t.get('persona',''))}</p><h3>{E(t['title'])}</h3><p class="verdict">{E(t['verdict'])}</p><p>{E(t['summary'])}</p><p style="color:var(--muted);font-size:.88rem"><b>No one owns it:</b> {E(t.get('owner_gap',''))}</p><p style="font-size:.86rem">Findings: {', '.join(f'<a href="#{x}">{x}</a>' for x in t['findings'])}</p></article>''' for t in lx['themes'])
    localr = ul([f'<b>{E(r_["id"])}</b>: {E(r_["description"])} <span style="color:var(--muted)">Raised by {E(r_["raised_by"])}</span>' for r_ in lx['local_risks']])
    peeps = ''.join(f'<li>{plink(x)}</li>' for x in (mlx.get('catalogue_personas') or ['D3', 'B1', 'M1', 'M2']) if x in P)
    body = f'''<div class="facts">
<div><h4>The question</h4><p>{E(mlx.get('question') or meta['scenario'])}</p></div>
<div><h4>Source</h4><p>{E(meta['source'])}. The Linux kernel maintainers run a trust community; maintainer rights need a personhood credential and two vouches.</p></div>
<div><h4>Reviewer's lens</h4><p>{E(meta['reviewer_persona'])}, an honest contributor joining from Jakarta. Threat: {E(meta['threat_persona'])}. See <a href="index.html#ways-in">the toolkit personas</a>.</p></div>
<div><h4>People from the catalogue</h4><ul>{peeps}</ul></div>
</div>
{sec('What was reviewed', '<p>Three draft specifications, each reported against an exact commit, one review record each:</p><ul>' + reviewed + '</ul><p class="flag">The underlying review records and their validation evidence are not retained in this repository. The reported checks cannot be independently reproduced from this public site. ' + CHECK_NOTE + '</p>')}
{sec('Who did what', whodid(mlx.get('steps', [])))}
{sec('What the specifications do', '<p class="lead" style="margin:0 0 .8rem">57 findings, labelled by what each specification does about the issue. Labels use shapes and words.</p>' + ctab)}
{sec('Ten themes across the specifications', '<p class="lead" style="margin:0 0 1rem">A review record holds one specification, so these themes sit outside the format. They are AI-drafted too.</p><div class="themes">' + themes + '</div>', 'themes')}
{sec('Findings, by where the fix belongs', '<div class="toolbar" style="margin-top:.6rem"><div class="chips" role="group" aria-label="Specification">' + chips_s + '</div><div class="chips" role="group" aria-label="Path">' + chips_p + '</div></div><p class="count-line" id="count" aria-live="polite">Showing all 57 findings.</p><div id="flist">' + plane_groups(lx['findings'], lxplane, lxf) + '</div>', 'findings')}
{sec('Proposed new risks', '<p class="lead" style="margin:0 0 .6rem">Not in the catalogue. Local to this example until the task force decides.</p>' + localr)}
{sec('Limits and next steps', ul(['The findings are AI-drafted. One AI agent read each specification. 27 cited lines were spot-checked and all matched, but that checks the quotations, not the judgements.', 'No person has reviewed the findings yet. Next: Nicky Hickman reviews them as the personas\' advocate.', 'The Trust Tasks registry repository, which holds the per-task specifications, was not read.', 'The Verifiable Trust Infrastructure (VTI) was not in scope, though several gaps are handed to it.', 'The specifications are moving: Credentials changed on the day of the review, and ZKP is an early working draft.']))}'''
    flt_js = r'''<script>(function(){var st={spec:'all',path:'all'},it=[].slice.call(document.querySelectorAll('#flist .item')),out=document.getElementById('count');
document.querySelectorAll('[data-k]').forEach(function(c){c.addEventListener('click',function(){document.querySelectorAll('[data-k="'+c.dataset.k+'"]').forEach(function(x){x.setAttribute('aria-pressed',x===c?'true':'false');});st[c.dataset.k]=c.dataset.v;var n=0;
it.forEach(function(i){var ok=(st.spec==='all'||i.dataset.spec===st.spec)&&(st.path==='all'||i.dataset.path.indexOf(st.path)>-1||i.dataset.path==='all');i.hidden=!ok;if(ok)n++;});
document.querySelectorAll('#flist h3').forEach(function(h){var g=h.nextElementSibling;h.hidden=g.querySelectorAll('.item:not([hidden])').length===0;g.hidden=h.hidden;});
out.textContent='Showing '+n+' of '+it.length+' findings.';});});})();</script>'''
    expage('ex-linux.html', 'RAHP Example: Linux Case', 'Linux case study: Dewi and Kestrel',
           'One situation run against three Decentralized Trust Graph specifications at once: can an honest contributor get in from far away, and can a patient insider be stopped?',
           1, f'<div class="statebox"><h2>State 1 of 4: AI draft</h2><p><b>{label_lx}</b></p><p>AI agents drafted all 57 findings and 10 themes. Nobody has reviewed them yet, examined them independently or decided anything about them. Read them as a draft, not a verdict.</p></div>',
           body + flt_js)
    cards.append(('ex-linux.html', 'Linux case study: Dewi and Kestrel', mlx.get('question', ''), 'One situation against three specifications at once: 57 findings and 10 themes that cut across them.', 1, 'AI draft, not yet reviewed by Nicky Hickman', False))

    # ---- Arthur and Margaret (public version only) ----
    am = _json.load(open(os.path.join(EXDIR, 'arthur-margaret', 'example.json')))
    def amf(f):
        return (f'<details class="item" id="{f["id"]}"><summary><span class="t">{E(f["title"])}</span><span class="sub">{E(f["plane"])}</span></summary>'
                f'<div class="body"><p>{E(f["finding"])}</p><div class="kv">{kvsec("Evidence", "<p>" + E(f.get("evidence", "")) + "</p>")}'
                f'{kvsec("Limits", ul([E(x) for x in f.get("limits") or []]))}{kvsec("Risks", "<p>" + rlinks(f.get("risks") or []) + "</p>")}'
                f'{kvsec("Who must act", "<p>" + E(f.get("who", "")) + "</p>")}{kvsec("Next step", "<p>" + E(f.get("next_step", "")) + "</p>")}</div>'
                f'<p class="ref">Reference: {f["id"]}</p></div></details>')
    def amplane(f):
        p_ = f['plane']
        return 'Technical standards' if p_.startswith('Technical standards') else 'Implementation' if 'implementation' in p_.lower() else 'Configuration' if p_.startswith('Config') else 'Governance' if p_.startswith('Gov') else 'User experience'
    am_steps = [{'step': 'Choose the people and situations', 'who': 'H', 'done': 'yes'},
                {'step': 'Gather catalogue context; search the code and documentation; draft findings', 'who': 'AI', 'done': 'yes'},
                {'step': 'Pin the repositories; validate the record; fingerprint the evidence', 'who': 'M', 'done': 'yes'},
                {'step': 'Confirm, change or drop each finding', 'who': 'H*', 'done': 'yes'},
                {'step': 'Re-check the code evidence', 'who': 'H', 'done': 'no'},
                {'step': 'Independent examination', 'who': 'H*', 'done': 'no'},
                {'step': 'Interpret and decide (task force)', 'who': 'H*', 'done': 'no'}]
    am_people = ''.join(f'<li>{plink(k)}: {E(v)}</li>' for k, v in am['people'].items() if k in P)
    am_sc = ''.join(f'<li>{slink(x.split(" ")[0])}</li>' for x in am['scenarios'] if x.split(' ')[0] in S)
    body = f'''<div class="facts">
<div><h4>The question</h4><p>Arthur has early-stage dementia. Margaret, his partner and carer, holds registered lasting powers of attorney. Can Arthur stay a member of his community, and can Margaret act for him lawfully, visibly and within limits? Does the system protect him?</p></div>
<div><h4>What was reviewed</h4><p>An open-source trust-community implementation stack. It isn't named here. The review record pins its three repositories to exact commits and is kept privately.</p></div>
<div><h4>The people</h4><ul>{am_people}</ul></div>
<div><h4>Situations</h4><ul>{am_sc}</ul></div>
</div>
<p class="flag">The source review record and evidence are private. Its preparer reports that the record passed RAHP validation, but this public example cannot independently reproduce that result. {CHECK_NOTE}</p>
{sec('Who did what', '<p class="lead" style="margin:0 0 .8rem">This review started from people, not from code: the route a non-technical, human-focused reviewer would take.</p>' + whodid(am_steps))}
{sec('Findings, by where the fix belongs', '<p class="lead" style="margin:0 0 .5rem">Eight findings across all five places a fix can belong.</p>' + plane_groups(am['findings'], amplane, amf), 'findings')}
{sec('What this example teaches about the toolkit', ul(['The record format strains to hold an implementation review: a record holds one repository, but this stack has three, and there are no fields for evidence, the person affected or who must act.', 'The toolkit has no place yet for fixes in user experience, so two findings had to be filed as implementation guidance.', 'Two findings rest on proposed risks that are not in the catalogue yet: coercion by someone close, and abuse of delegated authority.', 'Protection can create risk: a second notice recipient protects Arthur, but could expose someone under coercive control.']))}
{sec('Next steps', ul(['Re-check the code evidence behind each finding.', 'Independent examination by someone who did not prepare the review.', 'The task force decides where the fixes go.']))}'''
    expage('ex-arthur-margaret.html', 'RAHP Example: Arthur and Margaret', 'Arthur and Margaret',
           'A persona-led review of an implementation: a person living with dementia, and the partner who holds his lasting power of attorney.',
           2, f'<div class="statebox"><h2>State 2 of 4: checked by a person</h2><p>{E(am["state_detail"])}</p><p>Not yet independently examined, and not yet considered by the task force.</p></div>', body)
    cards.append(('ex-arthur-margaret.html', 'Arthur and Margaret', 'Can Arthur stay a member as his capacity declines, and can Margaret act for him lawfully, visibly and within limits?', 'A persona-led review of an implementation: 8 findings across all five places a fix can belong.', 2, 'Checked by a person. Code evidence not re-checked', False))

    # ---- upstream examples ----
    RT = {'already-addressed': 'already addressed by the specification', 'specification-change': 'the specification was changed', 'governance-action': 'a governance action'}
    def upf(f):
        res = f.get('resolution') or {}
        stt = ('done', 'Resolved: ' + RT.get(res.get('type'), res.get('type', ''))) if f.get('status') == 'resolved' else ('notyet', (f.get('status') or 'open').replace('_', ' ').capitalize())
        ref = res.get('reference') or ''
        refh = f'<a href="{E(ref)}" rel="noopener">source</a>' if ref.startswith('http') else E(ref)
        return (f'<details class="item" id="{f["id"]}"><summary><span class="t">{E(f["summary"])}</span><span class="sub">{E(CP.get(f.get("control_plane"), ""))}</span><span class="tags"><span class="st {stt[0]}">{E(stt[1])}</span></span></summary>'
                f'<div class="body"><div class="kv">{kvsec("Risks", "<p>" + rlinks(f.get("risks") or []) + "</p>")}'
                + (kvsec('Why it was closed', '<p>' + E(res.get('rationale', '')) + (f' ({refh})' if ref else '') + '</p>') if res else '')
                + f'</div><p class="ref">Reference: {f["id"]} · where the fix belongs: {E(f.get("control_plane", ""))}</p></div></details>')
    def upplane(f): return CP.get(f.get('control_plane'), 'Governance')
    UPNOTE = '<p>This state is our reading of the example\'s own notes. The task force has not assigned states to examples yet, and the wording is being confirmed with the author.</p>'
    ups = [
        ('tea', 'tea-delegated-authority', ['review.yaml'], 'TEA delegated authority', 'Trust-Enabled Agents: does an agent\'s action stay within what it was delegated?',
         'Three findings closed as already addressed by the specification; one open.', 2, 'Author-assessed with AI help and approved as an example by a second task force member. Independent examination of the three "already addressed" findings is still pending.', None),
        ('trqp', 'standalone-trqp', ['review.yaml'], 'TRQP', 'Trust Registry Query Protocol: what does a valid answer from a trust registry actually establish?',
         'The first tutorial example: what a schema-valid authorisation response does and does not prove.', 2, 'Author-assessed with AI help. Findings open; independent review pending.', None),
        ('vrc', 'vrc-v03', ['baseline-review.yaml', 'reassessed-review.yaml'], 'VRC v0.3 examination and reassessment', 'Relationship credentials, draft v0.3: can the method be reused on a different specification, and reassessed after it changes?',
         'Reusing the method on a second specification, then reassessing after a change: before and after.', 2, 'Author-assessed. The example itself says independent reviewer judgement remains required.',
         [{'step': 'Frame the question', 'who': 'H+AI', 'done': 'yes'}, {'step': 'Pin and keep both versions of the source', 'who': 'M', 'done': 'yes'}, {'step': 'Check the kept source has not changed', 'who': 'M', 'done': 'yes'},
          {'step': 'Record findings on the first version', 'who': 'H+AI', 'done': 'yes'}, {'step': 'Reassess after the specification changed', 'who': 'H+AI', 'done': 'yes'}, {'step': 'Validate both records', 'who': 'M', 'done': 'yes'}, {'step': 'Independent examination', 'who': 'H*', 'done': 'no'}]),
        ('worked', 'worked-adoption', ['baseline-review.yaml', 'reassessed-review.yaml'], 'Worked adoption', 'A fictional training exercise: is a membership lifecycle document clear enough about revocation and renewal?',
         'A training exercise across two versions of a made-up document. Not an assessment of anything real.', 0, 'Training only. All participants and judgements are synthetic.',
         [{'step': 'State a bounded question', 'who': 'H', 'done': 'yes'}, {'step': 'Pin two versions of the training document', 'who': 'M', 'done': 'yes'}, {'step': 'Record findings, then reassess', 'who': 'H', 'done': 'yes'}, {'step': 'Validate the records', 'who': 'M', 'done': 'yes'}]),
    ]
    for key, folder, files, h1, q, shows, n, snote, steps in ups:
        base = os.path.join(REPO, 'review', 'examples', folder)
        recs_ = [yaml.safe_load(open(os.path.join(base, f_))) for f_ in files]
        m_ = manifest(key) if key in ('tea', 'trqp') else {}
        steps = steps or m_.get('steps', [])
        rv = ''.join(f'<li><b>{E(r_["assessment_id"])}</b>: {E(r_["target"].get("version_label",""))}, <span class="mono">{E(r_["target"]["repository"].replace("https://github.com/",""))}</span> at commit {commit_link(r_["target"]["repository"], r_["target"]["revision"])}, reviewed {E(str(r_.get("reviewed_at","")))} by {E(r_.get("reviewer",""))}</li>' for r_ in recs_)
        fhtml = ''
        for r_ in recs_:
            if len(recs_) > 1: fhtml += f'<h3 class="sec" style="font-size:1.2rem;margin-top:1.4rem">{E(r_["assessment_id"])}: {E(r_["target"].get("version_label",""))}</h3>'
            fhtml += plane_groups(r_['findings'], upplane, upf)
        body = f'''<div class="facts"><div><h4>The question</h4><p>{E(q)}</p></div><div><h4>What it shows</h4><p>{E(shows)}</p></div></div>
{sec('What was reviewed', '<ul>' + rv + '</ul><p class="flag">' + ('The records pass' if len(recs_) > 1 else 'The record passes') + ' the toolkit\'s checks. ' + CHECK_NOTE + '</p>')}
{sec('Who did what', whodid(steps) + ('<p class="count-line">Steps are our summary of the example\'s notes.</p>' if key in ('vrc', 'worked') else ''))}
{sec('Findings, by where the fix belongs', fhtml, 'findings')}
{sec('Read the full example', f'<p><a href="https://github.com/trustoverip/dtgwg-rahp-tf/tree/{COMMIT}/review/examples/{folder}" rel="noopener">The example in the toolkit repository</a>, with its source files, evidence and notes.</p>')}'''
        training = (n == 0)
        sbox = (f'<div class="statebox" style="border-left-color:var(--muted);background:var(--surface)"><h2>Training only</h2><p>{E(snote)}</p></div>' if training else
                f'<div class="statebox"><h2>State 2 of 4: checked by a person</h2><p>{E(snote)}</p>{UPNOTE}</div>')
        fn = f'ex-{key}.html'
        expage(fn, f'RAHP Example: {h1}', h1, q, n, sbox, body, training)
        cards.append((fn, h1, q, shows, n, 'Training only' if training else 'Checked by a person (our reading, to be confirmed)', training))

    # ---- examples.html ----
    order = [c for c in cards if c[0] == 'ex-linux.html'] + [c for c in cards if c[0] == 'ex-arthur-margaret.html'] + [c for c in cards if c[0] not in ('ex-linux.html', 'ex-arthur-margaret.html')]
    excards = ''.join(f'''<article class="excard"><p class="label" style="margin:0;color:{'var(--muted)' if tr else 'var(--draft)'}">{'Training only' if tr else f'State {n} of 4: {E(STATES[n-1][0])}'}</p>{'' if tr else minisl(n)}<h3>{E(t)}</h3><p class="q">{E(q)}</p><p>{E(sh)}</p><p style="font-size:.88rem;color:var(--muted)">{E(st_)}</p><a class="go" href="{fn}">Open the example<span class="vh">: {E(t)}</span></a></article>''' for fn, t, q, sh, n, st_, tr in order)
    stx = ''.join(f'<li><b>{i}. {E(t)}</b>{E(d)}</li>' for i, (t, d) in enumerate(STATES, 1))
    body = EXCSS + f'''<div class="banner" style="border-left-color:var(--draft)"><h2>These are steps in a process, not verdicts</h2><p>Each example shows how far its review has got, and who did what: people, AI or machines. None has been decided by the task force yet. {CHECK_NOTE}</p></div>
<h2 class="sec" style="margin-top:0">The four review states</h2><ol class="stateline" aria-label="The four review states">{stx}</ol>
<h2 class="sec">The examples</h2><div class="excards">{excards}</div>
<p class="count-line" style="margin-top:1rem">The four upstream examples were prepared by another task force member. Their state is our reading of their own notes and is being confirmed. One more review, of an implementation, is published without naming the system reviewed.</p>'''
    page('examples.html', 'RAHP Examples', 'examples', 'Examples', 'Examples',
         'Real reviews, shown as they stand. Use them to see each step of the journey in practice, including the steps that have not been done yet.', body)
    print('examples built:', EX_PAGES)

# ================= step-by-step guides =================
REPOURL = 'https://github.com/trustoverip/dtgwg-rahp-tf'
RAW = 'https://raw.githubusercontent.com/trustoverip/dtgwg-rahp-tf/main'
GCSS = '''<style>
.gintro{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,250px),1fr));gap:.8rem;margin-bottom:1.6rem}
.gintro>div{background:var(--bg);border:1px solid var(--line);border-radius:var(--radius);padding:.8rem 1rem}
.gintro h3{font-family:var(--font-display);font-weight:800;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--mid);margin:0 0 .3rem}
.gintro p,.gintro ul{margin:0;font-size:.95rem}
.gsteps{list-style:none;margin:0;padding:0;counter-reset:g;display:grid;gap:1rem}
.gstep{counter-increment:g;display:grid;grid-template-columns:3rem minmax(0,1fr);gap:1rem;background:var(--bg);border:1px solid var(--line);border-radius:var(--radius);padding:1.1rem 1.2rem;scroll-margin-top:90px}
.gstep.rule{border-left:6px solid var(--fg)}
.gstep::before{content:counter(g);font-family:var(--font-display);font-weight:800;font-size:1.1rem;color:var(--on-brand);background:var(--brand);border-radius:50%;width:2.6rem;height:2.6rem;display:grid;place-items:center}
.gstep h2{font-size:1.2rem;font-weight:800;margin:0 0 .3rem}
.gstep .who{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;font-size:.86rem;color:var(--muted);margin:0 0 .6rem}
.gstep p{margin:.4rem 0}
.gstep p,.gstep li,.gstep pre{overflow-wrap:anywhere}
.gstep>div{min-width:0}
.gstep ol,.gstep ul{margin:.3rem 0;padding-left:1.3rem;display:grid;gap:.25rem}
.gstep .done{background:var(--ok-bg);border-left:4px solid var(--ok);padding:.45rem .7rem;font-size:.92rem;margin-top:.6rem}
.gstep .done b{font-family:var(--font-display);font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ok)}
.codebox{position:relative;margin:.6rem 0}
.codebox pre{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:.9rem 1rem;overflow-x:auto;font-family:var(--font-mono);font-size:.84rem;line-height:1.5;white-space:pre-wrap;margin:0}
.codebox .cap{display:flex;justify-content:space-between;align-items:center;gap:.6rem;font-family:var(--font-display);font-weight:800;font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:.3rem}
.copy{font:inherit;font-family:var(--font-display);font-weight:800;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;border:1.5px solid var(--brand);color:var(--brand);background:var(--bg);border-radius:var(--radius);padding:.3rem .7rem;cursor:pointer}
.urls{list-style:none;margin:.4rem 0;padding:0;display:grid;gap:.3rem;font-size:.92rem}
.urls li{overflow-wrap:anywhere}
.switch{display:flex;flex-wrap:wrap;gap:.6rem;margin:0 0 1.4rem}
</style>'''
COPYJS = r'''<script>
document.querySelectorAll('.copy').forEach(function(b){b.addEventListener('click',function(){
  var pre=document.getElementById(b.dataset.for), t=pre.textContent, lab=b.textContent;
  function sel(){var r=document.createRange();r.selectNodeContents(pre);var s=window.getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Selected: press Ctrl+C';setTimeout(function(){b.textContent=lab;},2500);}
  try{navigator.clipboard.writeText(t).then(function(){b.textContent='Copied';setTimeout(function(){b.textContent=lab;},2000);},sel);}catch(e){sel();}
});});
</script>'''
_cb = [0]
def code(cap, text, label='Copy'):
    _cb[0] += 1; i = f'cb{_cb[0]}'
    return f'<div class="codebox"><div class="cap"><span>{E(cap)}</span><button type="button" class="copy" data-for="{i}" aria-label="{label}: {E(cap)}">{label}</button></div><pre id="{i}">{E(text)}</pre></div>'
WHO_TAG = {'h': ('h', 'You'), 'r': ('r', 'You, by rule: AI must not do this'), 'ai': ('ai', 'AI drafts; you review'), 'm': ('m', 'A machine check')}
def gstep(id_, title, whos, body, done, rule=False):
    w = ''.join(f'<span style="display:inline-flex;align-items:center;gap:.35rem"><span class="mk {WHO_TAG[k][0]}" aria-hidden="true"></span>{WHO_TAG[k][1]}</span>' for k in whos)
    stg = STEP_STAGE.get(id_)
    if stg: w += f'<span>· Lifecycle: <a href="lifecycle.html#{stg}">stage {stg[-1]}, {E(next(x["name"] for x in life["records"] if x["id"]==stg))}</a></span>'
    return f'<li class="gstep{" rule" if rule else ""}" id="{id_}"><div><h2>{E(title)}</h2><p class="who">{w}</p>{body}<p class="done"><b>Done when</b> {done}</p></div></li>'
def link(url, text): return f'<a href="{E(url)}" rel="noopener">{E(text)}</a>'

QUESTIONS = '''1. Who is this person, and what are they trying to do in this situation?
2. What does the specification let them do, and what does it stop them doing?
3. Who could they be mistaken for, and who could pretend to be them?
4. What do they have to reveal about themselves, and to whom?
5. Could anything exclude them: geography, language, cost, disability, who they know?
6. What happens if something goes wrong: revocation, a dispute, a mistake, a death?
7. Who acts for them, or could act against them, and is that visible and limited?
8. Are AI agents or automated systems involved, and is someone accountable for them?
9. What does the specification leave to governance, implementations or other specifications? Which ones?
10. Is the normative language (MUST, SHOULD, MAY) clear enough to translate?'''

TABLE_TEMPLATE = '''Review of: [specification name], commit [40-character commit ID]
Reviewer: [your name]        Date: [date]
People and situations: [names from the People and Situations pages]

| # | What I found (one sentence) | Where (section or line) | Who is affected | Risk (name or new) | Where the fix belongs | Who must act | Status |
|---|-----------------------------|-------------------------|-----------------|--------------------|-----------------------|--------------|--------|
| 1 |                             |                         |                 |                    |                       |              | Open   |'''

YAML_TEMPLATE = '''schema: rahp-spec-review/v1
reviewer: Your Name
assessment_id: SR-900
target:
  repository: https://github.com/OWNER/REPOSITORY
  revision: "PASTE-THE-FULL-40-CHARACTER-COMMIT-ID"
  version_label: Working Draft 0.1.0
rahp_version: dtgwg-rahp-tf main f92cc6c
reviewed_at: "2026-11-11"
findings:
  - id: F-001
    summary: One sentence saying what is missing or wrong, for whom.
    risks: [RK-ID01]
    control_plane: specification
    status: open'''

SETUP = '''git clone https://github.com/trustoverip/dtgwg-rahp-tf.git
cd dtgwg-rahp-tf
python3 -m venv .venv
source .venv/bin/activate          # on Windows: .venv\\Scripts\\activate
pip install -r requirements.txt'''

CHECK = '''python3 review/validate_spec_review.py path/to/your-review.yaml
python3 tools/validate_all.py --review path/to/your-review.yaml'''

PROMPT_CONTEXT = f'''I am reviewing a specification with the RAHP (Risk Assessment and Harms Prevention) toolkit.
I have attached, or pasted below:
1. The specification, at commit [COMMIT ID] of [REPOSITORY URL].
2. The RAHP risks: {RAW}/data/risks.yaml
3. The RAHP people (personas): {RAW}/data/personas.yaml
4. The RAHP situations (scenarios): {RAW}/data/scenarios.yaml
5. Where a fix can belong (control planes): {RAW}/method/vocabularies.yaml

If you cannot open a link, say so and I will paste the file. Do not guess its contents.
Confirm what you have received, in a short list, before we start.'''

PROMPT_FRAME = '''I want to review the specification through the eyes of these people, in these situations:
[names of people and situations, from the RAHP People and Situations pages]

Draft up to ten review questions for this review. Use these as a starting point and adapt them to the people and the specification:
''' + QUESTIONS + '''

Keep each question short and plain. I will choose, change or drop each one.'''

PROMPT_READ = '''Read the specification with the eyes of [names], using the review questions we agreed.

For each question:
1. What the specification says: quote it briefly, with file and line (path:line).
2. Your assessment, labelled as one of: ADDRESSED / PARTLY / MISSING / CONTRADICTS / HANDED ELSEWHERE (say where).

Then give a table of candidate findings with these columns:
ID (F-001 and so on) | whose path | one-sentence finding | evidence (path:line, or "absent: searched for X, Y") | label | RAHP risk IDs | where the fix belongs (specification, companion-specification, governance, implementation-guidance, runtime-control, operational-policy; and say if it is really user experience or configuration) | who must act | your confidence (high, medium, low)

Rules:
- Quote the specification. Never invent line numbers. Check every line you cite.
- For anything you say is absent, list the search terms you used.
- Mark your own judgement as assessment, separate from what the text says.
- If a finding needs a risk the catalogue lacks, say so and propose a short name. Do not invent a risk ID.
- You are drafting. I will review every finding.'''

PROMPT_RECORD = '''Here are the findings I have reviewed and confirmed, changed or dropped:
[paste your reviewed table]

Write a RAHP review record in YAML (schema rahp-spec-review/v1), following this template:
[paste the template from the guide]

Rules:
- Include only the findings I confirmed or changed.
- target.revision must be the full 40-character commit ID: [COMMIT ID].
- reviewer: [your name]. If I have not reviewed every finding, write instead:
  "AI draft (assistant name), not yet reviewed by [your name]".
- Use only risk IDs that exist in the RAHP risks file. For a proposed risk, use EX-RK-... and list it separately so I can add it to a local risks file.
- control_plane and status must use the allowed values. Do not resolve or risk-accept anything I have not decided.'''

PROMPT_CHALLENGE = '''You are examining a review you did not write. Try to disprove each finding.
For each finding below:
1. Find the strongest reason it could be wrong: a misread line, text elsewhere in the specification that answers it, or a judgement that does not follow.
2. Say whether the evidence supports the finding: yes / partly / no, and why.
3. Say what a person must check before relying on it.

Findings:
[paste the review record]
Specification at commit [COMMIT ID]: [attach or paste]

This is an aid to a person's independent examination. It does not replace it.'''

# ---- without AI ----
steps = []
steps.append(gstep('na1', 'Choose your way in', ['h'],
    '<p>Decide where to start:</p><ul><li><b>From a person</b>, if you care most about who could be harmed. Start at <a href="people.html">People</a>.</li><li><b>From a specification or system</b>, if you are an editor or implementer. You will still pick people in step 2.</li></ul>',
    'you know whether you are starting from a person or from a specification.'))
steps.append(gstep('na2', 'Pick the people and situations', ['h'],
    '<ol><li>Open <a href="people.html">People</a> and choose one to three people. Open each card and read "What worries them" and "What keeps them out".</li><li>Open <a href="situations.html">Situations</a> and choose the situations they appear in.</li><li>Write down each name. Open "Reference in the files" to note its code (for example EC2a, SC-28): you need the codes in step 7.</li></ol>',
    'you have a short list of people and situations, with their codes.'))
steps.append(gstep('na3', 'Pick what you will review, and fix its exact version', ['h'],
    '<p>A specification changes. So that others can see exactly what you read, record the exact version, called a commit ID.</p><ol><li>Open the specification\'s repository on GitHub.</li><li>Above the list of files, select the clock icon or "commits".</li><li>On the latest commit, select the copy button. That copies the full 40-character commit ID.</li><li>Paste it at the top of your notes, with the date.</li><li>Read the specification at that version: open <span class="mono">https://github.com/OWNER/REPOSITORY/tree/COMMIT-ID</span>.</li></ol>',
    'you have the repository address and the 40-character commit ID written down.'))
steps.append(gstep('na4', "Read it with the person's eyes", ['h'],
    '<p>Read the specification section by section, asking these questions for each person. Note what the text says, and the section or line number.</p>' + code('Review questions', QUESTIONS) +
    '<p>This is the longest step. One specification can take a day or more. For several specifications, give one to each person, then meet to find the themes that cut across them.</p>',
    'every question has a note for each person, with where in the specification you saw it, or "not found" and what you searched for.'))
steps.append(gstep('na5', 'Match each finding to a risk', ['h'],
    '<ol><li>Open <a href="risks.html">Risks</a> and search for words from your finding, such as "revocation" or "agent".</li><li>Open the closest risk and check its harm matches yours. Note its code (RK-...).</li><li>If none fits, describe the risk in a few words. It becomes a proposed local risk (EX-RK-...), for the task force to decide on later.</li></ol>',
    'every finding has a risk, or a proposed new one.'))
steps.append(gstep('na6', 'Say where the fix belongs, and who must act', ['h'],
    '<p>For each finding, choose one of the <a href="index.html#planes">five places a fix can belong</a>: technical standards, implementation, configuration, governance or user experience. Then name who must act, such as the specification editors, the implementers or the community\'s governing body.</p>',
    'every finding says where its fix belongs and who must act.'))
steps.append(gstep('na7', 'Write it up', ['h'],
    '<p>If you don\'t use code, use this table, in a document or spreadsheet:</p>' + code('Review table template', TABLE_TEMPLATE) +
    '<p>If you can edit files, write a review record. Copy this template into a file ending <span class="mono">.yaml</span>. The ' + link(REPOURL + '/blob/main/docs/pressure-testing-a-spec.md', 'review record guide') + ' explains every field.</p>' + code('Review record template (YAML)', YAML_TEMPLATE),
    'every finding is written up, with the commit ID at the top.'))
steps.append(gstep('na8', 'Run the check (optional, technical)', ['m'],
    '<p>The check confirms that a review record is complete and that every risk code exists. It does not judge your findings. You need Git and Python 3.</p>' + code('One-time setup', SETUP) +
    '<p style="font-size:.92rem;color:var(--muted)">On Ubuntu, if <span class="mono">python3 -m venv</span> fails, first run <span class="mono">sudo apt install python3-venv</span>. System-wide <span class="mono">pip install</span> is blocked on recent versions, so always use the virtual environment.</p>' + code('Check your record', CHECK) +
    '<p class="flag">Passing the check means the record is well formed, not that its findings are right.</p>',
    'the check reports no errors, or you have skipped it and said so.'))
steps.append(gstep('na9', 'Ask someone else to examine it', ['r'],
    '<p>Ask a person who did not prepare the review to try to disprove each finding: re-read the cited text, look for text elsewhere that answers it, and question each judgement. Record what they agree with and what they dispute.</p>',
    'a second person has examined every finding, and any disagreement is written down.', rule=True))
steps.append(gstep('na10', 'Share it', ['r'],
    '<p>Decide what to share and with whom. For now, open an issue on the ' + link(REPOURL + '/issues', 'toolkit repository') + ' and attach or paste your review, or send it to the task force. The <a href="index.html#share">routes for sharing a finding</a> are still being chosen, including a protected route for people who cannot be named.</p>',
    'the review is shared, and you know where to look for the outcome.', rule=True))
body = GCSS + f'''<div class="switch"><a class="btn ghost" href="guide-with-ai.html">Switch to the guide with AI</a><a class="btn ghost" href="index.html#journey">See the journey</a></div>
<p class="flag"><b>Draft guide.</b> Based on the toolkit's review guide and the task force's first-use test. To be tried with first-time users.</p>
<div class="gintro"><div><h3>You will produce</h3><p>A review: what you found, for whom, where the fix belongs, at an exact version of the specification.</p></div>
<div><h3>You need</h3><ul><li>A browser.</li><li>A document or spreadsheet.</li><li>Git and Python 3, only for the optional check.</li></ul></div>
<div><h3>Time</h3><p>A day or more for one specification. Split several specifications across people.</p></div>
<div><h3>Reference</h3><p>{link(REPOURL + '/blob/main/docs/pressure-testing-a-spec.md', 'Review record guide')} · {link(REPOURL + '/blob/main/review/examples/tea-delegated-authority/TUTORIAL.md', 'Technical tutorial')} · <a href="examples.html">Examples</a></p></div></div>
<ol class="gsteps">{''.join(steps)}</ol>'''
page('guide-without-ai.html', 'RAHP Guide Without AI', 'guides', 'Guides', 'Review without AI',
     'A step-by-step guide to reviewing a specification by hand, from choosing the people to sharing what you found. No code is needed except for one optional check.', body, COPYJS)

# ---- with AI ----
steps = []
steps.append(gstep('ai1', 'Choose your way in, and the people', ['h'],
    '<p>Do steps 1 and 2 of the <a href="guide-without-ai.html#na1">guide without AI</a>: decide whether to start from a person or a specification, then choose people from <a href="people.html">People</a> and situations from <a href="situations.html">Situations</a>, noting their codes.</p><p>AI can suggest people, but you choose. Who you test for is a value judgement.</p>',
    'you have chosen the people and situations yourself.'))
steps.append(gstep('ai2', 'Fix the exact version', ['h', 'm'],
    '<p>Copy the full 40-character commit ID of the specification, as in <a href="guide-without-ai.html#na3">step 3 without AI</a>. If your AI assistant can run commands, it can do this with <span class="mono">git rev-parse HEAD</span>. Check the ID it gives you against GitHub.</p>',
    'you have the commit ID, checked on GitHub.'))
steps.append(gstep('ai3', 'Give the AI the context', ['h'],
    '<p>Start a new conversation with a general-purpose AI assistant that can read long documents. Attach or paste the specification at your commit, and these toolkit files:</p><ul class="urls">'
    + ''.join(f'<li>{E(n)}: <a href="{u}" rel="noopener">{E(u)}</a></li>' for n, u in [('Risks', RAW + '/data/risks.yaml'), ('People', RAW + '/data/personas.yaml'), ('Situations', RAW + '/data/scenarios.yaml'), ('Safeguards', RAW + '/data/controls.yaml'), ('Where a fix can belong', RAW + '/method/vocabularies.yaml')]) +
    '</ul><p>Some assistants cannot open links. Download the files and attach them instead. Then send this prompt:</p>' + code('Prompt 1: set up', PROMPT_CONTEXT),
    'the assistant has listed what it received, and nothing is missing.'))
steps.append(gstep('ai4', 'Agree the review questions', ['ai', 'h'],
    code('Prompt 2: frame the questions', PROMPT_FRAME) + '<p>Read its questions. Keep, change or drop each one, and tell it the final list.</p>',
    'you have agreed the questions yourself.'))
steps.append(gstep('ai5', "Have it read the specification and draft findings", ['ai'],
    code('Prompt 3: read and draft findings', PROMPT_READ) + '<p>For several specifications, run this once per specification, in separate conversations, then ask for the themes that cut across them. See the <a href="ex-linux.html">Linux case</a> for what this produces.</p>',
    'you have a draft table of findings, each with evidence.'))
steps.append(gstep('ai6', 'Check the citations yourself', ['h'],
    '<ol><li>Pick at least ten cited lines, including every finding you think matters most.</li><li>Open the specification at your commit and check each line says what the AI quoted.</li><li>For "absent" claims, search the specification yourself for the terms it listed, and one or two of your own.</li></ol><p>This checks the quotations. It does not check the judgements: that is the next step.</p>',
    'every citation you checked matches, or the finding is corrected.'))
steps.append(gstep('ai7', "Review every finding as the person's advocate", ['r'],
    '<p>Go through every finding with the person in mind. Confirm it, change it or drop it, and add anything the AI missed. Decide where each fix belongs and how serious it is. The AI must not do this.</p><p>Until you have done this, the review is an <b>AI draft</b> and must say so.</p>',
    'every finding is confirmed, changed or dropped by you.', rule=True))
steps.append(gstep('ai8', 'Have it write the review record', ['ai', 'h'],
    code('Prompt 4: write the review record', PROMPT_RECORD) + '<p>Use the <a href="guide-without-ai.html#na7">template in step 7 without AI</a>. Check the record names you as reviewer only if you reviewed every finding.</p>',
    'you have a review record, correctly labelled.'))
steps.append(gstep('ai9', 'Run the check', ['m'],
    '<p>Run the toolkit\'s check, as in <a href="guide-without-ai.html#na8">step 8 without AI</a>. An assistant that can run code can run it for you; read the output yourself.</p>' + code('Check your record', CHECK) + '<p class="flag">Passing the check means the record is well formed, not that its findings are right.</p>',
    'the check reports no errors.'))
steps.append(gstep('ai10', 'Have it examined independently', ['r'],
    '<p>A person who did not prepare the review tries to disprove each finding. A different AI model can help them by playing the challenger, but the person decides.</p>' + code('Prompt 5: challenger (an aid for the examiner)', PROMPT_CHALLENGE),
    'a second person has examined every finding.', rule=True))
steps.append(gstep('ai11', 'Label it and share it', ['r'],
    '<p>Say how AI helped and who is accountable. Then share it as in <a href="guide-without-ai.html#na10">step 10 without AI</a>.</p>',
    'the review is shared, labelled with how AI helped and who reviewed it.', rule=True))
body = GCSS + f'''<div class="switch"><a class="btn ghost" href="guide-without-ai.html">Switch to the guide without AI</a><a class="btn ghost" href="index.html#journey">See the journey</a></div>
<p class="flag"><b>Draft guide.</b> The prompts are drafts based on the task force's two trial reviews and the toolkit's {link(REPOURL + '/blob/main/RAHP_AI_Assisted_Process.md', 'AI-assisted process')}. To be tried with first-time users.</p>
<div class="gintro"><div><h3>Ground rules</h3><ul><li>AI assists. People decide.</li><li>Don't use AI to score risks, verify must-haves or make governance decisions.</li><li>Check every citation, then every judgement.</li></ul></div>
<div><h3>You need</h3><ul><li>An AI assistant that can read long documents, such as Claude.</li><li>The specification's files.</li><li>Git and Python 3, only for the check.</li></ul></div>
<div><h3>Time</h3><p>The reading takes minutes. Your review of the findings still takes hours: plan for it.</p></div>
<div><h3>More prompts</h3><p>For drafting people, user stories and coverage checks, see the {link(REPOURL + '/blob/main/RAHP_AI_Assisted_Process.md', 'AI-assisted process')}.</p></div></div>
<ol class="gsteps">{''.join(steps)}</ol>'''
page('guide-with-ai.html', 'RAHP Guide With AI', 'guides', 'Guides', 'Review with AI assistance',
     'A step-by-step guide to reviewing a specification with an AI assistant: what to give it, the prompts to use, and the steps that stay with people.', body, COPYJS)
print('guides built')

# ================= front door: shared header and click-throughs =================
h = open(HOME).read()
h = re.sub(r'<header class="site">.*?</header>', header('home', home_page=True), h, count=1, flags=re.S)
swaps = [
 ('<a class="go" href="#kit">Go to people and situations</a>', '<a class="go" href="people.html">Go to the people</a>'),
 ('<a class="go" href="#planes">Go to where fixes belong</a>', '<a class="go" href="safeguards.html#musthaves">Go to must-haves and tests</a>'),
 ('<a class="go" href="#kit">Go to what\'s in the kit</a>', '<a class="go" href="lifecycle.html">Go to the five stages</a>'),
 ('<a class="go" href="#examples">Go to worked examples</a>', '<a class="go" href="examples.html">Go to the examples</a>'),
]
for a, b in swaps:
    if a in h: h = h.replace(a, b, 1)
    else: print('WARN missing', a[:60])
countlinks = {
 '<div class="count"><b>5</b><span>lifecycle stages, from scoping to maintenance</span></div>': 'lifecycle.html',
 '<div class="count"><b>5</b><span>places a fix can belong</span></div>': '#planes',
 '<div class="count"><b>16</b><span>people, including agents, bad actors and edge cases</span></div>': 'people.html',
 '<div class="count"><b>33</b><span>situations that test the system</span></div>': 'situations.html',
 '<div class="count"><b>43</b><span>risks: what could go wrong, and for whom</span></div>': 'risks.html',
 '<div class="count"><b>66</b><span>safeguards, plus 21 must-haves</span></div>': 'safeguards.html',
 '<div class="count"><b>37</b><span>measures of whether a safeguard works</span></div>': 'safeguards.html#measures',
 '<div class="count"><b>3</b><span>risk decisions, all waiting for a named decision-maker</span></div>': 'decisions.html',
}
for a, href in countlinks.items():
    if a in h: h = h.replace(a, a.replace('<div class="count">', f'<a class="count" href="{href}">').replace('</div>', '</a>'), 1)
    else: print('WARN count', a[:50])
if 'a.count{' not in h:
    h = h.replace('.count{background:var(--surface);', 'a.count{text-decoration:none;color:var(--fg);border:1.5px solid transparent}\na.count:hover{border-color:var(--brand)}\n.count{background:var(--surface);', 1)
# kit section: add explicit links under the two chains
h = h.replace('<details class="more" style="margin-top:.8rem">\n            <summary>Terms and codes used in the files</summary>',
              '<p style="margin:.9rem 0 0"><a href="affected.html">See who is affected by what</a> · <a href="glossary.html">Words and codes</a></p>\n          <details class="more" style="margin-top:.8rem">\n            <summary>Terms and codes used in the files</summary>', 1)

# examples on the front door
if EXDIR:
    ex_cards = [
     ('ex-linux.html', 'draft', 'State 1: AI draft, not yet reviewed by Nicky Hickman', 'Linux case study: Dewi and Kestrel', 'One scenario against three draft specifications at once: 57 findings and 10 themes, all AI-drafted.'),
     ('ex-arthur-margaret.html', 'draft', 'State 2: checked by a person', 'Arthur and Margaret', 'A trial review of an open-source trust-community implementation stack, through the eyes of a person living with dementia and the attorney who acts for him.'),
     ('ex-tea.html', 'draft', 'State 2: checked by a person (to be confirmed)', 'TEA delegated authority', "Does an agent's action stay within what it was delegated?"),
     ('ex-trqp.html', 'draft', 'State 2: checked by a person (to be confirmed)', 'Trust registry query protocol', 'What a valid answer from a trust registry does and does not establish.'),
     ('ex-vrc.html', 'draft', 'State 2: checked by a person (to be confirmed)', 'Verifiable relationship credentials, v0.3', 'Reusing the method on another specification, then reassessing after it changed.'),
     ('ex-worked.html', 'todo', 'Training only', 'A fictional membership lifecycle', 'A training exercise with no real people or systems.'),
    ]
    inner = ''.join(f'\n        <article class="example"><span class="pill {c}">{E(st)}</span><h3><a href="{fn}">{E(t)}</a></h3><p>{E(d)}</p></article>' for fn, c, st, t, d in ex_cards)
    h = re.sub(r'(<div class="examples">).*?(\n      </div>\n    </div>\n  </section>)', lambda m: m.group(1) + inner + m.group(2), h, count=1, flags=re.S)
    h = h.replace('<p class="lead">Each example shows the exact version reviewed, what was found and what is still open.</p>',
                  '<p class="lead">Each example shows the exact version reviewed, what was found, who did what, and what is still open. <a href="examples.html">See all examples</a>.</p>', 1)
    h = h.replace('<div class="here"><span>Three specifications, one scenario</span></div>', '<div class="here"><span><a href="ex-linux.html">Linux case: three specifications</a></span></div>', 1)
    h = h.replace('<div class="here"><span>Arthur and Margaret</span></div>', '<div class="here"><span><a href="ex-arthur-margaret.html">Arthur and Margaret</a></span><span><a href="ex-tea.html">TEA</a></span><span><a href="ex-trqp.html">TRQP</a></span><span><a href="ex-vrc.html">VRC v0.3</a></span></div>', 1)
    h = h.replace('<b>Arthur and Margaret:</b> ', '<b><a href="ex-arthur-margaret.html">Arthur and Margaret</a>:</b> ', 1)
    h = h.replace('<b>Three specifications:</b> ', '<b><a href="ex-linux.html">Three specifications</a>:</b> ', 1)
    h = h.replace('<p class="lead">Every review record moves through four states. Neither of our two trial reviews is finished. They are shown here as they stand.</p>',
                  '<p class="lead">Every review record moves through four states. No review is finished. They are shown here as they stand; choose one to see it. The state of the upstream examples is our reading, to be confirmed.</p>', 1)
    h = h.replace('<p class="joins" style="color:var(--muted)">Steps 0 to 15 are using the kit.', '<p class="joins" style="color:var(--muted)"><a href="examples.html">See real reviews at each step</a>. Steps 0 to 15 are using the kit.', 1)

# guides on the front door
guides_band = """  <section class="band" id="guides" aria-labelledby="guides-title">
    <div class="wrap">
      <div class="band-head">
        <p class="label">Step-by-step guides</p>
        <h2 class="section-title" id="guides-title">Do a review yourself</h2>
        <p class="lead">Two guides follow the same journey. Each step says who does it, what to do and how you know it's done.</p>
      </div>
      <div class="split">
        <a class="panel" href="guide-with-ai.html" style="text-decoration:none;color:var(--fg)"><h3>With AI assistance <span class="pill draft">Draft</span></h3><p style="margin:.6rem 0 0">What to give the AI, the prompts to copy, and the steps that stay with people. 11 steps.</p><p class="label" style="color:var(--brand);margin:.9rem 0 0">Open the guide with AI</p></a>
        <a class="panel" href="guide-without-ai.html" style="text-decoration:none;color:var(--fg)"><h3>Without AI <span class="pill draft">Draft</span></h3><p style="margin:.6rem 0 0">Reading by hand, with templates for your notes and an optional check. 10 steps.</p><p class="label" style="color:var(--brand);margin:.9rem 0 0">Open the guide without AI</p></a>
      </div>
    </div>
  </section>

"""
h = h.replace('  <section class="band" id="states"', guides_band + '  <section class="band" id="states"', 1)
h = h.replace('<a class="go" href="#journey">Go to the journey</a>', '<a class="go" href="guide-without-ai.html">Go to the step-by-step guide</a>', 1)
h = h.replace('<h3>Rules for using AI</h3>', '<h3>Rules for using AI</h3><p style="margin:.4rem 0 0"><a href="guide-with-ai.html">Step-by-step guide with AI, with prompts</a></p>', 1)
h = h.replace('<p class="note warn" style="margin-bottom:0"><b>Without AI takes longer.</b> Reading one specification can take a day or more. Split several specifications across people, then meet to find the themes.</p>',
              '<p class="note warn" style="margin-bottom:0"><b>Without AI takes longer.</b> Reading one specification can take a day or more. Split several specifications across people, then meet to find the themes. <a href="guide-without-ai.html">Step-by-step guide without AI</a>.</p>', 1)

# lifecycle on the front door
h = h.replace('<p class="joins"><b>Joins the journey at</b>Steps 1 to 12, then hand over for examination</p>',
  '<p class="joins"><b>Joins the journey at</b>Steps 1 to 12, then hand over for examination</p>\n          <p class="joins"><b>Lifecycle</b><a href="lifecycle.html">Stages 1 to 3</a>: context, drafting, review and harmonisation</p>', 1)
lc_strip = '<div class="note" style="margin-top:1.2rem"><b>The journey across the five lifecycle stages</b> (proposed): ' + ' · '.join(
  f'<a href="lifecycle.html#{k}">{k[-1]}. {E(next(x["name"] for x in life["records"] if x["id"]==k))}</a>: {E(v[0].lower())}' for k, v in STAGE_MAP.items()) + '.</div>'
h = h.replace('      <div class="split" style="margin-top:2rem">\n        <div class="panel">\n          <h3>Rules for using AI</h3>', '      ' + lc_strip + '\n      <div class="split" style="margin-top:2rem">\n        <div class="panel">\n          <h3>Rules for using AI</h3>', 1)

open(HOME, 'w').write(h)
print('front door updated')

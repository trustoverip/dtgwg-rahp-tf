#!/usr/bin/env python3
"""
validate.py — integrity check for a RAHP artefact set.

Exits 0 on a clean repository. Exits 1 if any ERROR is found. Warnings do not
fail the build but are always printed and counted.

    python3 tools/validate.py                 # human-readable report
    python3 tools/validate.py --summary       # one line, suitable for a commit message
    python3 tools/validate.py --json          # machine-readable
    python3 tools/validate.py --strict        # treat warnings as errors

What it checks:
  1  Schema      — every record validates against method/schema/rahp.schema.json
  2  Vocabulary  — every controlled-vocabulary field holds a permitted value
  3  Identifiers — IDs match their namespace pattern; no duplicates within a namespace
  4  References  — every cross-reference resolves to a defined record
  5  Symmetry    — bidirectional links agree (a risk citing GR-07 and GR-07 citing that risk)
  6  Invariants  — the method's own rules from data/instance.yaml
  7  Orphans     — identifiers defined but never referenced
  8  Counts      — README figures match actual record counts

Configuration is read from data/instance.yaml. No working-group-specific logic
is hard-coded here: point it at a different data/ directory and it works.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import defaultdict

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("validate.py requires PyYAML: pip install -r requirements.txt")

try:
    from jsonschema import Draft202012Validator
    HAVE_JSONSCHEMA = True
except ImportError:  # pragma: no cover
    HAVE_JSONSCHEMA = False

ROOT = pathlib.Path(__file__).resolve().parent.parent


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict = {}
        self.checks: list[tuple[str, bool, str]] = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def check(self, name, ok, detail=""):
        self.checks.append((name, ok, detail))


def load_yaml(path: pathlib.Path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_records(data_dir: pathlib.Path, instance: dict):
    """Return {record_type: {id: record}} and {record_type: source filename}."""
    by_type, sources = {}, {}
    for ns, spec in instance["namespaces"].items():
        path = data_dir / spec["file"]
        rtype = spec["record_type"]
        if not path.exists():
            by_type.setdefault(rtype, {})
            continue
        doc = load_yaml(path) or {}
        records = doc.get("records") or []
        if isinstance(records, dict):  # tolerate mapping form
            records = [dict(v, id=k) for k, v in records.items()]
        by_type.setdefault(rtype, {})
        sources[rtype] = spec["file"]
        for rec in records:
            rid = rec.get("id")
            if rid in by_type[rtype]:
                continue  # duplicate handled in check_identifiers
            by_type[rtype][rid] = rec
    return by_type, sources


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def check_schema(by_type, rep: Report):
    if not HAVE_JSONSCHEMA:
        rep.warn("jsonschema not installed — schema validation skipped "
                 "(pip install -r requirements.txt)")
        rep.check("schema", True, "skipped")
        return
    schema_path = ROOT / "method" / "schema" / "rahp.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    defs = schema["$defs"]
    bad = 0
    for rtype, records in by_type.items():
        if rtype not in defs:
            continue
        sub = dict(schema)
        sub = {"$schema": schema["$schema"], "$defs": defs, **defs[rtype]}
        validator = Draft202012Validator(sub)
        for rid, rec in records.items():
            for err in validator.iter_errors(rec):
                loc = ".".join(str(p) for p in err.absolute_path) or "(record)"
                rep.error(f"schema  {rtype}/{rid}: {loc}: {err.message}")
                bad += 1
    rep.check("schema", bad == 0, f"{bad} violation(s)")


def check_vocabularies(by_type, vocab, rep: Report):
    def allowed(key):
        entry = vocab.get(key, {})
        vals = entry.get("values", [])
        out = []
        for v in vals:
            out.append(v["value"] if isinstance(v, dict) else v)
        return out

    field_vocab = {
        ("risk", "severity"): "severity",
        ("risk", "likelihood"): "likelihood",
        ("risk", "standards_priority"): "standards_priority",
        ("control", "type"): "control_type",
        ("control", "standards_status"): "standards_status",
        ("control", "normative_language"): "normative_language",
        ("guardrail", "standards_status"): "standards_status",
        ("guardrail", "normative_language"): "normative_language",
        ("persona", "type"): "persona_type",
        ("risk_acceptance", "decision"): "risk_acceptance_decision",
        ("governance_precedent", "status"): "governance_precedent_status",
    }
    bad = 0
    for (rtype, field), vkey in field_vocab.items():
        permitted = allowed(vkey)
        if not permitted:
            continue
        for rid, rec in by_type.get(rtype, {}).items():
            if field not in rec:
                continue
            val = rec[field]
            if val is None and None in permitted:
                continue
            if val is None and "null" in [str(p) for p in permitted]:
                continue
            if val is None:
                continue
            if val not in permitted:
                rep.error(f"vocab   {rtype}/{rid}: {field}={val!r} not in {vkey} "
                          f"({', '.join(str(p) for p in permitted if p)})")
                bad += 1
    rep.check("vocabulary", bad == 0, f"{bad} violation(s)")


def check_identifiers(data_dir, instance, rep: Report):
    bad = 0
    counts = {}
    for ns, spec in instance["namespaces"].items():
        path = data_dir / spec["file"]
        if not path.exists():
            rep.error(f"ids     missing data file: {spec['file']}")
            bad += 1
            continue
        doc = load_yaml(path) or {}
        records = doc.get("records") or []
        if isinstance(records, dict):
            records = [dict(v, id=k) for k, v in records.items()]
        pattern = re.compile(spec["pattern"])
        seen = set()
        for rec in records:
            rid = rec.get("id")
            if not rid:
                rep.error(f"ids     {spec['file']}: record with no id")
                bad += 1
                continue
            if not pattern.match(str(rid)):
                rep.error(f"ids     {spec['file']}: {rid!r} does not match {ns} pattern {spec['pattern']}")
                bad += 1
            if rid in seen:
                rep.error(f"ids     {spec['file']}: duplicate identifier {rid}")
                bad += 1
            seen.add(rid)
        counts[ns] = len(seen)
    rep.stats["counts"] = counts
    rep.check("identifiers", bad == 0, f"{bad} problem(s)")
    return counts


def check_references(by_type, instance, rep: Report):
    ns_to_type = {ns: spec["record_type"] for ns, spec in instance["namespaces"].items()}
    known = {ns: set(by_type.get(rt, {})) for ns, rt in ns_to_type.items()}
    broken = 0
    referenced = defaultdict(set)

    for rtype, fields in instance["references"].items():
        for rid, rec in by_type.get(rtype, {}).items():
            for field, ns in fields.items():
                val = rec.get(field)
                if val is None:
                    continue
                targets = val if isinstance(val, list) else [val]
                for t in targets:
                    if t is None:
                        continue
                    if t not in known.get(ns, set()):
                        rep.error(f"ref     {rtype}/{rid}: {field} -> {t} does not resolve in {ns}")
                        broken += 1
                    else:
                        referenced[ns].add(t)
    rep.stats["_referenced"] = {k: sorted(v) for k, v in referenced.items()}
    rep.check("references", broken == 0, f"{broken} broken reference(s)")
    return referenced


def check_symmetry(by_type, rep: Report):
    """Bidirectional relationships must agree in both directions."""
    pairs = [
        # (type_a, field_a, type_b, field_b)
        ("risk", "guardrails", "guardrail", "risks_addressed"),
        ("risk", "controls", "control", "linked_risks"),
        ("guardrail", "controls", "control", "guardrails"),
        ("risk", "user_stories", "user_story", None),
    ]
    asym = 0
    for ta, fa, tb, fb in pairs:
        if fb is None:
            continue
        for rid, rec in by_type.get(ta, {}).items():
            for target in rec.get(fa) or []:
                other = by_type.get(tb, {}).get(target)
                if other is None:
                    continue
                back = other.get(fb) or []
                if rid not in back:
                    rep.warn(f"symm    {ta}/{rid} cites {target}, but {tb}/{target}.{fb} does not cite it back")
                    asym += 1
    rep.check("symmetry", asym == 0, f"{asym} asymmetric link(s)")


def check_invariants(by_type, instance, rep: Report):
    risks = by_type.get("risk", {})
    controls = by_type.get("control", {})
    guardrails = by_type.get("guardrail", {})
    acceptances = by_type.get("risk_acceptance", {})
    failures = defaultdict(int)

    sev_by_rule = {inv["rule"]: inv for inv in instance.get("invariants", [])}

    def emit(rule, msg):
        inv = sev_by_rule.get(rule, {})
        (rep.error if inv.get("severity") == "error" else rep.warn)(f"inv     [{rule}] {msg}")
        failures[rule] += 1

    if "every_guardrail_has_assurance_test" in sev_by_rule:
        for gid, g in guardrails.items():
            if not (g.get("assurance_tests") or []):
                emit("every_guardrail_has_assurance_test", f"{gid} has no assurance test")

    if "every_control_reaches_a_metric" in sev_by_rule:
        for cid, c in controls.items():
            reaches = any(risks.get(r, {}).get("affected_metrics") for r in c.get("linked_risks") or [])
            if not reaches:
                emit("every_control_reaches_a_metric",
                     f"{cid} reaches no metric via any linked risk — unmonitorable")

    if "critical_risk_has_guardrail" in sev_by_rule:
        for rid, r in risks.items():
            if r.get("severity") == "Critical":
                if not (r.get("guardrails") or []):
                    emit("critical_risk_has_guardrail", f"{rid} is Critical with no guardrail")
                accepted = [a for a in acceptances.values()
                            if a.get("risk_id") == rid and a.get("decision", "").startswith("accepted")]
                if accepted:
                    emit("critical_risk_has_guardrail",
                         f"{rid} is Critical but has an acceptance record ({accepted[0]['id']}) — not permitted")

    if "must_address_risk_is_covered" in sev_by_rule:
        accepted_ids = {a.get("risk_id") for a in acceptances.values()}
        for rid, r in risks.items():
            if r.get("standards_priority") == "must_address":
                if not (r.get("guardrails") or []) and rid not in accepted_ids:
                    emit("must_address_risk_is_covered",
                         f"{rid} is must_address with neither a guardrail nor an acceptance record")

    rep.stats["invariant_failures"] = dict(failures)
    rep.check("invariants", not any(
        sev_by_rule.get(k, {}).get("severity") == "error" for k in failures), f"{sum(failures.values())} failure(s)")


def check_orphans(by_type, instance, referenced, rep: Report):
    orphans = defaultdict(list)
    for ns, spec in instance["namespaces"].items():
        rtype = spec["record_type"]
        defined = set(by_type.get(rtype, {}))
        # Records that are entry points by design are not orphans.
        if ns in {"RK", "REC", "RA", "GP", "PERSONA"}:
            continue
        unreferenced = sorted(defined - referenced.get(ns, set()))
        if unreferenced:
            orphans[ns] = unreferenced
            rep.warn(f"orphan  {ns}: {len(unreferenced)} identifier(s) defined but never referenced: "
                     f"{', '.join(unreferenced[:12])}{' …' if len(unreferenced) > 12 else ''}")
    rep.stats["orphans"] = dict(orphans)
    rep.check("orphans", not orphans, f"{sum(len(v) for v in orphans.values())} orphan(s)")


def check_readme_counts(counts, rep: Report):
    """Counts are read from the identifier table in README.md, matched by the
    namespace code in the first cell. Prose elsewhere in the README is ignored —
    counting bare numbers in prose produces false positives ('3 risk acceptances'
    is not a claim about the number of risks)."""
    readme = ROOT / "README.md"
    if not readme.exists():
        rep.check("readme counts", True, "no README")
        return
    ns_alias = {"D/M/B/EC": "PERSONA"}
    bad = checked = 0
    row = re.compile(r"^\|\s*`?([A-Z/]+)(?:-x+)?`?\s*\|[^|]*\|\s*(\d+)\b[^|]*\|")
    for line in readme.read_text(encoding="utf-8").splitlines():
        m = row.match(line.strip())
        if not m:
            continue
        ns = ns_alias.get(m.group(1), m.group(1))
        if ns not in counts:
            continue
        checked += 1
        stated, actual = int(m.group(2)), counts[ns]
        if stated != actual:
            rep.error(f"counts  README identifier table says {stated} for {ns}; data/ contains {actual}")
            bad += 1
    if checked == 0:
        rep.warn("counts  no identifier table rows found in README.md — counts unchecked")
    rep.check("readme counts", bad == 0, f"{checked} row(s) checked, {bad} mismatch(es)")


def check_coverage_stats(by_type, rep: Report):
    """Not pass/fail — visibility. These are the numbers the task force needs."""
    controls = by_type.get("control", {})
    guardrails = by_type.get("guardrail", {})
    risks = by_type.get("risk", {})
    acceptances = by_type.get("risk_acceptance", {})
    rep.stats["triage"] = {
        "controls_unassigned_status": sum(1 for c in controls.values()
                                          if c.get("standards_status") in (None, "unassigned")),
        "guardrails_unassigned_status": sum(1 for g in guardrails.values()
                                            if g.get("standards_status") in (None, "unassigned")),
        "risks_must_address": sum(1 for r in risks.values()
                                  if r.get("standards_priority") == "must_address"),
        "risks_critical": sum(1 for r in risks.values() if r.get("severity") == "Critical"),
        "acceptances_pending": sum(1 for a in acceptances.values()
                                   if a.get("decision") == "pending"),
        "metrics_without_monitoring": sum(1 for m in by_type.get("metric", {}).values()
                                          if not m.get("monitoring")),
    }


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = ap.parse_args()

    data_dir = pathlib.Path(a.data)
    instance = load_yaml(data_dir / "instance.yaml")
    vocab = load_yaml(ROOT / "method" / "vocabularies.yaml")

    rep = Report()
    by_type, _ = load_records(data_dir, instance)

    counts = check_identifiers(data_dir, instance, rep)
    check_schema(by_type, rep)
    check_vocabularies(by_type, vocab, rep)
    referenced = check_references(by_type, instance, rep)
    check_symmetry(by_type, rep)
    check_invariants(by_type, instance, rep)
    check_orphans(by_type, instance, referenced, rep)
    check_readme_counts(counts, rep)
    check_coverage_stats(by_type, rep)
    rep.stats.pop("_referenced", None)

    failed = bool(rep.errors) or (a.strict and bool(rep.warnings))

    summary = (" · ".join(f"{v} {k}" for k, v in counts.items())
               + f" · {len(rep.errors)} errors · {len(rep.warnings)} warnings")

    if a.json:
        print(json.dumps({"ok": not failed, "counts": counts, "errors": rep.errors,
                          "warnings": rep.warnings, "stats": rep.stats}, indent=2))
        return 1 if failed else 0

    if a.summary:
        print(f"validate.py: {summary}")
        return 1 if failed else 0

    print("RAHP artefact validation")
    print("=" * 72)
    print("\nRecord counts")
    for ns, n in counts.items():
        print(f"  {ns:<8} {n}")

    print("\nChecks")
    for name, ok, detail in rep.checks:
        print(f"  [{'ok' if ok else 'FAIL'}] {name:<16} {detail}")

    if rep.errors:
        print(f"\nERRORS ({len(rep.errors)})")
        for e in rep.errors:
            print(f"  {e}")
    if rep.warnings:
        print(f"\nWARNINGS ({len(rep.warnings)})")
        for w in rep.warnings:
            print(f"  {w}")

    t = rep.stats.get("triage", {})
    if t:
        print("\nTriage state (not pass/fail — this is the task force's work queue)")
        for k, v in t.items():
            print(f"  {k.replace('_', ' '):<34} {v}")

    print("\n" + "-" * 72)
    print("FAIL" if failed else "PASS", "·", summary)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

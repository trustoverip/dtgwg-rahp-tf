"""A01-P5: source-derived, constructed delegation experiment, not an agent or policy engine."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEADLINE = 12  # logical ticks; research protocol, not a Matrix-prescribed SLA
GRANTS = {
    "root": (None, "book"), "child": ("root", "book"),
    "grandchild": ("child", "book"), "read": (None, "read"),
    **{g: (None, g) for g in ("calendar", "message", "purchase", "account")},
}
PARTIALS = ["calendar", "message", "purchase", "account"]
# ID, source scenario suffix, tick, path, operation, offered grants, expected effect.
# The oracle is the declared research protocol, not the gate's decision.
def protocol(deadline):
    if deadline < 10:
        raise ValueError('Deadline precedes revocation')
    return {
    "baseline": [
        ["B1", "POS", 9, "direct", "book", ["grandchild"], True],
        ["B2", "NEG", 9, "combined", "book", PARTIALS, False],
        ["B3", "ADV", 9, "recombine", "book", PARTIALS, False],
        ["B4", "POS", 9, "direct", "read", ["read"], True],
    ],
    "reassessed": [
        ["R1", "NEG", deadline, "direct", "book", ["grandchild"], False],
        ["R2", "NEG", deadline, "combined", "book", PARTIALS, False],
        ["R3", "ADV", deadline, "cached", "book", ["grandchild"], False],
        ["R4", "ADV", deadline + 1, "fallback", "book", ["grandchild"], False],
        ["R5", "ADV", deadline, "recombine", "book", PARTIALS, False],
        ["R6", "POS", deadline + 1, "direct", "read", ["read"], True],
        ["R7", "NEG", deadline + 1, "direct", "book", ["grandchild"], False],
    ],
    }


PROTOCOL = protocol(DEADLINE)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def eligible(grant, operation, revoked):
    """Require every ancestor to carry the requested operation and be current."""
    visited = set()
    while grant is not None:
        if grant in visited or grant in revoked or grant not in GRANTS:
            return False
        visited.add(grant)
        grant, scope = GRANTS[grant]
        if scope != operation:
            return False
    return bool(visited)


def context(phase, variant="reference", deadline=DEADLINE):
    return {"phase": phase, "variant": variant, "subject_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "protocol_sha256": digest(protocol(deadline)), "grant_graph": {k: list(v) for k, v in GRANTS.items()},
            "revocation": None if phase == "baseline" else {"grant": "root", "effective_tick": 10, "deadline_tick": deadline}}


def execute(case, ctx):
    ident, kind, tick, path, operation, offered, _ = case
    event = ctx["revocation"]
    revoked = {event["grant"]} if event and tick >= event["effective_tick"] else set()
    variant = ctx["variant"]
    checked_revocation = set() if variant == "cached-mutant" and path == "cached" else revoked
    if variant == "late-propagation-mutant" and event and tick < event["effective_tick"] + 3:
        checked_revocation = set()
    gate = any(eligible(g, operation, checked_revocation) for g in offered)
    if variant == "recombine-mutant" and path == "recombine" and revoked:
        gate = True
    # Separate observation of the mock actuator's effect, including a fault that bypasses the gate.
    effects = []
    if gate or (variant == "fallback-mutant" and path == "fallback"):
        effects.append({"operation": operation, "request": ident, "tick": tick})
    return {"id": ident, "scenario": "A01-P5-" + kind, "context": digest(ctx), "tick": tick,
            "path": path, "operation": operation, "offered": offered,
            "authority": sorted(revoked), "gate_allow": gate, "effects": effects}


def trial(case, observed, ctx):
    ident, kind, tick, path, operation, offered, expected = case
    binding = {"id": ident, "scenario": "A01-P5-" + kind, "context": digest(ctx), "tick": tick,
               "path": path, "operation": operation, "offered": offered}
    if not isinstance(observed, dict) or any(observed.get(k) != v for k, v in binding.items()):
        return "INDETERMINATE"
    gate = observed.get("gate_allow")
    effects = observed.get("effects")
    # A correctly bound counterexample is not concealed by an incomplete evidence bundle.
    expected_effects = [{"operation": operation, "request": ident, "tick": tick}] if expected else []
    effect_valid = isinstance(effects, list) and all(
        isinstance(e, dict) and set(e) == {"operation", "request", "tick"}
        and isinstance(e["operation"], str) and isinstance(e["request"], str) and type(e["tick"]) is int
        for e in effects)
    if (type(gate) is bool and gate != expected) or (effect_valid and effects != expected_effects):
        return "FAIL"
    event = ctx["revocation"]
    revoked = [event["grant"]] if event and tick >= event["effective_tick"] else []
    if type(gate) is not bool or not effect_valid or observed.get("authority") != revoked:
        return "INDETERMINATE"
    return "PASS"


def aggregate(phase, observations, ctx):
    deadline = ctx["revocation"]["deadline_tick"] if ctx["revocation"] else DEADLINE
    cases = {c[0]: c for c in protocol(deadline)[phase]}
    valid = [o for o in observations if isinstance(o, dict) and isinstance(o.get("id"), str) and o["id"] in cases]
    results = [trial(cases[o["id"]], o, ctx) for o in valid]
    if "FAIL" in results:
        return "FAIL"
    ids = [o["id"] for o in valid]
    if len(ids) != len(observations) or sorted(ids) != sorted(cases) or "INDETERMINATE" in results:
        return "INDETERMINATE"
    return "PASS"


def campaign(phase, variant="reference", deadline=DEADLINE):
    ctx = context(phase, variant, deadline)
    cases = protocol(deadline)[phase]
    obs = [execute(case, ctx) for case in cases]
    return {"context": ctx, "observations": obs,
            "trial_results": {c[0]: trial(c, o, ctx) for c, o in zip(cases, obs)},
            "protocol_result": aggregate(phase, obs, ctx)}


def replay():
    bindings = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in
                ("source-lock.json", "risks.yaml", "baseline-review.json", "reassessed-review.json")}
    return {"source_proposition": "A01-P5", "bindings": bindings,
            "baseline": campaign("baseline"), "reassessed": campaign("reassessed"),
            "challenges": {v: campaign("reassessed", v) for v in
                           ("cached-mutant", "fallback-mutant", "recombine-mutant", "late-propagation-mutant")},
            "matrix_campaign": "not-executed", "overall_assurance": "review-required"}


def reproduce():
    retained = json.loads((ROOT / "lifecycle-evidence.json").read_text())
    if replay() != retained:
        raise ValueError("Fresh execution or evidence bindings differ from retained observations")
    return retained


def verify_sources(workbook, wla):
    lock = json.loads((ROOT / "source-lock.json").read_text())
    for kind, path in (("workbook", workbook), ("wla", wla)):
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != lock["local_sources"][kind]["sha256"]:
            raise ValueError(f"{kind}: source digest mismatch")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit fresh evidence, without overwriting retained records")
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--wla", type=Path)
    args = parser.parse_args()
    if bool(args.workbook) != bool(args.wla):
        parser.error("provide both source copies or neither")
    if args.workbook:
        verify_sources(args.workbook, args.wla)
    if args.emit:
        print(json.dumps(replay(), separators=(",", ":"), sort_keys=True))
    else:
        report = reproduce()
        print(json.dumps({"source_bytes": "verified" if args.workbook else "not-reverified",
                          "baseline_protocol": report["baseline"]["protocol_result"],
                          "reassessed_protocol": report["reassessed"]["protocol_result"],
                          "challenges": {k: v["protocol_result"] for k, v in report["challenges"].items()},
                          "matrix_campaign": report["matrix_campaign"], "overall_assurance": report["overall_assurance"]}, indent=2))

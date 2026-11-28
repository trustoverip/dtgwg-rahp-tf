"""Offline constructed RAHP/Matrix research fixture. NOT operational assurance."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ROLES={"authority","gate","capability","execution"}
def evaluate(data):
    if not data.get("subject",{}).get("revision"): raise ValueError("revision missing")
    if set(data["required_evidence_roles"]) != ROLES: raise ValueError("changed evidence roles")
    seen=set(); out=[]
    for s in data["scenarios"]:
        if s["id"] in seen: raise ValueError("duplicate scenario")
        seen.add(s["id"])
        if s["permission"] not in {"active","revoked","suspended","expired","unknown"}: raise ValueError("unknown permission state")
        if s["gate"] not in {"allow","deny"}: raise ValueError("invalid gate")
        if set(s["evidence"])-ROLES or len(s["evidence"])!=len(set(s["evidence"])): raise ValueError("invalid evidence")
        missing=sorted(ROLES-set(s["evidence"]))
        valid=s["permission"]=="active" and s["permission_scope"]=="booking" and s["capability"]
        violation=(s["booking_executed"] and not valid) or (s["gate"]=="allow" and not valid)
        if violation or (s["booking_executed"] != (s["gate"]=="allow")): status="FAIL"
        elif missing or s["permission"]=="unknown": status="INDETERMINATE"
        elif valid and s["gate"]=="deny": status="REVIEW REQUIRED"
        else: status="PASS"
        out.append({"id":s["id"],"outcome":status,"missing_roles":missing})
    dispositions=data["material_change"]["dispositions"]
    if len({d["evidence"] for d in dispositions})!=len(dispositions): raise ValueError("duplicate disposition")
    if any(d["state"] not in {"retained","stale","weakened","invalid","contradicted","unresolved"} for d in dispositions): raise ValueError("invalid disposition")
    return {"fixture_validation":"complete","target_assurance":"not-assessed","human_review":"required","results":out,"material_change":data["material_change"]}
if __name__=="__main__":
    actual=evaluate(json.loads((ROOT/"cases.json").read_text()))
    expected=json.loads((ROOT/"expected.json").read_text())
    if actual!=expected: raise SystemExit("INCOMPLETE: fresh observations differ from retained expected result")
    print(json.dumps(actual,indent=2))

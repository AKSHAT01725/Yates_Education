#!/usr/bin/env python3
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []
for code in ("FR", "PM"):
    path = ROOT / "data" / "question-banks" / f"{code.lower()}.json"
    bank = json.loads(path.read_text(encoding="utf-8"))
    if bank.get("subject") != code: errors.append(f"{path}: subject mismatch")
    ids = set()
    for i, q in enumerate(bank.get("questions", [])):
        qid = q.get("id")
        if not qid or qid in ids: errors.append(f"{code}[{i}]: missing/duplicate id {qid!r}")
        ids.add(qid)
        if q.get("subject") != code: errors.append(f"{code}[{qid}]: wrong subject")
        if q.get("verification", {}).get("status") != "verified" and q.get("published"):
            errors.append(f"{code}[{qid}]: unverified question is published")
        if not q.get("source", {}).get("questionPages"):
            errors.append(f"{code}[{qid}]: missing source page reference")
    if bank.get("published") and any(q.get("verification",{}).get("status")!="verified" for q in bank.get("questions",[])):
        errors.append(f"{code}: bank marked published with unverified questions")
if errors:
    print("\n".join(errors)); sys.exit(1)
print("FR/PM bank manifests valid; no cross-subject records or unverified published questions.")

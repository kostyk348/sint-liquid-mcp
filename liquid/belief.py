import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import DATA_DIR

BELIEFS_FILE = DATA_DIR / "beliefs.json"

def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _load():
    _ensure_dir()
    if BELIEFS_FILE.exists():
        return json.loads(BELIEFS_FILE.read_text())
    return []

def _save(beliefs):
    _ensure_dir()
    BELIEFS_FILE.write_text(json.dumps(beliefs, indent=2, default=str))

def upsert(claim, status="HYPOTHESIS", confidence=0.5, source="", domain="general", tags=None):
    beliefs = _load()
    now = datetime.now(timezone.utc).isoformat()

    for b in beliefs:
        if b["claim"] == claim:
            old_status = b["status"]
            old_confidence = b["confidence"]

            changed = old_status != status or old_confidence != confidence

            b["status"] = status
            b["confidence"] = confidence
            b["source"] = source
            b["domain"] = domain
            b["tags"] = tags or []
            b["updated"] = now

            if changed:
                reasons = []
                if old_status != status:
                    reasons.append(f"status: {old_status}->{status}")
                if old_confidence != confidence:
                    reasons.append(f"confidence: {old_confidence}->{confidence}")
                b["revision_chain"].append({
                    "old_status": old_status,
                    "new_status": status,
                    "reason": "; ".join(reasons),
                    "timestamp": now
                })

            _save(beliefs)
            return b

    belief = {
        "id": str(uuid.uuid4()),
        "claim": claim,
        "status": status,
        "confidence": confidence,
        "source": source,
        "domain": domain,
        "tags": tags or [],
        "created": now,
        "updated": now,
        "revision_chain": [],
        "contradiction_ids": [],
    }
    beliefs.append(belief)
    _save(beliefs)
    return belief

def find(query):
    beliefs = _load()
    for b in beliefs:
        if b["id"] == query:
            return b
    for b in beliefs:
        if b["claim"] == query:
            return b
    return None

def get_by_id(claim_id):
    beliefs = _load()
    for b in beliefs:
        if b["id"] == claim_id:
            return b
    return None

def get_all():
    return _load()

def update(belief):
    beliefs = _load()
    for i, b in enumerate(beliefs):
        if b["id"] == belief["id"]:
            beliefs[i] = belief
            break
    _save(beliefs)

def list_domains():
    beliefs = _load()
    domains = set()
    for b in beliefs:
        if b["domain"]:
            domains.add(b["domain"])
    return sorted(domains)

def stats():
    beliefs = _load()
    total = len(beliefs)
    statuses = {}
    total_revisions = 0
    for b in beliefs:
        statuses[b["status"]] = statuses.get(b["status"], 0) + 1
        total_revisions += len(b["revision_chain"])
    return {
        "total_beliefs": total,
        "by_status": statuses,
        "total_revisions": total_revisions,
    }

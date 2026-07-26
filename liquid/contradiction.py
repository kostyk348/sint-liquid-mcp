import json
import uuid
from datetime import datetime, timezone

from config import DATA_DIR
from . import belief

CONTRADICTIONS_FILE = DATA_DIR / "contradictions.json"

def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _load():
    _ensure_dir()
    if CONTRADICTIONS_FILE.exists():
        return json.loads(CONTRADICTIONS_FILE.read_text())
    return []

def _save(contradictions):
    _ensure_dir()
    CONTRADICTIONS_FILE.write_text(json.dumps(contradictions, indent=2, default=str))

def register(claim1_id, claim2_id, contradiction_type="LOGICAL"):
    b1 = belief.get_by_id(claim1_id)
    b2 = belief.get_by_id(claim2_id)
    if not b1 or not b2:
        return None

    contradictions = _load()
    now = datetime.now(timezone.utc).isoformat()

    contradiction = {
        "id": str(uuid.uuid4()),
        "claim1_id": claim1_id,
        "claim2_id": claim2_id,
        "type": contradiction_type,
        "resolved": False,
        "resolution": None,
        "correct_claim_id": None,
        "created": now,
        "resolved_at": None,
    }
    contradictions.append(contradiction)
    _save(contradictions)

    b1["contradiction_ids"].append(contradiction["id"])
    belief.update(b1)
    b2["contradiction_ids"].append(contradiction["id"])
    belief.update(b2)

    return contradiction

def resolve(contradiction_id, resolution, correct_claim_id=None):
    contradictions = _load()
    now = datetime.now(timezone.utc).isoformat()

    for c in contradictions:
        if c["id"] == contradiction_id:
            c["resolved"] = True
            c["resolution"] = resolution
            c["correct_claim_id"] = correct_claim_id
            c["resolved_at"] = now
            _save(contradictions)
            return c

    return None

def get_all():
    return _load()

def get_unresolved():
    return [c for c in _load() if not c["resolved"]]

def stats():
    contradictions = _load()
    total = len(contradictions)
    resolved = sum(1 for c in contradictions if c["resolved"])
    types = {}
    for c in contradictions:
        types[c["type"]] = types.get(c["type"], 0) + 1
    return {
        "total_contradictions": total,
        "resolved": resolved,
        "unresolved": total - resolved,
        "by_type": types,
    }

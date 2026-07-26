from datetime import datetime, timezone

from . import belief

def add_revision(claim_id, new_status, new_confidence, reason):
    b = belief.get_by_id(claim_id)
    if not b:
        return None

    now = datetime.now(timezone.utc).isoformat()
    old_status = b["status"]

    b["revision_chain"].append({
        "old_status": old_status,
        "new_status": new_status,
        "reason": reason,
        "timestamp": now
    })

    b["status"] = new_status
    b["confidence"] = new_confidence
    b["updated"] = now

    belief.update(b)
    return b

def get_history(claim_id):
    b = belief.get_by_id(claim_id)
    if not b:
        return None
    return {
        "id": b["id"],
        "claim": b["claim"],
        "current_status": b["status"],
        "current_confidence": b["confidence"],
        "revision_count": len(b["revision_chain"]),
        "revision_chain": b["revision_chain"],
    }

import json

from mcp.server.fastmcp import FastMCP

from liquid import belief, revision, contradiction
from config import NAME, VERSION

mcp = FastMCP(NAME)


@mcp.tool()
def liquid_belief(
    claim: str,
    status: str = "HYPOTHESIS",
    confidence: float = 0.5,
    source: str = "",
    domain: str = "general",
    tags: list[str] | None = None,
) -> str:
    result = belief.upsert(claim, status, confidence, source, domain, tags or [])
    return json.dumps(result, indent=2)


@mcp.tool()
def liquid_query(claim_query: str) -> str:
    b = belief.find(claim_query)
    if not b:
        return json.dumps({"error": "Belief not found"})
    return json.dumps(b, indent=2)


@mcp.tool()
def liquid_contradict(
    claim1_id: str,
    claim2_id: str,
    contradiction_type: str = "LOGICAL",
) -> str:
    c = contradiction.register(claim1_id, claim2_id, contradiction_type)
    if not c:
        return json.dumps({"error": "One or both claims not found"})
    return json.dumps(c, indent=2)


@mcp.tool()
def liquid_resolve(claim_id: str, resolution: str) -> str:
    b = belief.get_by_id(claim_id)
    if not b:
        return json.dumps({"error": "Claim not found"})
    all_c = contradiction.get_all()
    resolved = []
    for c in all_c:
        if not c["resolved"] and (c["claim1_id"] == claim_id or c["claim2_id"] == claim_id):
            r = contradiction.resolve(c["id"], resolution, correct_claim_id=claim_id)
            if r:
                resolved.append(r)
    return json.dumps({"resolved": len(resolved), "contradictions": resolved}, indent=2)


@mcp.tool()
def liquid_revise(
    claim_id: str,
    new_status: str,
    new_confidence: float,
    reason: str,
) -> str:
    r = revision.add_revision(claim_id, new_status, new_confidence, reason)
    if not r:
        return json.dumps({"error": "Claim not found"})
    return json.dumps(r, indent=2)


@mcp.tool()
def liquid_history(claim_id: str) -> str:
    h = revision.get_history(claim_id)
    if not h:
        return json.dumps({"error": "Claim not found"})
    return json.dumps(h, indent=2)


@mcp.tool()
def liquid_domains() -> str:
    return json.dumps(belief.list_domains(), indent=2)


@mcp.tool()
def liquid_stats() -> str:
    bstats = belief.stats()
    cstats = contradiction.stats()
    return json.dumps({**bstats, **cstats}, indent=2)


if __name__ == "__main__":
    mcp.run()

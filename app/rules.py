"""Deterministic underwriting rules that run before the model.

Each hit carries a weight; the sum becomes a floor under the final risk score.
"""

from datetime import date


def _parse(d: str):
    try:
        return date.fromisoformat(d)
    except (TypeError, ValueError):
        return None


def run_rule_checks(meta: dict) -> list[dict]:
    hits = []
    amount = meta.get("claimed_amount") or 0
    limit = meta.get("coverage_limit") or 0
    incident = _parse(meta.get("incident_date"))
    start = _parse(meta.get("policy_start_date"))
    filed = _parse(meta.get("date_filed")) or date.today()

    if limit and amount > limit:
        hits.append({"rule": "Claim exceeds coverage limit", "weight": 35,
                     "detail": f"Claimed {amount:,.0f} vs limit {limit:,.0f}"})
    elif limit and amount >= 0.9 * limit:
        hits.append({"rule": "Claim near coverage limit", "weight": 15,
                     "detail": f"Claimed {amount / limit:.0%} of limit"})

    if incident and start:
        if incident < start:
            hits.append({"rule": "Incident before policy start", "weight": 60,
                         "detail": f"Incident {incident} precedes policy start {start}"})
        elif (incident - start).days <= 30:
            hits.append({"rule": "Incident within 30 days of policy start", "weight": 25,
                         "detail": f"{(incident - start).days} days after inception"})

    if incident:
        if incident > filed:
            hits.append({"rule": "Incident date in the future", "weight": 50,
                         "detail": f"Incident {incident} is after filing date {filed}"})
        elif (filed - incident).days > 90:
            hits.append({"rule": "Late reporting (>90 days)", "weight": 15,
                         "detail": f"Reported {(filed - incident).days} days after incident"})

    prior = meta.get("prior_claims_last_3_years") or 0
    if prior >= 3:
        hits.append({"rule": "High claim frequency", "weight": 20,
                     "detail": f"{prior} prior claims in 3 years"})

    if amount and amount % 1000 == 0 and amount >= 5000:
        hits.append({"rule": "Round-number claim amount", "weight": 5,
                     "detail": f"{amount:,.0f} is an exact round figure"})
    return hits

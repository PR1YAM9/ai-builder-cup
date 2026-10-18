"""Deterministic underwriting rules that run before the model.

Each hit carries a weight; the sum becomes a floor under the final risk score.
Thresholds and weights are configurable per insurer through the RULES_CONFIG
environment variable (a JSON object overriding any keys in DEFAULT_RULES).
"""

import json
import os
from datetime import date

DEFAULT_RULES = {
    "over_limit_weight": 35,
    "near_limit_ratio": 0.9,
    "near_limit_weight": 15,
    "before_policy_weight": 60,
    "new_policy_days": 30,
    "new_policy_weight": 25,
    "future_incident_weight": 50,
    "late_report_days": 90,
    "late_report_weight": 15,
    "frequency_threshold": 3,
    "frequency_weight": 20,
    "round_amount_min": 5000,
    "round_amount_weight": 5,
}


def load_rules() -> dict:
    rules = dict(DEFAULT_RULES)
    override = os.getenv("RULES_CONFIG")
    if override:
        rules.update({k: v for k, v in json.loads(override).items() if k in DEFAULT_RULES})
    return rules


RULES = load_rules()


def _parse(d: str):
    try:
        return date.fromisoformat(d)
    except (TypeError, ValueError):
        return None


def run_rule_checks(meta: dict, cfg: dict = RULES) -> list[dict]:
    hits = []
    amount = meta.get("claimed_amount") or 0
    limit = meta.get("coverage_limit") or 0
    incident = _parse(meta.get("incident_date"))
    start = _parse(meta.get("policy_start_date"))
    filed = _parse(meta.get("date_filed")) or date.today()

    if limit and amount > limit:
        hits.append({"rule": "Claim exceeds coverage limit", "weight": cfg["over_limit_weight"],
                     "detail": f"Claimed {amount:,.0f} vs limit {limit:,.0f}"})
    elif limit and amount >= cfg["near_limit_ratio"] * limit:
        hits.append({"rule": "Claim near coverage limit", "weight": cfg["near_limit_weight"],
                     "detail": f"Claimed {amount / limit:.0%} of limit"})

    if incident and start:
        if incident < start:
            hits.append({"rule": "Incident before policy start", "weight": cfg["before_policy_weight"],
                         "detail": f"Incident {incident} precedes policy start {start}"})
        elif (incident - start).days <= cfg["new_policy_days"]:
            hits.append({"rule": f"Incident within {cfg['new_policy_days']} days of policy start",
                         "weight": cfg["new_policy_weight"],
                         "detail": f"{(incident - start).days} days after inception"})

    if incident:
        if incident > filed:
            hits.append({"rule": "Incident date in the future", "weight": cfg["future_incident_weight"],
                         "detail": f"Incident {incident} is after filing date {filed}"})
        elif (filed - incident).days > cfg["late_report_days"]:
            hits.append({"rule": f"Late reporting (>{cfg['late_report_days']} days)",
                         "weight": cfg["late_report_weight"],
                         "detail": f"Reported {(filed - incident).days} days after incident"})

    prior = meta.get("prior_claims_last_3_years") or 0
    if prior >= cfg["frequency_threshold"]:
        hits.append({"rule": "High claim frequency", "weight": cfg["frequency_weight"],
                     "detail": f"{prior} prior claims in 3 years"})

    if amount and amount % 1000 == 0 and amount >= cfg["round_amount_min"]:
        hits.append({"rule": "Round-number claim amount", "weight": cfg["round_amount_weight"],
                     "detail": f"{amount:,.0f} is an exact round figure"})
    return hits

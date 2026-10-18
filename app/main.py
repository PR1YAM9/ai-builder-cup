"""ClaimGuard AI - multimodal insurance claim fraud & risk analyzer.

FastAPI service that sends claim evidence (damage photos, invoices/receipts,
claimant narrative, policy metadata) to Gemini on Vertex AI and returns a
structured fraud-risk assessment. Deterministic rule checks run alongside the
model so the final score blends policy rules with AI reasoning.
"""

import json
import os
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from pydantic import BaseModel

from .rules import run_rule_checks
from .schema import ASSESSMENT_SCHEMA

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_FILE_BYTES = 8 * 1024 * 1024
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "application/pdf"}

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
SAMPLES_DIR = BASE_DIR / "samples"


def make_client() -> genai.Client:
    # Local dev can use an AI Studio key; Cloud Run uses Vertex AI via the
    # service account (GOOGLE_CLOUD_PROJECT is set in the deploy script).
    if os.getenv("GEMINI_API_KEY"):
        return genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )


client = make_client()
app = FastAPI(title="ClaimGuard AI")

# In-memory claim store for the demo (history list + follow-up chat context).
CLAIMS: dict[str, dict] = {}

SYSTEM_PROMPT = """You are ClaimGuard, a senior insurance claims fraud investigator.
You receive a claim: policy metadata, the claimant's written description, damage
photos, and supporting documents (invoices, repair estimates, receipts, reports).

Your job:
1. Extract key facts from every document (vendor, dates, line items, totals).
2. Describe what the photos actually show (object, damage type, severity, any
   signs of staging, reuse, editing, stock imagery, or mismatched vehicle/item).
3. Cross-check everything: narrative vs photos, photos vs invoice line items,
   invoice totals vs claimed amount, dates vs incident date and policy period,
   arithmetic on invoices, plausibility of repair costs for the damage seen.
4. List concrete red flags with the specific evidence. Do not invent flags; if
   evidence is consistent, say so. Missing evidence is a flag only if it matters.
5. Score fraud risk 0-100 (0-29 low, 30-59 medium, 60-100 high) and recommend
   APPROVE, MANUAL_REVIEW, or INVESTIGATE.

Be specific, cite which file the evidence came from, and be fair to honest
claimants. Write for a claims adjuster who must act on this in two minutes."""


@app.post("/api/analyze")
async def analyze(
    description: str = Form(...),
    claim_type: str = Form("auto"),
    claimed_amount: float = Form(0),
    incident_date: str = Form(""),
    policy_start: str = Form(""),
    coverage_limit: float = Form(0),
    prior_claims: int = Form(0),
    claimant_name: str = Form(""),
    date_filed: str = Form(""),
    files: list[UploadFile] = File(default=[]),
):
    parts: list[types.Part] = []
    file_names = []
    for f in files:
        data = await f.read()
        if not data:
            continue
        mime = f.content_type or "application/octet-stream"
        if mime not in ALLOWED_MIME:
            raise HTTPException(400, f"Unsupported file type for {f.filename}: {mime}")
        if len(data) > MAX_FILE_BYTES:
            raise HTTPException(400, f"{f.filename} exceeds 8 MB")
        parts.append(types.Part.from_text(text=f"--- File: {f.filename} ---"))
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))
        file_names.append(f.filename)

    metadata = {
        "claimant_name": claimant_name,
        "claim_type": claim_type,
        "claimed_amount": claimed_amount,
        "incident_date": incident_date,
        "policy_start_date": policy_start,
        "coverage_limit": coverage_limit,
        "prior_claims_last_3_years": prior_claims,
        "date_filed": date_filed or date.today().isoformat(),
    }
    rule_flags = run_rule_checks(metadata)

    prompt = (
        f"CLAIM METADATA:\n{json.dumps(metadata, indent=2)}\n\n"
        f"CLAIMANT DESCRIPTION:\n{description}\n\n"
        f"ATTACHED FILES: {', '.join(file_names) or 'none'}\n\n"
        f"DETERMINISTIC POLICY RULE HITS (already verified and shown to the adjuster "
        f"separately; factor them into the score but do NOT repeat them in red_flags):\n"
        f"{json.dumps(rule_flags, indent=2)}"
    )

    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt), *parts])],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=ASSESSMENT_SCHEMA,
                temperature=0.2,
            ),
        )
        assessment = json.loads(resp.text)
    except Exception as e:  # surface model errors to the UI instead of a bare 500
        raise HTTPException(502, f"Gemini analysis failed: {e}") from e

    # Blend: rule hits put a floor under the AI score so hard policy breaches
    # can never be scored as low risk.
    rule_floor = min(100, sum(r["weight"] for r in rule_flags))
    ai_score = int(assessment.get("risk_score", 0))
    final = max(ai_score, rule_floor)
    assessment["ai_score"] = ai_score
    assessment["rule_score"] = rule_floor
    assessment["risk_score"] = final
    assessment["risk_level"] = "HIGH" if final >= 60 else "MEDIUM" if final >= 30 else "LOW"
    if final >= 60 and assessment.get("recommendation") == "APPROVE":
        assessment["recommendation"] = "INVESTIGATE"
    assessment["rule_flags"] = rule_flags

    claim_id = "CLM-" + uuid.uuid4().hex[:6].upper()
    CLAIMS[claim_id] = {
        "id": claim_id,
        "created": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata,
        "description": description,
        "files": file_names,
        "assessment": assessment,
        "chat": [],
    }
    return {"claim_id": claim_id, "metadata": metadata, "assessment": assessment}


class ChatIn(BaseModel):
    question: str


@app.post("/api/claims/{claim_id}/chat")
def chat(claim_id: str, body: ChatIn):
    claim = CLAIMS.get(claim_id)
    if not claim:
        raise HTTPException(404, "Claim not found")
    context = json.dumps(
        {k: claim[k] for k in ("metadata", "description", "files", "assessment")}, indent=2
    )
    history = [
        types.Content(role=m["role"], parts=[types.Part.from_text(text=m["text"])])
        for m in claim["chat"]
    ]
    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=[
                *history,
                types.Content(role="user", parts=[types.Part.from_text(text=body.question)]),
            ],
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are ClaimGuard, assisting a claims adjuster with a claim you "
                    "already assessed. Answer concisely (under 150 words), grounded only "
                    "in this claim record. If asked to draft a message to the claimant, "
                    "keep it professional and non-accusatory.\n\nCLAIM RECORD:\n" + context
                ),
                temperature=0.3,
            ),
        )
    except Exception as e:
        raise HTTPException(502, f"Gemini chat failed: {e}") from e
    claim["chat"] += [
        {"role": "user", "text": body.question},
        {"role": "model", "text": resp.text},
    ]
    return {"answer": resp.text}


@app.get("/api/claims")
def list_claims():
    return [
        {
            "id": c["id"],
            "created": c["created"],
            "claimant": c["metadata"]["claimant_name"],
            "type": c["metadata"]["claim_type"],
            "amount": c["metadata"]["claimed_amount"],
            "risk_score": c["assessment"]["risk_score"],
            "risk_level": c["assessment"]["risk_level"],
            "recommendation": c["assessment"]["recommendation"],
        }
        for c in sorted(CLAIMS.values(), key=lambda c: c["created"], reverse=True)
    ]


@app.get("/api/samples")
def list_samples():
    index = SAMPLES_DIR / "samples.json"
    return json.loads(index.read_text(encoding="utf-8")) if index.exists() else []


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}


app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")

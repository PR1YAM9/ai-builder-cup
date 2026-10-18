# ClaimGuard AI: Submission Kit

- **Live prototype:** https://claimguard-ai-342329356911.us-central1.run.app
- **GitHub:** https://github.com/PR1YAM9/ai-builder-cup
- **Track:** Banking, Financial Services & Insurance (fraud detection · document intelligence · risk assessment)

---

## 1. Brief description

**Short (≈50 words)**
> ClaimGuard AI is a multimodal insurance-claim fraud checker. An adjuster uploads the claimant's statement, damage photos and supporting documents. Gemini on Vertex AI reads every file, cross-checks them against each other and against policy rules, and returns an explainable fraud-risk score, cited red flags and a recommended action in under 30 seconds.

**Long (≈150 words)**
> Insurance fraud is estimated to cost U.S. consumers over $300 billion a year (Coalition Against Insurance Fraud, 2022). Adjusters still catch it by hand-checking invoices, photos, police reports and statements against each other.
>
> ClaimGuard AI automates that cross-check. Gemini 2.5 Flash on Vertex AI takes the claimant's statement, photos and documents (images or PDFs) in a single multimodal call. It extracts key fields, describes the damage it sees, and flags contradictions: invoices dated before the incident, line items that don't add up, repairs that don't match the described damage, conflicting police reports. A deterministic policy-rule engine runs alongside (coverage limits, new-policy claims, late reporting, claim frequency) and sets a floor under the AI score, so a hard policy breach is never scored as low risk. Every claim gets a 0–100 risk score, APPROVE / MANUAL REVIEW / INVESTIGATE, cited evidence, next steps, and a grounded chat assistant that can explain the score or draft a message to the claimant. It runs serverless on Cloud Run.

---

## 2. Pitch deck content (slide by slide)

Map these onto the prescribed template. If the template has fewer slides, merge 5+6 and 8+9.

### Slide 1: Title
- **ClaimGuard AI**
- *Multimodal claim fraud triage in 30 seconds, powered by Gemini on Vertex AI*
- Priyam Maini · AI Builder Cup · BFSI track
- Live demo URL + GitHub URL

### Slide 2: The problem
- Insurance fraud is estimated at **$308.6B a year** in the U.S. alone (Coalition Against Insurance Fraud, 2022)
- Adjusters cross-check photos, invoices, police reports and statements **by hand**
- That's slow for honest claimants and easy to game for fraudsters: altered invoices, staged or reused photos, contradictory stories
- Rule-only systems miss **semantic** fraud (the story doesn't match the evidence); black-box ML can't explain its decisions to a regulator or an adjuster

### Slide 3: The solution
- An adjuster uploads a claim: statement + photos + documents (JPG / PNG / PDF)
- ClaimGuard returns in under 30 s:
  - **Fraud-risk score 0–100** and **APPROVE / MANUAL REVIEW / INVESTIGATE**
  - **Red flags with cited evidence** ("invoice dated 28 Sep, incident 1 Oct, s2_repair_invoice.png")
  - Consistency checks (pass / warn / fail), extracted fields, photo analysis, next steps
  - **Ask ClaimGuard:** a chat grounded in that claim ("Why this score?", "Draft a document request")

### Slide 4: How it works (architecture)
```
Adjuster UI ──► Cloud Run (FastAPI)
                 ├─ Policy rule engine (deterministic) ─┐
                 └─ Gemini 2.5 Flash on Vertex AI ◄─────┘
                      multimodal input → JSON-schema structured output
                 ▼
          Final score = max(AI score, rule floor)
```
- **One multimodal Gemini call** reads every image and PDF alongside the statement
- **Structured output** (response schema) gives typed, UI-ready results with no fragile parsing
- **Hybrid scoring:** hard policy breaches can't be talked down by the model
- **Grounded chat:** follow-up answers use only that claim's record

### Slide 5: What Gemini catches (demo results, live on Cloud Run)
| Claim | What ClaimGuard found | Verdict |
|---|---|---|
| Rear-end collision | Invoice, police report and statement agree | **10 · APPROVE** |
| Inflated repair invoice | Items sum to $4,750 but total says $9,000; front-end parts vs rear damage; invoice predates the incident | **95 · INVESTIGATE** |
| "Stolen" phone, new policy | Police report says *lost* on 30 Sep, two days **before** the purchase; location and story contradict; 3 prior claims | **90–100 · INVESTIGATE** |
| Kitchen water damage | Evidence consistent, but filed 109 days late with no photos | **45–55 · MANUAL REVIEW** |

### Slide 6: Why it's different
- **Cross-document reasoning**, not single-document OCR: it finds contradictions *between* files
- **Explainable by design:** every flag cites its source file, which supports audit and regulatory review
- **Human-in-the-loop:** it triages and recommends; the adjuster decides
- **Fair to honest claimants:** clean claims get fast-tracked rather than everyone getting the same scrutiny

### Slide 7: Google Cloud stack
| Service | Role |
|---|---|
| **Gemini 2.5 Flash on Vertex AI** | Multimodal document and photo understanding, reasoning, structured output, chat |
| **Cloud Run** | Serverless API and UI hosting, autoscaling |
| **Cloud Build + Artifact Registry** | Source-to-container deploys |
| *Roadmap:* Document AI, BigQuery, Pub/Sub, Firestore | High-volume parsing, fraud-ring analytics, event-driven intake, persistence |

### Slide 8: Impact
- **Minutes → ~30 seconds** of first-pass review per claim (measured 18–35 s per live demo claim)
- Clean claims are **fast-tracked**, which improves customer experience and NPS
- Investigators spend time on the **highest-risk** claims, with the evidence already assembled
- Every decision has a **reasoned audit trail**

### Slide 9: Roadmap
1. **BigQuery** claims history → cross-claim signals (same invoice reused, same vendor across many claims, fraud rings)
2. **Image forensics:** reverse-image search for stock or reused photos, EXIF date checks
3. **Document AI** processors for high-volume invoice parsing
4. **Pub/Sub** intake from claim portals and **Firestore** persistence, with adjuster feedback loops to tune thresholds
5. Extend to **health and travel** claims and **KYC / loan document** verification

### Slide 10: Thank you / links
- Live: https://claimguard-ai-342329356911.us-central1.run.app
- Code: https://github.com/PR1YAM9/ai-builder-cup
- Contact: Priyam Maini

---

## 3. Demo video script (target 2:30)

Before recording, open the live URL in a fresh tab and zoom the browser to about 110%. Run sample 1 once off-camera so the instance is warm. Gemini takes 20–30 s per claim, so **pause the recording while it thinks** (or cut that part in editing) to stay under 3 minutes.

| Time | On screen | Voice-over |
|---|---|---|
| **0:00–0:20** | Landing page at `/`, scroll slowly through "The problem" | "Insurance fraud costs an estimated three hundred billion dollars a year in the U.S. alone, and adjusters still catch it by hand-checking invoices, photos and police reports against each other. This is ClaimGuard AI. It does that cross-check in seconds with Gemini on Vertex AI." |
| **0:20–0:45** | Click **Try the demo** (opens `/app`), then **Sample 1 · Rear-end collision**; show the filled form and the two document thumbnails; click **Analyze with Gemini** | "Here's a typical auto claim: the claimant's statement, a repair invoice and a police report. ClaimGuard sends all of it to Gemini in one multimodal call, alongside our policy rules." |
| **0:45–1:00** | Result: score 10, APPROVE; scroll briefly through the consistency checks | "Everything lines up. The invoice matches the claimed amount and the police report matches the story. Low risk, approve. An honest customer gets paid fast." |
| **1:00–1:40** | Click **Sample 2 · Inflated repair invoice** → Analyze → score 95, INVESTIGATE; hover over each red flag | "Now a suspicious one. The claimant says the *back* of the car was hit. Gemini read the invoice and found front-end parts, a hood and a radiator. The line items add up to forty-seven fifty, but the total says nine thousand. The invoice is dated *before* the accident. And the same shop's own estimate was only fifteen fifty. Every flag cites the exact file it came from." |
| **1:40–2:05** | Scroll to **Ask ClaimGuard**; click "Draft a message to the claimant requesting more documents"; show the reply | "Adjusters can ask follow-up questions grounded in this claim. Here it drafts a professional, non-accusatory request for more documents, ready to send." |
| **2:05–2:20** | Quickly run **Sample 3**; show the 90+ score and the "lost before purchase" flag; then open the **Claims queue** tab | "Another one: a 'stolen' phone on a ten-day-old policy, where the police report says it was lost two days before it was even bought. The claims queue ranks everything by risk so investigators start with the worst cases." |
| **2:20–2:35** | Landing page "Integration" section with the curl example, then `/docs` | "For insurers it is plug-in: one REST API with key authentication, rule thresholds configurable per deployment, and a one-command install into their own Google Cloud project, so claim data never leaves their tenancy. Underneath: Gemini 2.5 Flash on Vertex AI, a deterministic rule floor, and Cloud Run. ClaimGuard AI: faster payouts for honest customers, and nowhere to hide for fraud." |

---

## 4. Deployment (how it's deployed and how to redeploy)

The app is **already live** on Cloud Run (service `claimguard-ai`, project `gen-lang-client-0913397478`, region `us-central1`). To push a change after editing code:

```bash
gcloud auth login --update-adc                 # only if your login has expired
gcloud config set project gen-lang-client-0913397478
bash deploy.sh                                 # run from the repo root in Git Bash
```

`deploy.sh` does the following:
1. Enables the Cloud Run, Cloud Build, Artifact Registry and Vertex AI APIs.
2. Grants the Cloud Run service account `roles/aiplatform.user` so it can call Gemini (no API key needed).
3. Runs `gcloud run deploy --source .`: Cloud Build builds the `Dockerfile` remotely (no local Docker), pushes the image to Artifact Registry and rolls out a new revision. The URL stays the same.
4. Prints the service URL. A redeploy takes about 4–6 minutes.

Check that it's up:
```bash
curl https://claimguard-ai-342329356911.us-central1.run.app/health
python scripts/test_samples.py https://claimguard-ai-342329356911.us-central1.run.app
```

To deploy into a **different** project: the project must have billing enabled. Then run `PROJECT_ID=<id> bash deploy.sh`.

Keeping it up through evaluation: `--min-instances 1` keeps one instance warm, so there are no cold starts and the demo claims queue isn't wiped. That instance bills continuously at a small rate. After judging, run `gcloud run services delete claimguard-ai --region us-central1` to stop the cost.

---

## 5. Talking points for Q&A
- **"What if Gemini is wrong?"** It triages; the adjuster decides. Policy-rule hits put a floor under the score, every flag cites evidence a human can check, and temperature is 0.2 for consistency.
- **"Why not a trained ML model?"** There's no labelled multimodal fraud dataset to train on in a hackathon, and tabular models can't read a police report. Gemini handles the semantic cross-checks. The roadmap adds BigQuery and Vertex AI tabular models for cross-claim patterns.
- **"Privacy?"** Runs in the insurer's own GCP project on Vertex AI, where customer data isn't used to train Google's models. The demo uses entirely synthetic documents.
- **"Scale?"** Cloud Run autoscales (currently 1–3 instances). Each claim is one model call (~20–30 s). The in-memory claims queue is demo-only and would move to Firestore or BigQuery in production.

"""Repeat-run benchmark: each sample claim N times, report verdict stability, latency and tokens.

Usage: python scripts/benchmark.py [base_url] [runs]   -> prints a table and writes docs/benchmark.json
"""

import json
import statistics
import sys
import time
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8765"
RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
EXPECTED = {0: "APPROVE", 1: "INVESTIGATE", 2: "INVESTIGATE", 3: "MANUAL_REVIEW", 4: "INVESTIGATE"}


def post(fields, files):
    boundary = uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for name in files:
        mime = "image/jpeg" if name.endswith(".jpg") else "image/png"
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="files"; filename="{name}"\r\n'
                 f"Content-Type: {mime}\r\n\r\n").encode() + (ROOT / "samples" / name).read_bytes() + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/api/analyze", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    t = time.time()
    with urllib.request.urlopen(req, timeout=240) as r:
        a = json.loads(r.read())["assessment"]
    a["wall_s"] = round(time.time() - t, 1)
    return a


samples = json.loads((ROOT / "samples" / "samples.json").read_text(encoding="utf-8"))
jobs = [(i, s) for i, s in enumerate(samples) for _ in range(RUNS)]
with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(lambda j: (j[0], post(j[1]["fields"], j[1]["files"])), jobs))

rows = []
for i, s in enumerate(samples):
    rs = [a for k, a in results if k == i]
    scores = [a["risk_score"] for a in rs]
    rows.append({
        "sample": s["label"],
        "files": len(s["files"]),
        "expected": EXPECTED[i],
        "verdicts": [a["recommendation"] for a in rs],
        "correct": sum(a["recommendation"] == EXPECTED[i] for a in rs),
        "runs": len(rs),
        "score_min": min(scores), "score_max": max(scores), "score_mean": round(statistics.mean(scores)),
        "latency_mean_s": round(statistics.mean(a["elapsed_s"] for a in rs), 1),
        "tokens_in_mean": round(statistics.mean(a["tokens"]["input"] for a in rs)),
        "tokens_out_mean": round(statistics.mean(a["tokens"]["output"] for a in rs)),
    })
    r = rows[-1]
    print(f"{r['sample']:<36} {r['correct']}/{r['runs']} correct  score {r['score_min']}-{r['score_max']} "
          f"(mean {r['score_mean']})  {r['latency_mean_s']}s  tokens in {r['tokens_in_mean']} out {r['tokens_out_mean']}")
(ROOT / "docs" / "benchmark.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

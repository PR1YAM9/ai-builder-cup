"""Run every sample claim through a running ClaimGuard server and print verdicts.

Usage: python scripts/test_samples.py [base_url]   (default http://localhost:8765)
"""

import json
import sys
import time
import urllib.request
import uuid
from pathlib import Path

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8765"
SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def post_multipart(url, fields, files):
    boundary = uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for name in files:
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="files"; filename="{name}"\r\n'
                 f"Content-Type: image/png\r\n\r\n").encode() + (SAMPLES / name).read_bytes() + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())


for s in json.loads((SAMPLES / "samples.json").read_text(encoding="utf-8")):
    t = time.time()
    res = post_multipart(BASE + "/api/analyze", s["fields"], s["files"])
    a = res["assessment"]
    print(f"\n=== {s['label']}  ({time.time() - t:.1f}s)")
    print(f"score {a['risk_score']} (ai {a['ai_score']}, rules {a['rule_score']}) {a['risk_level']} -> {a['recommendation']}")
    print("summary:", a["summary"])
    for f in a["red_flags"]:
        print(f"  [{f['severity']}] {f['signal']}: {f['evidence']}")

"""Structured-output schema Gemini must follow for a claim assessment."""

ASSESSMENT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "summary": {"type": "STRING", "description": "2-3 sentence verdict for the adjuster."},
        "risk_score": {"type": "INTEGER", "description": "Fraud risk 0-100."},
        "recommendation": {"type": "STRING", "enum": ["APPROVE", "MANUAL_REVIEW", "INVESTIGATE"]},
        "confidence": {"type": "STRING", "enum": ["LOW", "MEDIUM", "HIGH"]},
        "extracted_fields": {
            "type": "ARRAY",
            "description": "Key facts pulled from documents and photos.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "field": {"type": "STRING"},
                    "value": {"type": "STRING"},
                    "source": {"type": "STRING", "description": "File name or 'description'."},
                },
                "required": ["field", "value", "source"],
            },
        },
        "photo_findings": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "file": {"type": "STRING"},
                    "observation": {"type": "STRING"},
                },
                "required": ["file", "observation"],
            },
        },
        "consistency_checks": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "check": {"type": "STRING"},
                    "status": {"type": "STRING", "enum": ["PASS", "WARN", "FAIL"]},
                    "detail": {"type": "STRING"},
                },
                "required": ["check", "status", "detail"],
            },
        },
        "red_flags": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "severity": {"type": "STRING", "enum": ["LOW", "MEDIUM", "HIGH"]},
                    "signal": {"type": "STRING"},
                    "evidence": {"type": "STRING"},
                },
                "required": ["severity", "signal", "evidence"],
            },
        },
        "next_steps": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": [
        "summary",
        "risk_score",
        "recommendation",
        "confidence",
        "extracted_fields",
        "photo_findings",
        "consistency_checks",
        "red_flags",
        "next_steps",
    ],
}

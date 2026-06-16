# Confidential Data Protection Proxy

A production-quality proxy service that sits in front of an LLM and prevents confidential information leakage.

---

## Architecture

```
Client
  │
  ▼
Proxy API  (FastAPI)
  │
  ▼
Content Extractor
  ├── TextExtractor       — plain text, source code
  ├── DocumentExtractor   — PDF (pdfplumber), DOCX (python-docx)
  └── ImageOCRExtractor   — pytesseract
  │
  ▼
Detection Pipeline
  ├── RegexDetector       — AWS keys, OpenAI keys, GitHub tokens, JWTs, private keys,
  │                         DB connection strings, Bearer tokens
  ├── KeywordDetector     — password, secret, token, api_key, …
  └── SLMDetector (stub)  — future local inference engine
  │
  ▼
Risk Aggregator           — Σ(finding.risk)
  │
  ▼
Policy Engine
  ├── risk ≥ 100  → BLOCK
  ├── risk ≥ 50   → REDACT
  └── risk < 50   → ALLOW
  │
  ▼
Redactor & Forwarder
  │
 LLM
  | 
  ▼
Audit Logger + Metrics
```

---

## Quick Start

### Docker (recommended)

```bash
docker compose up --build
```

The API is available at `http://localhost:8000`.

### Local

```bash
# System dependencies
apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils

# Python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Run
uvicorn app.main:app --reload
```

---

## API Reference

Interactive docs: `http://localhost:8000/docs`

### POST /scan/json

Scan a plain-text or code string.

**Request**
```json
{ "content": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE" }
```

**Response**
```json
{
  "request_id": "3f4e...",
  "decision": "BLOCK",
  "risk_score": 150,
  "findings": [
    { "detector": "regex", "type": "aws_access_key", "risk": 100, "match": "AKIAIO..." }
  ],
  "processed_content": "[CONTENT BLOCKED]"
}
```

---

### POST /scan

Scan an uploaded file (multipart form).

Supported extensions: `.txt .py .js .ts .java .go .env .json .yaml .yml .md .pdf .docx .png .jpg .jpeg .webp`

```bash
curl -X POST http://localhost:8000/scan \
  -F "file=@secret_config.env"
```

---

### GET /metrics

```json
{
  "total_requests": 42,
  "allowed_requests": 30,
  "blocked_requests": 8,
  "redacted_requests": 4,
  "files_scanned": 35,
  "images_scanned": 5,
  "documents_scanned": 2
}
```

### GET /health

```json
{ "status": "ok" }
```

---

## Policy Rules

| Risk Score | Decision |
|------------|----------|
| ≥ 100      | BLOCK    |
| 50 – 99    | REDACT   |
| < 50       | ALLOW    |

---

## Risk Scores by Finding Type

| Finding                  | Score |
|--------------------------|-------|
| AWS / OpenAI / GitHub key | 100  |
| Private key / DB string   | 100  |
| JWT / Bearer token        | 80   |
| Credential keyword (k=v)  | 50   |

---

---

## SLM Integration (Future)

`app/detectors/slm_detector.py` contains a no-op `SLMDetector` class.  Replace the body of `analyze()` with local model inference.  The `Scanner` class accepts it via constructor injection — no other code changes are required.

```python
class SLMDetector:
    async def analyze(self, text: str) -> dict:
        # TODO: load model, run inference
        return {"contains_confidential": False, "score": 0, "findings": []}
```

---

## Project Structure

```
app/
├── api/
│   ├── content_type_helper.py
│   ├── metrics.py
│   └── scan.py
├── detectors/
│   ├── keyword_detector.py
│   ├── regex_detector.py
│   └── slm_detector.py
├── engine/
│   ├── policy_engine.py
│   ├── risk_engine.py
│   └── scanner.py
├── extractors/
│   ├── document_extractor.py
│   ├── image_ocr.py
│   └── text_extractor.py
├── models/
│   └── schemas.py
├── services/
│   ├── audit_logger.py
│   ├── forwarder.py
│   ├── metrics_service.py
│   └── redactor.py
└── main.py
requirements.txt
pytest.ini
README.md
```

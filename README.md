# ATS — Explainable Resume-Job Matching Engine

A backend system that ranks job candidates against a job posting using
an **explainable, weighted scoring algorithm** — not a single opaque
"AI says 87% match" number. Every score comes with a breakdown a
recruiter (or an interviewer) can actually inspect and question.

## The problem this project solves

Most student "AI matching" projects call an LLM and return a percentage
with no way to explain it. That's not defensible in an interview and
it's not useful to a real recruiter, who needs to know *why* someone
ranked where they did. This project instead computes three separate,
interpretable signals and combines them with documented weights:

1. **Skill overlap** (50%) — Jaccard overlap between required skills and
   skills extracted from the resume.
2. **Semantic similarity** (30%) — TF-IDF + cosine similarity between the
   full job description and full resume text, catching relevant experience
   phrased differently than the skill list.
3. **Experience match** (20%) — candidate's years of experience vs. the
   job's minimum, capped so overqualification doesn't inflate the score.

Full reasoning and tradeoffs for each are documented inline in
`app/services/matching_service.py`.

**This is proven, not just claimed** — see `tests/test_matching.py`,
which asserts a clearly-stronger candidate scores higher than a clearly
weaker one, and checks each scoring component's edge cases individually.

## Architecture

```
Client → FastAPI routers → matching_service.py (scoring)
                          → resume_parser.py (PDF/DOCX → structured data)
                          → SQLAlchemy models → PostgreSQL
```

- **Resume parsing** (`resume_parser.py`): extracts raw text from PDF
  (pdfplumber) or DOCX (python-docx), then pulls out a skill list via
  vocabulary matching and years of experience via date-range parsing.
- **Scoring** (`matching_service.py`): the core algorithm described above.
- **Recruiter dashboard endpoint**: `GET /applications/job/{job_id}/ranked`
  returns every applicant sorted by score, each with full breakdown.

## Stack

FastAPI, PostgreSQL, SQLAlchemy 2.0, scikit-learn (TF-IDF + cosine
similarity), pdfplumber, python-docx, JWT auth, pytest.

## Running locally (MySQL via XAMPP)

1. Start MySQL from the XAMPP control panel.
2. Open phpMyAdmin (http://localhost/phpmyadmin) and create a database
   named `ats`.
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --reload --port 8001` (use a different port
   than the ticketing project if running both at once)
5. API docs at http://localhost:8001/docs

Default connection assumes XAMPP's default MySQL user (`root`, no
password, port 3306). Override with the `DATABASE_URL` env var if needed.

## Running the tests

```bash
pytest tests/test_matching.py -v
```

## What to highlight in interviews

1. **Why three separate signals instead of one black-box score** —
   explainability and the ability to debug/tune each independently.
2. **Why TF-IDF instead of a pretrained embedding model** — deliberate
   tradeoff: full explainability and zero external dependencies vs.
   potentially better semantic matching. You chose correctness and
   defensibility for a portfolio project; you can name sentence
   embeddings as the natural upgrade path.
3. **The resume parsing heuristics** — date-range regex for experience,
   word-boundary skill matching, and their documented limitations.
4. **Why weights are named constants** (`MatchWeights`) instead of magic
   numbers, and how you'd validate/tune them against real outcome data
   if this were a real product.

## Possible extensions (good "what would you do next" answers)

- Swap TF-IDF for sentence-transformers embeddings, add an A/B comparison
- Bias/fairness audit: check score distributions across resumes with
  different name/school signals removed vs. present
- Recruiter feedback loop: let recruiters mark "good match"/"bad match"
  on ranked candidates and use that to tune the weights over time
- Batch resume upload + async processing queue for high-volume recruiters

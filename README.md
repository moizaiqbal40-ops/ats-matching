<h1 align="center">📄 ATS — Explainable Resume-Job Matching Engine</h1>

<p align="center">
  An API-driven Applicant Tracking System that parses resumes, scores candidate-job fit, and ranks applicants using an interpretable multi-signal matching algorithm.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/scikit--learn-TF--IDF%20%2B%20Cosine-F7931E?logo=scikit-learn&logoColor=white" alt="scikit-learn" />
  <img src="https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white" alt="pytest" />
</p>

## Overview

Most student ATS projects reduce resume matching to an unexplained percentage. This project takes a different approach: **every candidate score is decomposed into signals that can be inspected, tested, and tuned.**

The system accepts job requirements and candidate resumes, extracts structured information from PDF/DOCX files, computes three independent matching signals, and exposes ranked candidates through a FastAPI backend and lightweight browser UI.

### Problem → Solution

| Problem | Engineering approach |
|---|---|
| A single opaque match percentage is hard to defend | Separate skill, semantic, and experience signals |
| Resumes are unstructured documents | PDF/DOCX text extraction + structured skill/experience parsing |
| Relevant experience may use different wording | TF-IDF + cosine similarity over full text |
| Recruiters need to know why candidates ranked | Return matched skills, missing skills, and component scores |
| Matching logic can become difficult to tune | Named `MatchWeights` configuration instead of magic numbers |

## Core Matching Algorithm

The final score is a weighted combination of three interpretable signals:

```text
Final Score
    │
    ├── 50% Skill Overlap
    │      └── Jaccard-style required-vs-candidate skill match
    │
    ├── 30% Semantic Similarity
    │      └── TF-IDF + cosine similarity on job/resume text
    │
    └── 20% Experience Match
           └── Candidate years ÷ required years, capped at 1.0
```

```text
final_score =
    0.5 × skill_overlap
  + 0.3 × semantic_similarity
  + 0.2 × experience_score
```

The weights are represented by a frozen `MatchWeights` dataclass, making the scoring policy explicit and easy to change.

### Why TF-IDF instead of an LLM?

This project deliberately uses TF-IDF rather than calling an external LLM or embedding API. It keeps the matching decision deterministic, fast, locally reproducible, and easier to explain in a technical interview.

A natural next step would be to compare this baseline against sentence embeddings and measure whether the additional semantic capability justifies the added complexity.

## Resume Parsing Pipeline

```text
PDF / DOCX Upload
       ↓
Text Extraction
       ↓
Skill Vocabulary Matching
       ↓
Date-Range / Experience Parsing
       ↓
Structured Resume Data
       ↓
Matching Engine
```

The parser currently handles:

- PDF extraction with `pdfplumber`
- DOCX extraction with `python-docx`
- Curated technical skill vocabulary
- Word-boundary matching to reduce false positives such as `java` inside `javascript`
- Date ranges such as `2019 - 2023` and `2019 - Present`
- Explicit phrases such as `3 years of experience`

The parser is intentionally a portfolio-scale heuristic rather than a production resume-understanding system. Complex layouts, overlapping employment periods, images/scanned PDFs, and richer experience semantics remain known limitations.

## Recruiter & Candidate Workflow

```text
Candidate                         Recruiter
   │                                  │
   ├── Sign up / Login                ├── Sign up as recruiter
   │                                  │
   ├── Upload PDF/DOCX resume         ├── Post job
   │                                  │
   ├── View parsed skills             ├── View applicants
   │                                  │
   └── Apply to job                   └── Inspect ranked candidates
                  \                  /
                   \                /
                    → Matching Engine
                           ↓
                  Explainable Score
```

The included browser UI supports authentication, job posting, resume upload/parsing, applications, job browsing, and recruiter-only ranked candidate views.

## Architecture

```text
Browser UI
    │
    ▼
FastAPI Application
    │
    ├── Auth Router ───────────── JWT authentication
    ├── Jobs Router ───────────── Job creation/listing
    ├── Resumes Router ────────── PDF/DOCX parsing
    └── Applications Router ───── Matching + ranking
                                  │
                                  ▼
                         matching_service.py
                         ├── Skill overlap
                         ├── TF-IDF similarity
                         └── Experience score
                                  │
                                  ▼
                         SQLAlchemy + MySQL/PostgreSQL
```

## API Highlights

| Endpoint | Purpose |
|---|---|
| `POST /auth/signup` | Create candidate or recruiter account |
| `POST /auth/login` | Authenticate and receive JWT |
| `GET /jobs` | Browse available jobs |
| `POST /jobs` | Create a recruiter job posting |
| `POST /resumes/upload` | Upload and parse PDF/DOCX resume |
| `GET /resumes/mine` | Retrieve the current user's resumes |
| `POST /applications` | Apply a resume to a job and calculate match score |
| `GET /applications/job/{job_id}/ranked` | Return ranked applicants with score breakdown |
| `GET /api` | API health/status response |

Interactive API documentation is available through FastAPI's generated `/docs` page when running locally.

## Project Structure

```text
ats-matching/
├── app/
│   ├── core/              # Database and application configuration
│   ├── models/            # SQLAlchemy data models
│   ├── routers/           # Auth, jobs, resumes, applications APIs
│   ├── services/
│   │   ├── matching_service.py
│   │   └── resume_parser.py
│   ├── schemas/           # Pydantic request/response models
│   ├── static/
│   │   └── index.html     # Lightweight browser UI
│   └── main.py             # FastAPI application entry point
├── tests/
│   └── test_matching.py   # Matching-engine unit tests
├── requirements.txt
└── README.md
```

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| API | FastAPI, Uvicorn |
| Database | MySQL / PostgreSQL via SQLAlchemy |
| ORM | SQLAlchemy 2.0 |
| Authentication | JWT + bcrypt |
| Resume parsing | pdfplumber, python-docx |
| Matching | scikit-learn, TF-IDF, cosine similarity |
| Validation | Pydantic |
| Testing | pytest |
| Frontend | HTML, CSS, Vanilla JavaScript |

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/moizaiqbal40-ops/ats-matching.git
cd ats-matching
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database

Create an `ats` database in MySQL and set `DATABASE_URL` if your local credentials differ from the project's default configuration.

Example:

```text
mysql+pymysql://root:password@localhost:3306/ats
```

### 5. Start the API

```bash
uvicorn app.main:app --reload --port 8001
```

Then open:

```text
http://localhost:8001/
http://localhost:8001/docs
```

## Testing

The matching engine is tested independently from the database and network layer:

```bash
pytest tests/test_matching.py -v
```

The test suite covers:

- Perfect and partial skill overlap
- Empty required-skill handling
- High and low TF-IDF similarity
- Experience scoring and upper-bound behavior
- End-to-end strong-vs-weak candidate ranking
- Default weight validation

This is important because the project's core value is the **matching logic**, not simply exposing an API around it.

## Engineering Decisions

### 1. Explainability over black-box scoring

The system returns the score components rather than hiding everything behind one prediction. A recruiter can see which skills matched, which were missing, and how semantic and experience signals contributed.

### 2. Deterministic baseline

TF-IDF and cosine similarity provide a transparent baseline with no external model download or API dependency.

### 3. Named scoring policy

`MatchWeights` makes the scoring policy explicit. In a production system, these weights should be validated against historical hiring outcomes rather than treated as universally optimal.

### 4. Parser limitations are documented

Resume parsing is intentionally heuristic. The implementation acknowledges that real-world resumes contain inconsistent formatting and overlapping roles that require substantially more sophisticated document understanding.

## Security & Production Considerations

The project includes JWT authentication, password hashing, role-aware recruiter/candidate workflows, and protected application/ranking operations.

For production deployment, the following would need additional hardening:

- Restrict CORS to trusted frontend origins
- Store secrets only in environment variables/secret managers
- Add upload size/type validation and malware scanning
- Improve token lifecycle and refresh/revocation strategy
- Add database migrations
- Replace heuristic resume parsing with a stronger document pipeline
- Add structured audit logging and rate limiting

## Current Limitations

- Skill extraction uses a curated vocabulary rather than a full taxonomy
- Experience parsing is heuristic and does not deduplicate overlapping roles
- TF-IDF is lexical rather than deep semantic matching
- The current UI is intentionally lightweight
- Matching weights are hand-selected and not learned from hiring outcomes
- Scanned/image-only resumes require OCR, which is not currently included

## Future Improvements

- Sentence-transformer embedding comparison against the TF-IDF baseline
- Larger, configurable skill taxonomy such as ESCO-style skill data
- OCR support for scanned resumes
- Better section-aware resume parsing
- Batch resume processing with background jobs
- Recruiter feedback loop for weight calibration
- Bias/fairness evaluation with protected or proxy signals excluded from scoring
- Database migrations and production observability
- More comprehensive API/integration tests
- Modern recruiter dashboard with visual score explanations

## What This Project Demonstrates

**Backend Engineering**
- REST API design with FastAPI
- Authentication and role-based workflows
- SQLAlchemy data modeling
- File upload and document processing

**Algorithms & Applied ML**
- Set-based skill matching
- TF-IDF vectorization
- Cosine similarity
- Weighted scoring systems
- Deterministic ranking

**Software Engineering**
- Separation of routers, services, models, and schemas
- Explicit configuration instead of magic numbers
- Unit testing of core business logic
- Documented tradeoffs and limitations

## Screenshots / Demo

<!-- Add 2–4 real screenshots here when available. Keep this section concise and focused on the recruiter workflow. -->

## Portfolio Positioning

This project is best presented as an **Explainable ATS / Resume-Job Matching Engine**, not simply an "AI resume matcher." Its strongest portfolio story is the combination of backend API engineering, document parsing, applied NLP, deterministic scoring, authentication, database integration, and tests around the core algorithm.

## License

MIT License.

## Author

**Moeeza Iqbal**  
Computer Science Student | Software Engineering

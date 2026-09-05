<div align="center">

# 📄 ATS Matching

### Explainable resume-to-job matching with a simple, transparent scoring engine.

</div>

## 💡 What It Is

A backend-focused ATS that parses resumes, compares them with job requirements, and ranks candidates using signals you can actually inspect. I built it to explore how a matching system can stay useful without becoming a black box.

## 🛠️ Tech Stack

- **Python** · FastAPI · Uvicorn
- **SQLAlchemy** · MySQL / PostgreSQL
- **TF-IDF + Cosine Similarity** · scikit-learn
- **PDF/DOCX parsing** · pdfplumber · python-docx
- **JWT + bcrypt** · Pydantic · pytest
- **HTML · CSS · Vanilla JavaScript**

## ⚙️ How It Works

```text
Resume + Job
     ↓
Parse & Extract Skills
     ↓
Skill Match + TF-IDF + Experience
     ↓
Weighted Score
     ↓
Rank Candidates
```

The score combines **skill overlap (50%)**, **text similarity (30%)**, and **experience (20%)**, with the individual signals returned so the result is explainable.

## 🚀 Run Locally

```bash
git clone https://github.com/moizaiqbal40-ops/ats-matching.git
cd ats-matching
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Then open `http://localhost:8001/docs` for the API docs.

## ✨ What I Learned / Challenges

The main challenge was turning messy resume text into a deterministic scoring system that is simple enough to test, explain, and improve.

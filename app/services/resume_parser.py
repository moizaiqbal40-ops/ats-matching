"""
Turns a raw resume file (PDF or DOCX) into structured data:
  - raw_text: full extracted text
  - skills: list of recognized skills found in the text
  - years_experience: estimated total years, parsed from date ranges

WHY THIS IS HARDER THAN IT LOOKS (worth mentioning in interviews):
Resumes have no consistent format. People write "5+ years", "Jan 2019 -
Present", "2019-2023", skills as a comma list or scattered through bullet
points, etc. A production ATS spends huge effort on this. Here we handle
the common cases robustly and document what's out of scope.
"""

import re
from datetime import datetime
from io import BytesIO

import pdfplumber
import docx


# A curated skill vocabulary. In production this would be a much larger,
# regularly-updated taxonomy (e.g. ESCO or a custom-maintained list) rather
# than a hardcoded set — documented here as a known simplification.
SKILL_VOCABULARY = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "postgresql", "mysql", "mongodb", "redis",
    "react", "angular", "vue", "next.js", "node.js", "django", "flask", "fastapi",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
    "machine learning", "deep learning", "nlp", "computer vision", "pandas",
    "numpy", "scikit-learn", "tensorflow", "pytorch",
    "git", "linux", "rest api", "graphql", "microservices", "system design",
    "html", "css", "tailwind", "figma", "agile", "scrum",
]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type. Use PDF or DOCX.")


def extract_skills(text: str) -> list[str]:
    """
    Matches against SKILL_VOCABULARY using word-boundary regex so
    'c++' or 'node.js' match correctly and 'java' doesn't false-positive
    match inside 'javascript'.
    """
    text_lower = text.lower()
    found = []
    for skill in SKILL_VOCABULARY:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


# Matches ranges like "Jan 2019 - Present", "2019 - 2023", "2019-Present"
DATE_RANGE_PATTERN = re.compile(
    r"(?:(?P<start_month>[A-Za-z]{3,9})\s+)?(?P<start_year>\d{4})\s*[-–—]\s*"
    r"(?:(?P<end_month>[A-Za-z]{3,9})\s+)?(?P<end_year>\d{4}|present|current)",
    re.IGNORECASE,
)


def extract_years_experience(text: str) -> int:
    """
    Sums non-overlapping date ranges found in the resume text as a proxy
    for total years of experience. This is a heuristic, not exact —
    documented limitation: doesn't dedupe overlapping concurrent roles.
    """
    total_months = 0
    now = datetime.utcnow()
    for match in DATE_RANGE_PATTERN.finditer(text):
        start_year = int(match.group("start_year"))
        end_raw = match.group("end_year").lower()
        end_year = now.year if end_raw in ("present", "current") else int(end_raw)
        years_diff = max(0, end_year - start_year)
        total_months += years_diff * 12

    # Fallback: explicit "X years of experience" mention
    explicit = re.search(r"(\d+)\+?\s*years?\s+(?:of\s+)?experience", text, re.IGNORECASE)
    explicit_years = int(explicit.group(1)) if explicit else 0

    computed_years = total_months // 12
    return max(computed_years, explicit_years)


def parse_resume(filename: str, file_bytes: bytes) -> dict:
    text = extract_text(filename, file_bytes)
    return {
        "raw_text": text,
        "skills": extract_skills(text),
        "years_experience": extract_years_experience(text),
    }

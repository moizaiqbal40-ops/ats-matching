"""
THE CORE OF THIS PROJECT.

Computes a match score between a resume and a job as a WEIGHTED,
EXPLAINABLE combination of three signals — never a single opaque
"AI says X%" number. Each signal is something you can defend
mathematically in an interview:

1. skill_overlap_score (weight 0.5)
   Jaccard-style overlap between the job's required_skills and the
   resume's extracted_skills. Direct, interpretable, and the signal
   recruiters trust most ("does this person actually have the skills").

2. semantic_similarity_score (weight 0.3)
   TF-IDF vectorization of the full job description and full resume
   text, compared with cosine similarity. This catches relevant
   experience described in different words than the skill list
   (e.g. resume says "built REST services" but job says "API design").
   We use TF-IDF instead of a pretrained embedding model deliberately:
   it's fully explainable (every dimension is a literal word, weighted
   by how distinctive it is via inverse-document-frequency), needs no
   external model download, and is fast enough to run per-request.
   A documented extension: swap in sentence embeddings (e.g.
   sentence-transformers) for better semantic matching at the cost of
   explainability and infra complexity — good to mention as a
   deliberate scope tradeoff in an interview.

3. experience_score (weight 0.2)
   How the candidate's years_experience compares to the job's
   min_years_experience, capped at 1.0 (more experience than required
   doesn't over-reward, avoiding bias toward over-qualification).

final_score = 0.5*skill_overlap + 0.3*semantic_similarity + 0.2*experience

Weights are configurable constants, not magic numbers buried in logic —
see MatchWeights below. In an interview: "these weights were a judgment
call; here's how I'd validate/tune them with real hiring outcome data
if I had it" is a strong thing to be able to say.
"""

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class MatchWeights:
    skill_overlap: float = 0.5
    semantic_similarity: float = 0.3
    experience: float = 0.2


DEFAULT_WEIGHTS = MatchWeights()


def compute_skill_overlap(required_skills: list[str], candidate_skills: list[str]) -> dict:
    required_set = {s.lower() for s in required_skills}
    candidate_set = {s.lower() for s in candidate_skills}

    if not required_set:
        # No required skills specified -> this signal shouldn't penalize anyone.
        return {"score": 1.0, "matched": [], "missing": []}

    matched = sorted(required_set & candidate_set)
    missing = sorted(required_set - candidate_set)
    score = len(matched) / len(required_set)

    return {"score": score, "matched": matched, "missing": missing}


def compute_semantic_similarity(job_description: str, resume_text: str) -> float:
    """
    Fits a TF-IDF vectorizer on just these two documents and returns
    cosine similarity between them, in [0, 1].
    """
    if not job_description.strip() or not resume_text.strip():
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
    except ValueError:
        # Happens if both docs are entirely stopwords/empty after cleaning.
        return 0.0

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return float(max(0.0, min(1.0, similarity)))


def compute_experience_score(min_years_required: int, candidate_years: int) -> float:
    if min_years_required <= 0:
        return 1.0
    return float(max(0.0, min(1.0, candidate_years / min_years_required)))


def score_application(
    job_description: str,
    required_skills: list[str],
    min_years_required: int,
    resume_text: str,
    candidate_skills: list[str],
    candidate_years: int,
    weights: MatchWeights = DEFAULT_WEIGHTS,
) -> dict:
    skill_result = compute_skill_overlap(required_skills, candidate_skills)
    semantic_score = compute_semantic_similarity(job_description, resume_text)
    experience_score = compute_experience_score(min_years_required, candidate_years)

    final_score = (
        weights.skill_overlap * skill_result["score"]
        + weights.semantic_similarity * semantic_score
        + weights.experience * experience_score
    )

    return {
        "skill_overlap_score": skill_result["score"],
        "semantic_similarity_score": semantic_score,
        "experience_score": experience_score,
        "final_score": round(final_score, 4),
        "matched_skills": skill_result["matched"],
        "missing_skills": skill_result["missing"],
    }

"""
Tests for the core matching algorithm. These don't need a database or
network — they test matching_service.py in isolation, which is exactly
what you want to demo live: "here's proof my scoring logic does what
I claim it does."
"""

from app.services.matching_service import (
    compute_skill_overlap,
    compute_semantic_similarity,
    compute_experience_score,
    score_application,
    MatchWeights,
)


def test_skill_overlap_perfect_match():
    result = compute_skill_overlap(
        required_skills=["python", "sql", "react"],
        candidate_skills=["python", "sql", "react", "docker"],
    )
    assert result["score"] == 1.0
    assert result["matched"] == ["python", "react", "sql"]
    assert result["missing"] == []


def test_skill_overlap_partial_match():
    result = compute_skill_overlap(
        required_skills=["python", "sql", "react", "aws"],
        candidate_skills=["python", "sql"],
    )
    assert result["score"] == 0.5
    assert set(result["missing"]) == {"aws", "react"}


def test_skill_overlap_no_required_skills_does_not_penalize():
    result = compute_skill_overlap(required_skills=[], candidate_skills=["python"])
    assert result["score"] == 1.0


def test_semantic_similarity_identical_text_is_high():
    text = "Experienced backend engineer with Python and PostgreSQL background"
    score = compute_semantic_similarity(text, text)
    assert score > 0.99


def test_semantic_similarity_unrelated_text_is_low():
    job = "Looking for a backend engineer skilled in Python and PostgreSQL"
    resume = "Professional chef with ten years of experience in French cuisine"
    score = compute_semantic_similarity(job, resume)
    assert score < 0.3


def test_experience_score_meets_requirement():
    assert compute_experience_score(min_years_required=3, candidate_years=3) == 1.0


def test_experience_score_exceeds_requirement_caps_at_one():
    # More experience than required should NOT score above 1.0 —
    # avoids biasing toward "most experienced" over "meets the bar".
    assert compute_experience_score(min_years_required=3, candidate_years=10) == 1.0


def test_experience_score_below_requirement_is_proportional():
    assert compute_experience_score(min_years_required=4, candidate_years=2) == 0.5


def test_experience_score_no_requirement_is_full_score():
    assert compute_experience_score(min_years_required=0, candidate_years=0) == 1.0


def test_stronger_candidate_ranks_above_weaker_candidate():
    """
    The end-to-end sanity check: given a fixed job, a candidate who
    matches on skills, description language, AND experience should
    score strictly higher than one who matches on none of it.
    """
    job_description = "Backend engineer role focused on Python, SQL, and API design"
    required_skills = ["python", "sql", "rest api"]

    strong = score_application(
        job_description=job_description,
        required_skills=required_skills,
        min_years_required=3,
        resume_text="Backend engineer with 5 years building Python REST APIs and SQL databases",
        candidate_skills=["python", "sql", "rest api"],
        candidate_years=5,
    )

    weak = score_application(
        job_description=job_description,
        required_skills=required_skills,
        min_years_required=3,
        resume_text="Graphic designer specializing in branding and illustration",
        candidate_skills=["figma"],
        candidate_years=1,
    )

    assert strong["final_score"] > weak["final_score"]
    assert strong["final_score"] > 0.75
    assert weak["final_score"] < 0.3


def test_weights_sum_to_one_by_default():
    w = MatchWeights()
    assert round(w.skill_overlap + w.semantic_similarity + w.experience, 5) == 1.0

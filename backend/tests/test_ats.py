import pytest

from app.ats import score_resume


def test_score_is_deterministic_keyword_coverage_with_evidence():
    result = score_resume(
        "Backend Engineer\nPython, FastAPI, PostgreSQL\nBuilt accessibility APIs.",
        "We need Python, FastAPI, React, PostgreSQL and accessibility.",
    )

    assert result.overall_score == 80.0
    assert result.matched_terms == ["python", "fastapi", "postgresql", "accessibility"]
    assert result.missing_terms == ["react"]
    assert result.breakdown["method"] == "keyword_coverage"
    python_item = next(item for item in result.evidence if item.requirement == "python")
    assert python_item.resume_evidence
    assert python_item.matched
    assert "AI inference" in python_item.explanation
    assert "python" in python_item.explanation.lower()
    react_item = next(item for item in result.evidence if item.requirement == "react")
    assert not react_item.matched
    assert react_item.explanation == ""


def test_score_does_not_invent_terms_or_treat_substrings_as_matches():
    result = score_resume("Java developer", "JavaScript and SQL")

    assert result.overall_score == 0
    assert result.matched_terms == []
    assert result.missing_terms == ["javascript", "sql"]


def test_score_rejects_an_unscorable_job_description():
    with pytest.raises(ValueError, match="enough scorable terms"):
        score_resume("Python", "and the with")


def test_matched_inference_when_evidence_line_exists():
    result = score_resume(
        "Built REST services with FastAPI and Docker.",
        "Looking for FastAPI experience.",
    )
    item = next(item for item in result.evidence if item.requirement == "fastapi")
    assert item.matched
    assert item.resume_evidence
    assert "fastapi" in item.explanation.lower() or "FastAPI" in item.explanation

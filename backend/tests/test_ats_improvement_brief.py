from app.agents.ats.improvement_brief import _deterministic_brief


def test_deterministic_brief_lists_only_missing_terms():
    brief = _deterministic_brief(
        score=60,
        missing=["react", "kubernetes"],
        matched_count=3,
        total=5,
        role_title="Backend Engineer",
    )
    text = brief["overall_inference"].lower()
    assert "react" in text
    assert "kubernetes" in text
    assert "60" in brief["overall_inference"] or "60" in text
    assert brief["focus_areas"] == ["react", "kubernetes"]
    assert "hiring prediction" in text


def test_deterministic_brief_no_missing():
    brief = _deterministic_brief(score=100, missing=[], matched_count=5, total=5, role_title=None)
    assert "no scored jd keywords were missing" in brief["overall_inference"].lower()
    assert brief["focus_areas"] == []

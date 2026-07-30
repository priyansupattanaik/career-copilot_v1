from app.agents.interview.question_generator import _template_questions


def test_template_questions_respect_count_and_mode():
    rows = _template_questions("technical", 4, "Backend Engineer")
    assert len(rows) == 4
    assert all(r["question"] for r in rows)
    assert any("API" in r["question"] or "technical" in (r["question_type"] or "") for r in rows)


def test_template_questions_caps_at_requested():
    rows = _template_questions("behavioural", 2, None)
    assert len(rows) == 2

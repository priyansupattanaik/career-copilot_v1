import re

from app.agents.profile_fill.pipeline import _filter_draft_by_evidence, merge_profile_drafts


def test_filter_drops_invented_company():
    draft = {
        "profile": {"full_name": "Jane Doe", "phone": None, "location": None, "current_role": "Engineer", "headline": None, "bio": None},
        "skills": [{"name": "Python", "selected": True}],
        "experiences": [
            {"company_name": "Totally Fake Corp XYZ", "role_title": "CEO", "selected": True},
            {"company_name": "Acme Corp", "role_title": "Engineer", "selected": True},
        ],
        "education": [],
        "projects": [],
        "certifications": [],
        "languages": [],
        "links": [],
        "meta": {"warnings": []},
    }
    resume = "Jane Doe\nSoftware Engineer at Acme Corp\nPython FastAPI\n"
    filtered = _filter_draft_by_evidence(draft, resume)
    companies = [e["company_name"] for e in filtered["experiences"]]
    assert "Acme Corp" in companies
    assert "Totally Fake Corp XYZ" not in companies
    assert any(s["name"] == "Python" for s in filtered["skills"])


def test_merge_prefers_ai_experiences_and_keeps_base_skills():
    base = {
        "profile": {"full_name": "Jane", "phone": "+91 99999 99999", "location": None, "current_role": None, "headline": None, "bio": None, "years_experience": None, "career_level": None, "career_goal": None},
        "skills": [{"name": "Docker", "selected": True}],
        "experiences": [{"company_name": "Beta", "role_title": "Intern", "selected": True}],
        "education": [],
        "projects": [],
        "certifications": [],
        "languages": [],
        "links": [{"url": "https://github.com/jane", "link_type": "github", "selected": True}],
        "meta": {"warnings": [], "email_detected": "jane@example.com"},
    }
    ai = {
        "profile": {"full_name": "Jane Doe", "phone": None, "location": "Pune", "current_role": "Engineer", "headline": "Backend engineer", "bio": "Built APIs", "years_experience": 2, "career_level": "junior", "career_goal": None, "selected": True},
        "skills": [{"name": "Python", "selected": True}],
        "experiences": [{"company_name": "Acme Corp", "role_title": "Software Engineer", "selected": True, "display_order": 0}],
        "education": [],
        "projects": [],
        "certifications": [],
        "languages": [],
        "links": [],
        "meta": {"warnings": [], "ai_used": True},
    }
    resume = "Jane Doe Pune Software Engineer Acme Corp Built APIs with Python Beta Intern Docker github.com/jane"
    merged = merge_profile_drafts(base, ai, plain_text=resume)
    assert merged["profile"]["full_name"] == "Jane Doe"
    # Phone kept from deterministic and normalized (spaces stripped)
    assert merged["profile"]["phone"] and "9999999999" in re.sub(r"\D", "", merged["profile"]["phone"])
    assert merged["meta"]["ai_used"] is True
    skill_names = {s["name"] for s in merged["skills"]}
    assert "Python" in skill_names
    assert "Docker" in skill_names

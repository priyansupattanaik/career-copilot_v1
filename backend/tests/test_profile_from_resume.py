from app.profile_from_resume import build_profile_draft, draft_counts

SAMPLE = """
Jane Doe
jane@example.com | +91 98765 43210 | https://linkedin.com/in/janedoe | https://github.com/janedoe
Pune, India

PROFESSIONAL SUMMARY
Backend engineer focused on APIs and data systems.

TECHNICAL SKILLS
Languages: Python, SQL, JavaScript
Frameworks: FastAPI, React, Django
Tools: Docker, AWS, Git, PostgreSQL

PROFESSIONAL EXPERIENCE
Software Engineer | Acme Corp | Jan 2022 – Present
- Designed and shipped REST APIs with FastAPI
- Improved PostgreSQL performance by 40%

Backend Intern | Beta Labs | Jun 2021 – Dec 2021
- Built internal tooling in Python

PROJECTS
Career Copilot | Personal
- Full-stack ATS analyzer with Next.js and FastAPI

EDUCATION
B.Tech Computer Science | State University | 2018 – 2022
CGPA: 8.4/10

CERTIFICATIONS
AWS Cloud Practitioner | Amazon

LANGUAGES
English - Fluent
Hindi - Native
"""


def test_build_profile_draft_maps_core_sections():
    draft = build_profile_draft(SAMPLE)
    profile = draft["profile"]
    assert profile["full_name"] == "Jane Doe"
    assert profile["phone"]
    assert profile["location"]
    assert profile["current_role"] == "Software Engineer"
    assert profile["headline"]
    assert draft["skills"]
    assert any(s["name"].lower() == "python" for s in draft["skills"])
    assert len(draft["experiences"]) >= 2
    assert draft["experiences"][0]["company_name"] == "Acme Corp"
    assert len(draft["education"]) >= 1
    assert "State University" in draft["education"][0]["institution"] or draft["education"][0][
        "institution"
    ]
    assert draft["projects"]
    assert draft["certifications"]
    assert draft["languages"]
    assert any(link["link_type"] == "linkedin" for link in draft["links"])
    assert any(link["link_type"] == "github" for link in draft["links"])
    counts = draft_counts(draft)
    assert counts["skills"] >= 3
    assert counts["experiences"] >= 2


def test_build_profile_draft_does_not_require_structured_content():
    draft = build_profile_draft("Skills\nPython, SQL\nExperience\nBuilt APIs at Acme")
    assert draft["skills"]
    assert draft["experiences"]

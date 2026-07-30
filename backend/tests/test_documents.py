from app.documents import (
    extract_sections,
    extract_skill_candidates,
    infer_job_metadata,
    infer_resume_title,
    match_section_heading,
)

REALISTIC_RESUME = """
Jane Doe
jane@example.com | +91 98765 43210 | LinkedIn

PROFESSIONAL SUMMARY
Results-driven software engineer with 3+ years building APIs and data pipelines.

TECHNICAL SKILLS
Languages: Python, SQL, JavaScript
Frameworks: FastAPI, React, Django
Tools: Docker, AWS, Git, PostgreSQL

PROFESSIONAL EXPERIENCE
Software Engineer | Acme Corp | Jan 2022 – Present
- Designed and shipped REST APIs with FastAPI serving 50k daily users
- Improved query performance by 40% using PostgreSQL indexing
- Collaborated with product to deliver sprint goals on time

Backend Intern | Beta Labs | Jun 2021 – Dec 2021
- Built internal tooling in Python for data validation
- Wrote unit tests and documentation for microservices

PROJECTS
Career Copilot | Personal
- Full-stack ATS analyzer with Next.js and FastAPI
- Resume parsing and keyword coverage scoring

Inventory Tracker | Academic
- Django app for warehouse stock with barcode scanning

EDUCATION
B.Tech Computer Science | State University | 2018 – 2022
CGPA: 8.4/10

CERTIFICATIONS
AWS Cloud Practitioner | 2023
"""


def test_infer_resume_title_from_filename():
    assert infer_resume_title("Priya_Resume_v2.pdf") == "Priya Resume v2"
    assert infer_resume_title(None) == "Resume"


def test_infer_job_metadata_from_labels():
    text = """
    Job Title: Senior Backend Engineer
    Company: Acme Labs

    We need Python, FastAPI, and SQL experience.
    """
    meta = infer_job_metadata(text)
    assert meta["role_title"] == "Senior Backend Engineer"
    assert meta["company"] == "Acme Labs"
    assert "Senior Backend Engineer" in (meta["title"] or "")
    assert meta["confidence"] == "high"


def test_infer_job_metadata_from_role_hint_line():
    text = """
    Data Analyst
    Location: Pune

    Requirements include SQL, Python, and dashboards for stakeholders.
    """
    meta = infer_job_metadata(text)
    assert meta["role_title"] == "Data Analyst"
    assert meta["title"] == "Data Analyst"


def test_extract_skill_candidates():
    skills = extract_skill_candidates("Built APIs with Python, FastAPI, SQL and Docker on AWS.")
    assert "Python" in skills
    assert "SQL" in skills
    assert "Docker" in skills
    assert "AWS" in skills


def test_match_section_heading_aliases():
    assert match_section_heading("PROFESSIONAL EXPERIENCE") == "experience"
    assert match_section_heading("Technical Skills:") == "skills"
    assert match_section_heading("Personal Projects") == "projects"
    assert match_section_heading("Work History") == "experience"
    assert match_section_heading("Professional Summary") == "summary"
    # Sentences must not become headings
    assert match_section_heading("I have strong experience with Python and APIs.") is None
    assert match_section_heading("Built projects using FastAPI and React") is None


def test_extract_sections_separates_experience_projects_and_skills():
    result = extract_sections(REALISTIC_RESUME)
    sections = result["sections"]

    assert "summary" in sections
    assert "skills" in sections
    assert "experience" in sections
    assert "projects" in sections
    assert "education" in sections
    assert "certifications" in sections

    # Experience must not bleed into skills
    skills_blob = "\n".join(sections["skills"]).lower()
    assert "software engineer" not in skills_blob
    assert "acme" not in skills_blob
    assert "python" in skills_blob or any("python" in line.lower() for line in sections["skills"])

    # Two distinct experience entries
    assert len(sections["experience"]) == 2
    assert "Acme Corp" in sections["experience"][0]
    assert "FastAPI" in sections["experience"][0]
    assert "Beta Labs" in sections["experience"][1]
    assert "Python" in sections["experience"][1]

    # Projects stay out of experience
    experience_blob = "\n".join(sections["experience"]).lower()
    assert "career copilot" not in experience_blob
    assert "inventory tracker" not in experience_blob

    assert len(sections["projects"]) == 2
    assert "Career Copilot" in sections["projects"][0]
    assert "Inventory Tracker" in sections["projects"][1]

    # Contact captured from header
    contact = "\n".join(sections.get("contact") or [])
    assert "jane@example.com" in contact.lower() or "jane@example.com" in "\n".join(
        result["unclassified_blocks"]
    ).lower()


def test_extract_sections_simple_fixture_style_resume():
    text = "Skills\nPython, FastAPI, SQL\nExperience\nBuilt APIs\nProjects\nCareer Copilot app"
    sections = extract_sections(text)["sections"]
    assert sections["skills"]
    assert any("python" in line.lower() for line in sections["skills"])
    assert sections["experience"] == ["Built APIs"]
    assert any("career copilot" in line.lower() for line in sections["projects"])


def test_extract_sections_splits_entries_without_blank_lines():
    """PDF extractors often drop blank lines between jobs; entries must still split."""
    text = """
PROFESSIONAL EXPERIENCE
Software Engineer | Acme Corp | Jan 2022 - Present
- Designed REST APIs with FastAPI
- Improved PostgreSQL performance
Backend Intern | Beta Labs | Jun 2021 - Dec 2021
- Built internal tooling in Python
PROJECTS
Career Copilot | Personal
- Full-stack ATS analyzer
Inventory Tracker | Academic
- Django warehouse app
"""
    sections = extract_sections(text)["sections"]
    assert len(sections["experience"]) == 2
    assert "Acme Corp" in sections["experience"][0]
    assert "Beta Labs" in sections["experience"][1]
    assert "Career Copilot" not in sections["experience"][0]
    assert len(sections["projects"]) == 2
    assert "Career Copilot" in sections["projects"][0]
    assert "Inventory Tracker" in sections["projects"][1]

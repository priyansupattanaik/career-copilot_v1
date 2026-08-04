"""Tests for ATS-grounded YouTube learning crew (no invented video IDs)."""

from __future__ import annotations

import asyncio

from app.features.learning.agents.crew.tools import (
    tool_extract_ats_gaps,
    tool_validate_and_materialize,
)
from app.features.learning.youtube_catalog import (
    build_grounded_resource,
    is_allowed_youtube_url,
    youtube_search_url,
)


def test_extract_only_missing_or_partial_gaps():
    evidence = [
        {"requirement_text": "Docker", "match_status": "not_found"},
        {"requirement_text": "Python", "match_status": "partial_match"},
        {"requirement_text": "SQL", "match_status": "matched"},
        {"requirement_text": "Docker", "match_status": "not_found"},  # duplicate
    ]
    out = tool_extract_ats_gaps({"evidence_rows": evidence, "source_analysis_id": "a1"})
    assert out["allowed_gaps"] == ["Docker", "Python"]
    assert out["gap_count"] == 2


def test_validator_rejects_invented_gap_and_fills_missing():
    ctx = {
        "allowed_gaps": ["Docker", "Kubernetes"],
        "planner_provider": "test",
        "plan": {
            "recommendations": [
                {
                    "skill_gap": "Docker",
                    "title": "Learn Docker",
                    "objective": "Study Docker with free tutorials for containers.",
                    "youtube_search_query": "Docker tutorial freecodecamp",
                    "estimated_minutes": 45,
                    "difficulty": "foundational",
                },
                {
                    "skill_gap": "Quantum Telepathy",
                    "title": "Hallucinated",
                    "objective": "This skill was not in the ATS analysis and must be dropped.",
                    "youtube_search_query": "quantum telepathy course",
                    "estimated_minutes": 30,
                },
            ]
        },
    }
    out = tool_validate_and_materialize(ctx)
    assert out["accepted_count"] == 2
    requirements = {item["metadata"]["requirement"] for item in out["items"]}
    assert requirements == {"Docker", "Kubernetes"}
    assert any("Quantum Telepathy" in r or "gap_not_in_ats_evidence" in r for r in out["rejected"])
    for item in out["items"]:
        url = item["resources"][0]["url"]
        assert is_allowed_youtube_url(url)
        assert "youtube.com" in url


def test_youtube_urls_are_search_or_allowlist_only():
    resource = build_grounded_resource(gap="Rust", search_query="Rust tutorial freecodecamp")
    assert resource["resource_type"] in {"youtube_search", "youtube_video"}
    assert is_allowed_youtube_url(resource["url"])
    policy = resource["metadata"].get("video_id_policy") or ""
    assert "search_only" in policy or "allowlist" in policy
    # Search URLs must not look like random watch IDs for unknown skills
    if resource["resource_type"] == "youtube_search":
        assert "/results" in resource["url"]
        assert "/watch" not in resource["url"]


def test_search_url_encoding():
    url = youtube_search_url("C++ basics for beginners")
    assert url.startswith("https://www.youtube.com/results?search_query=")
    assert is_allowed_youtube_url(url)


def test_crew_run_end_to_end_without_llm():
    from app.features.learning.agents.crew.orchestrator import run_learning_youtube_crew

    class DummySettings:
        groq_configured = False
        nvidia_configured = False

    evidence = [
        {"requirement_text": "Docker", "match_status": "not_found"},
        {"requirement_text": "Git", "match_status": "not_found"},
    ]
    items, audit = asyncio.run(
        run_learning_youtube_crew(
            DummySettings(),  # type: ignore[arg-type]
            evidence_rows=evidence,
            source_analysis_id="analysis-1",
            role_title="Backend Engineer",
        )
    )
    assert audit.success is True
    assert len(items) == 2
    assert all(item["resources"] for item in items)
    assert all(is_allowed_youtube_url(item["resources"][0]["url"]) for item in items)

"""
AI agents package for Career Copilot.

Layout:
  agents/
    llm/              NVIDIA + Groq provider clients (separate; no cross-fallback)
    prompts/          System prompts (versioned text files)
    profile_fill/     Resume → profile (NVIDIA when configured)
    interview/        Mock interview questions (Groq when configured)

Public entry points:
  from app.agents.llm import NvidiaClient, GroqClient
  from app.agents.profile_fill import build_profile_draft_enriched
  from app.agents.interview import generate_interview_questions
"""

from app.agents.interview import generate_interview_questions
from app.agents.llm import GroqClient, NvidiaClient
from app.agents.profile_fill import (
    build_profile_draft,
    build_profile_draft_enriched,
    draft_counts,
    profile_draft_response_payload,
)

__all__ = [
    "GroqClient",
    "NvidiaClient",
    "build_profile_draft",
    "build_profile_draft_enriched",
    "draft_counts",
    "generate_interview_questions",
    "profile_draft_response_payload",
]

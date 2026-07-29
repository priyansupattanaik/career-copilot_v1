from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class ProfilePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = Field(default=None, max_length=120)
    headline: str | None = Field(default=None, max_length=240)
    bio: str | None = Field(default=None, max_length=4000)
    phone: str | None = Field(default=None, max_length=40)
    location: str | None = Field(default=None, max_length=160)
    current_role: str | None = Field(default=None, max_length=160)
    years_experience: float | None = Field(default=None, ge=0, le=80)
    career_level: str | None = Field(default=None, max_length=80)
    career_goal: str | None = Field(default=None, max_length=2000)
    onboarding_step: int | None = Field(default=None, ge=1, le=6)
    onboarding_completed: bool | None = None


class PreferencesUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_roles: list[str] = []
    preferred_industries: list[str] = []
    preferred_locations: list[str] = []
    work_modes: list[str] = []
    employment_types: list[str] = []
    notice_period_days: int | None = Field(default=None, ge=0)
    willing_to_relocate: bool = False
    work_authorization: str | None = Field(default=None, max_length=160)
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)
    salary_currency: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")

    @model_validator(mode="after")
    def salary_order(self) -> "PreferencesUpdate":
        if self.salary_min is not None and self.salary_max is not None and self.salary_min > self.salary_max:
            raise ValueError("salary_min cannot exceed salary_max")
        return self


class JobDescriptionTextCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    company: str | None = Field(default=None, max_length=200)
    role_title: str | None = Field(default=None, max_length=200)
    raw_text: str = Field(min_length=20, max_length=200_000)


class ExtractionPatch(BaseModel):
    structured_content: dict[str, Any]


class InterviewCreate(BaseModel):
    mode: Literal[
        "resume", "resume_and_jd", "role", "topic", "company", "behavioural", "technical", "hr", "mixed"
    ]
    resume_version_id: UUID | None = None
    job_description_id: UUID | None = None
    target_role: str | None = None
    target_company: str | None = None
    topic: str | None = None
    difficulty: str | None = None
    question_count: int = Field(default=5, ge=1, le=20)
    duration_minutes: int = Field(default=20, ge=5, le=180)
    camera_enabled: bool = False
    microphone_enabled: bool = False
    recording_consent: bool = False


class InterviewResponseCreate(BaseModel):
    question_id: UUID
    typed_response: str | None = Field(default=None, max_length=20_000)
    transcript: str | None = Field(default=None, max_length=50_000)
    duration_seconds: int | None = Field(default=None, ge=0)


class LearningPathCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    source_type: Literal["candidate_selected"] = "candidate_selected"


class SavedJobPatch(BaseModel):
    status: Literal["saved", "applied", "interviewing", "offer", "rejected", "withdrawn"] = "saved"
    notes: str | None = Field(default=None, max_length=4000)


class NotificationSettings(BaseModel):
    job_alerts: bool = False
    learning_reminders: bool = True
    interview_reminders: bool = True
    product_updates: bool = False
    email_frequency: Literal["never", "daily", "weekly"] = "weekly"


class PrivacySettings(BaseModel):
    camera_permission: Literal["ask", "allowed", "disabled"] = "ask"
    microphone_permission: Literal["ask", "allowed", "disabled"] = "ask"
    recording_retention_days: int = Field(default=0, ge=0, le=365)
    resume_processing_consent: bool = False
    job_recommendation_consent: bool = False
    profile_visibility: Literal["private", "limited"] = "private"


class LinkInput(BaseModel):
    link_type: Literal["linkedin", "github", "portfolio", "website", "other"]
    label: str | None = None
    url: HttpUrl
    display_order: int = Field(default=0, ge=0)

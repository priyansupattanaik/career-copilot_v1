from fastapi import APIRouter, Depends

from app.ats_scoring.schemas import ScoreRequest, ScoreResult
from app.ats_scoring.service import score_resume_jd
from app.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/ats", tags=["ats-scoring"])


@router.post("/score", response_model=ScoreResult)
async def score(
    payload: ScoreRequest,
    _: CurrentUser = Depends(get_current_user),
) -> ScoreResult:
    return await score_resume_jd(payload.resume_text, payload.jd_text)

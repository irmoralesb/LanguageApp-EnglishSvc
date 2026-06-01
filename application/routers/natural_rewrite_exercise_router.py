from fastapi import APIRouter, Depends

from application.routers.dependency_utils import (
    NaturalRewriteExerciseSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.natural_rewrite_exercise_schema import (
    NaturalRewriteExerciseRequest,
    NaturalRewriteExercisePromptResponse,
    NaturalRewriteAnswerRequest,
    NaturalRewriteEvaluationResponse,
    NaturalRewriteHistoryResponse,
)

router = APIRouter(
    prefix="/api/v1/natural-rewrite/exercises",
    tags=["Natural Rewrite Exercises"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.post("/generate", response_model=NaturalRewriteExercisePromptResponse)
async def generate_exercise(
    payload: NaturalRewriteExerciseRequest,
    svc: NaturalRewriteExerciseSvcDep,
    current_user: CurrentUserDep,
):
    prompt, prompt_token = await svc.generate(
        user_id=current_user.user_id,
        target_language_code=payload.target_language_code,
    )
    return NaturalRewriteExercisePromptResponse(
        target_language_code=prompt.target_language_code,
        scenario_native=prompt.scenario_native,
        stiff_sentence=prompt.stiff_sentence,
        context_note=prompt.context_note,
        prompt_token=prompt_token,
    )


@router.post("/evaluate", response_model=NaturalRewriteEvaluationResponse)
async def evaluate_answer(
    payload: NaturalRewriteAnswerRequest,
    svc: NaturalRewriteExerciseSvcDep,
    current_user: CurrentUserDep,
):
    evaluation = await svc.evaluate(
        user_id=current_user.user_id,
        prompt_token=payload.prompt_token,
        user_answer=payload.user_answer,
    )
    return NaturalRewriteEvaluationResponse(
        is_correct=evaluation.is_correct,
        feedback=evaluation.feedback,
        model_answer=evaluation.model_answer,
    )


@router.get("/history", response_model=list[NaturalRewriteHistoryResponse])
async def get_history(
    svc: NaturalRewriteExerciseSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 50,
):
    records = await svc.get_history(current_user.user_id, skip=skip, limit=limit)
    return [
        NaturalRewriteHistoryResponse(
            id=r.id,  # type: ignore[arg-type]
            target_language_code=r.target_language_code,
            scenario_native=r.scenario_native,
            stiff_sentence=r.stiff_sentence,
            user_answer=r.user_answer,
            is_correct=r.is_correct,
            feedback=r.feedback,
            model_answer=r.model_answer,
            created_at=r.created_at,  # type: ignore[arg-type]
        )
        for r in records
    ]

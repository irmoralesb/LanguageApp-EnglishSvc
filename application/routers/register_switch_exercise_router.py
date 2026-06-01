from fastapi import APIRouter, Depends

from application.routers.dependency_utils import (
    RegisterSwitchExerciseSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.register_switch_exercise_schema import (
    RegisterSwitchExerciseRequest,
    RegisterSwitchExercisePromptResponse,
    RegisterSwitchAnswerRequest,
    RegisterSwitchEvaluationResponse,
    RegisterSwitchHistoryResponse,
)

router = APIRouter(
    prefix="/api/v1/register-switch/exercises",
    tags=["Register Switch Exercises"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.post("/generate", response_model=RegisterSwitchExercisePromptResponse)
async def generate_exercise(
    payload: RegisterSwitchExerciseRequest,
    svc: RegisterSwitchExerciseSvcDep,
    current_user: CurrentUserDep,
):
    prompt, prompt_token = await svc.generate(
        user_id=current_user.user_id,
        target_language_code=payload.target_language_code,
        target_register=payload.target_register,
        slang_level=payload.slang_level,
    )
    return RegisterSwitchExercisePromptResponse(
        target_language_code=prompt.target_language_code,
        scenario_native=prompt.scenario_native,
        source_sentence=prompt.source_sentence,
        source_register=prompt.source_register,
        target_register=prompt.target_register,
        slang_level=prompt.slang_level,
        prompt_token=prompt_token,
    )


@router.post("/evaluate", response_model=RegisterSwitchEvaluationResponse)
async def evaluate_answer(
    payload: RegisterSwitchAnswerRequest,
    svc: RegisterSwitchExerciseSvcDep,
    current_user: CurrentUserDep,
):
    evaluation = await svc.evaluate(
        user_id=current_user.user_id,
        prompt_token=payload.prompt_token,
        user_answer=payload.user_answer,
    )
    return RegisterSwitchEvaluationResponse(
        is_correct=evaluation.is_correct,
        feedback=evaluation.feedback,
        model_answer=evaluation.model_answer,
    )


@router.get("/history", response_model=list[RegisterSwitchHistoryResponse])
async def get_history(
    svc: RegisterSwitchExerciseSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 50,
):
    records = await svc.get_history(current_user.user_id, skip=skip, limit=limit)
    return [
        RegisterSwitchHistoryResponse(
            id=r.id,  # type: ignore[arg-type]
            target_language_code=r.target_language_code,
            scenario_native=r.scenario_native,
            source_sentence=r.source_sentence,
            source_register=r.source_register,
            target_register=r.target_register,
            slang_level=r.slang_level,
            user_answer=r.user_answer,
            is_correct=r.is_correct,
            feedback=r.feedback,
            model_answer=r.model_answer,
            created_at=r.created_at,  # type: ignore[arg-type]
        )
        for r in records
    ]

from fastapi import APIRouter, Depends

from application.routers.dependency_utils import (
    PrepositionChoiceExerciseSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.preposition_choice_exercise_schema import (
    PrepositionChoiceExerciseRequest,
    PrepositionChoiceExercisePromptResponse,
    PrepositionChoiceAnswerRequest,
    PrepositionChoiceEvaluationResponse,
    PrepositionChoiceHistoryResponse,
    PrepositionChoicePairStatsResponse,
)

router = APIRouter(
    prefix="/api/v1/prepositions/exercises/preposition-choice",
    tags=["Preposition Choice Exercises"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.post("/generate", response_model=PrepositionChoiceExercisePromptResponse)
async def generate_exercise(
    payload: PrepositionChoiceExerciseRequest,
    svc: PrepositionChoiceExerciseSvcDep,
    current_user: CurrentUserDep,
):
    prompt, prompt_token = await svc.generate(
        user_id=current_user.user_id,
        target_language_code=payload.target_language_code,
    )
    return PrepositionChoiceExercisePromptResponse(
        option_a=prompt.option_a,
        option_b=prompt.option_b,
        target_language_code=prompt.target_language_code,
        scenario_native=prompt.scenario_native,
        sentence_with_blank=prompt.sentence_with_blank,
        prompt_token=prompt_token,
    )


@router.post("/evaluate", response_model=PrepositionChoiceEvaluationResponse)
async def evaluate_answer(
    payload: PrepositionChoiceAnswerRequest,
    svc: PrepositionChoiceExerciseSvcDep,
    current_user: CurrentUserDep,
):
    evaluation = await svc.evaluate(
        user_id=current_user.user_id,
        prompt_token=payload.prompt_token,
        user_answer=payload.user_answer,
    )
    return PrepositionChoiceEvaluationResponse(
        is_correct=evaluation.is_correct,
        feedback=evaluation.feedback,
        correct_preposition=evaluation.correct_preposition,
        sentence_complete=evaluation.sentence_complete,
    )


@router.get("/history", response_model=list[PrepositionChoiceHistoryResponse])
async def get_history(
    svc: PrepositionChoiceExerciseSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 50,
):
    records = await svc.get_history(current_user.user_id, skip=skip, limit=limit)
    return [
        PrepositionChoiceHistoryResponse(
            id=r.id,  # type: ignore[arg-type]
            option_a=r.option_a,
            option_b=r.option_b,
            target_language_code=r.target_language_code,
            scenario_native=r.scenario_native,
            sentence_with_blank=r.sentence_with_blank,
            sentence_complete=r.sentence_complete,
            correct_preposition=r.correct_preposition,
            user_answer=r.user_answer,
            is_correct=r.is_correct,
            feedback=r.feedback,
            created_at=r.created_at,  # type: ignore[arg-type]
        )
        for r in records
    ]


@router.get("/stats", response_model=list[PrepositionChoicePairStatsResponse])
async def get_stats(
    svc: PrepositionChoiceExerciseSvcDep,
    current_user: CurrentUserDep,
):
    stats = await svc.get_stats(current_user.user_id)
    return [
        PrepositionChoicePairStatsResponse(
            option_a=s.option_a,
            option_b=s.option_b,
            correct_count=s.correct_count,
            incorrect_count=s.incorrect_count,
        )
        for s in stats
    ]

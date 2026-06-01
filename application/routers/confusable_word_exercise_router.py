from fastapi import APIRouter, Depends

from application.routers.dependency_utils import (
    ConfusableWordExerciseSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.confusable_word_exercise_schema import (
    ConfusableWordExerciseRequest,
    ConfusableWordExercisePromptResponse,
    ConfusableWordAnswerRequest,
    ConfusableWordEvaluationResponse,
    ConfusableWordHistoryResponse,
    ConfusableWordPairStatsResponse,
)

router = APIRouter(
    prefix="/api/v1/confusable-words/exercises",
    tags=["Confusable Word Exercises"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.post("/generate", response_model=ConfusableWordExercisePromptResponse)
async def generate_exercise(
    payload: ConfusableWordExerciseRequest,
    svc: ConfusableWordExerciseSvcDep,
    current_user: CurrentUserDep,
):
    prompt, prompt_token = await svc.generate(
        user_id=current_user.user_id,
        target_language_code=payload.target_language_code,
    )
    return ConfusableWordExercisePromptResponse(
        option_a=prompt.option_a,
        option_b=prompt.option_b,
        target_language_code=prompt.target_language_code,
        scenario_native=prompt.scenario_native,
        sentence_with_blank=prompt.sentence_with_blank,
        prompt_token=prompt_token,
    )


@router.post("/evaluate", response_model=ConfusableWordEvaluationResponse)
async def evaluate_answer(
    payload: ConfusableWordAnswerRequest,
    svc: ConfusableWordExerciseSvcDep,
    current_user: CurrentUserDep,
):
    evaluation = await svc.evaluate(
        user_id=current_user.user_id,
        prompt_token=payload.prompt_token,
        user_answer=payload.user_answer,
    )
    return ConfusableWordEvaluationResponse(
        is_correct=evaluation.is_correct,
        feedback=evaluation.feedback,
        correct_word=evaluation.correct_word,
        sentence_complete=evaluation.sentence_complete,
    )


@router.get("/history", response_model=list[ConfusableWordHistoryResponse])
async def get_history(
    svc: ConfusableWordExerciseSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 50,
):
    records = await svc.get_history(current_user.user_id, skip=skip, limit=limit)
    return [
        ConfusableWordHistoryResponse(
            id=r.id,  # type: ignore[arg-type]
            option_a=r.option_a,
            option_b=r.option_b,
            target_language_code=r.target_language_code,
            scenario_native=r.scenario_native,
            sentence_with_blank=r.sentence_with_blank,
            sentence_complete=r.sentence_complete,
            correct_word=r.correct_word,
            user_answer=r.user_answer,
            is_correct=r.is_correct,
            feedback=r.feedback,
            created_at=r.created_at,  # type: ignore[arg-type]
        )
        for r in records
    ]


@router.get("/stats", response_model=list[ConfusableWordPairStatsResponse])
async def get_stats(
    svc: ConfusableWordExerciseSvcDep,
    current_user: CurrentUserDep,
):
    stats = await svc.get_stats(current_user.user_id)
    return [
        ConfusableWordPairStatsResponse(
            option_a=s.option_a,
            option_b=s.option_b,
            correct_count=s.correct_count,
            incorrect_count=s.incorrect_count,
        )
        for s in stats
    ]

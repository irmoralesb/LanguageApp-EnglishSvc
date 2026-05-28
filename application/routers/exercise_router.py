from fastapi import APIRouter, Depends

from application.routers.dependency_utils import (
    ExerciseSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.exercise_schema import (
    ExerciseRequest,
    ExercisePromptResponse,
    ExerciseAnswerRequest,
    ExerciseEvaluationResponse,
    ExerciseHistoryResponse,
    PracticeTermStatsResponse,
)

router = APIRouter(
    prefix="/api/v1/prepositions/exercises",
    tags=["Prepositions Exercises"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.post("/generate", response_model=ExercisePromptResponse)
async def generate_exercise(
    payload: ExerciseRequest,
    svc: ExerciseSvcDep,
    current_user: CurrentUserDep,
):
    prompt = await svc.generate_exercise(
        user_id=current_user.user_id,
        target_language_code=payload.target_language_code,
        practice_term_id=payload.practice_term_id,
        situation=payload.situation,
    )
    assert prompt.practice_term_id is not None
    return ExercisePromptResponse(
        practice_term_id=prompt.practice_term_id,
        practice_term_text=prompt.practice_term_text,
        term_type=prompt.term_type,
        target_language_code=prompt.target_language_code,
        scenario_native=prompt.scenario_native,
        sentence_native=prompt.sentence_native,
        sentence_target=prompt.sentence_target,
    )


@router.post("/evaluate", response_model=ExerciseEvaluationResponse)
async def evaluate_answer(
    payload: ExerciseAnswerRequest,
    svc: ExerciseSvcDep,
    current_user: CurrentUserDep,
):
    evaluation = await svc.evaluate_answer(
        user_id=current_user.user_id,
        practice_term_id=payload.practice_term_id,
        target_language_code=payload.target_language_code,
        scenario_native=payload.scenario_native,
        sentence_native=payload.sentence_native,
        sentence_target=payload.sentence_target,
        user_answer=payload.user_answer,
    )
    return ExerciseEvaluationResponse(
        is_correct=evaluation.is_correct,
        feedback=evaluation.feedback,
        correct_example=evaluation.correct_example,
    )


@router.get("/history", response_model=list[ExerciseHistoryResponse])
async def get_history(
    svc: ExerciseSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 50,
):
    records = await svc.get_history(current_user.user_id, skip=skip, limit=limit)
    return [
        ExerciseHistoryResponse(
            id=r.id,
            practice_term_id=r.practice_term_id,
            exercise_type=r.exercise_type,
            target_language_code=r.target_language_code,
            scenario_native=r.scenario_native,
            sentence_native=r.sentence_native,
            sentence_target=r.sentence_target,
            user_answer=r.user_answer,
            is_correct=r.is_correct,
            feedback=r.feedback,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/stats", response_model=list[PracticeTermStatsResponse])
async def get_stats(
    svc: ExerciseSvcDep,
    current_user: CurrentUserDep,
):
    stats = await svc.get_stats(current_user.user_id)
    return [
        PracticeTermStatsResponse(
            practice_term_id=s.practice_term_id,
            term=s.term,
            term_type=s.term_type,
            correct_count=s.correct_count,
            incorrect_count=s.incorrect_count,
        )
        for s in stats
    ]

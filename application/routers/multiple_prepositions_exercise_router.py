from fastapi import APIRouter, Depends

from application.routers.dependency_utils import (
    MultiplePrepositionsExerciseSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.multiple_prepositions_exercise_schema import (
    MultiplePrepositionsExerciseRequest,
    MultiplePrepositionsExercisePromptResponse,
    MultiplePrepositionsAnswerRequest,
    MultiplePrepositionsEvaluationResponse,
    MultiplePrepositionsHistoryResponse,
    PrepositionFeedbackItem,
)

router = APIRouter(
    prefix="/api/v1/prepositions/exercises/multiple-prepositions",
    tags=["Multiple Prepositions Exercises"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.post("/generate", response_model=MultiplePrepositionsExercisePromptResponse)
async def generate_exercise(
    payload: MultiplePrepositionsExerciseRequest,
    svc: MultiplePrepositionsExerciseSvcDep,
    current_user: CurrentUserDep,
):
    prompt, prompt_token = await svc.generate(
        user_id=current_user.user_id,
        target_language_code=payload.target_language_code,
    )
    return MultiplePrepositionsExercisePromptResponse(
        practice_term_ids=prompt.practice_term_ids,
        practice_term_texts=prompt.practice_term_texts,
        target_language_code=prompt.target_language_code,
        sentence_native=prompt.sentence_native,
        prompt_token=prompt_token,
    )


@router.post("/evaluate", response_model=MultiplePrepositionsEvaluationResponse)
async def evaluate_answer(
    payload: MultiplePrepositionsAnswerRequest,
    svc: MultiplePrepositionsExerciseSvcDep,
    current_user: CurrentUserDep,
):
    evaluation = await svc.evaluate(
        user_id=current_user.user_id,
        prompt_token=payload.prompt_token,
        user_answer=payload.user_answer,
        attempt_number=payload.attempt_number,
    )
    return MultiplePrepositionsEvaluationResponse(
        is_correct=evaluation.is_correct,
        feedback=evaluation.feedback,
        preposition_feedback=[
            PrepositionFeedbackItem(**item) for item in evaluation.preposition_feedback
        ],
        minor_issues=list(evaluation.minor_issues),
        attempt_number=payload.attempt_number,
        correct_sentence_target=evaluation.correct_sentence_target,
    )


@router.get("/history", response_model=list[MultiplePrepositionsHistoryResponse])
async def get_history(
    svc: MultiplePrepositionsExerciseSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 50,
):
    records = await svc.get_history(current_user.user_id, skip=skip, limit=limit)
    return [
        MultiplePrepositionsHistoryResponse(
            id=r.id,  # type: ignore[arg-type]
            practice_term_ids=r.practice_term_ids,
            target_language_code=r.target_language_code,
            sentence_native=r.sentence_native,
            sentence_target=r.sentence_target,
            user_answer=r.user_answer,
            attempt_number=r.attempt_number,
            is_correct=r.is_correct,
            feedback=r.feedback,
            revealed=r.revealed,
            created_at=r.created_at,  # type: ignore[arg-type]
        )
        for r in records
    ]

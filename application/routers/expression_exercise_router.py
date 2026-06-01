from fastapi import APIRouter, Depends

from application.routers.dependency_utils import (
    ExpressionExerciseSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.expression_exercise_schema import (
    ExpressionMcGenerateRequest,
    IdiomCompletePromptResponse,
    CollocationChoicePromptResponse,
    ExpressionMcAnswerRequest,
    ExpressionExerciseEvaluationResponse,
    UseInContextGenerateRequest,
    UseInContextPromptResponse,
    UseInContextAnswerRequest,
    ExpressionExerciseHistoryResponse,
)

router = APIRouter(
    prefix="/api/v1/expressions/exercises",
    tags=["Expression Exercises"],
    dependencies=[Depends(require_role("english-user"))],
)


@router.post("/idiom-complete/generate", response_model=IdiomCompletePromptResponse)
async def generate_idiom_complete(
    payload: ExpressionMcGenerateRequest,
    svc: ExpressionExerciseSvcDep,
    current_user: CurrentUserDep,
):
    prompt, prompt_token = await svc.generate_idiom_complete(
        user_id=current_user.user_id,
        english_expression_id=payload.english_expression_id,
    )
    return IdiomCompletePromptResponse(
        english_expression_id=prompt.english_expression_id,
        text=prompt.text,
        definition=prompt.definition,
        sentence_with_blank=prompt.sentence_with_blank,
        options=prompt.options,
        scenario_native=prompt.scenario_native,
        prompt_token=prompt_token,
    )


@router.post("/collocation-choice/generate", response_model=CollocationChoicePromptResponse)
async def generate_collocation_choice(
    payload: ExpressionMcGenerateRequest,
    svc: ExpressionExerciseSvcDep,
    current_user: CurrentUserDep,
):
    prompt, prompt_token = await svc.generate_collocation_choice(
        user_id=current_user.user_id,
        english_expression_id=payload.english_expression_id,
    )
    return CollocationChoicePromptResponse(
        english_expression_id=prompt.english_expression_id,
        text=prompt.text,
        definition=prompt.definition,
        sentence_with_blank=prompt.sentence_with_blank,
        options=prompt.options,
        scenario_native=prompt.scenario_native,
        prompt_token=prompt_token,
    )


@router.post("/idiom-complete/evaluate", response_model=ExpressionExerciseEvaluationResponse)
@router.post("/collocation-choice/evaluate", response_model=ExpressionExerciseEvaluationResponse)
async def evaluate_multiple_choice(
    payload: ExpressionMcAnswerRequest,
    svc: ExpressionExerciseSvcDep,
    current_user: CurrentUserDep,
):
    evaluation = await svc.evaluate_multiple_choice(
        user_id=current_user.user_id,
        prompt_token=payload.prompt_token,
        user_answer=payload.user_answer,
    )
    return ExpressionExerciseEvaluationResponse(
        is_correct=evaluation.is_correct,
        feedback=evaluation.feedback,
        correct_example=evaluation.correct_example,
    )


@router.post("/use-in-context/generate", response_model=UseInContextPromptResponse)
async def generate_use_in_context(
    payload: UseInContextGenerateRequest,
    svc: ExpressionExerciseSvcDep,
    current_user: CurrentUserDep,
):
    prompt = await svc.generate_use_in_context(
        user_id=current_user.user_id,
        target_language_code=payload.target_language_code,
        english_expression_id=payload.english_expression_id,
    )
    return UseInContextPromptResponse(
        english_expression_id=prompt.english_expression_id,
        text=prompt.text,
        expression_type=prompt.expression_type,
        definition=prompt.definition,
        target_language_code=prompt.target_language_code,
        scenario_native=prompt.scenario_native,
        prompt_native=prompt.prompt_native,
        expected_answer=prompt.expected_answer,
    )


@router.post("/use-in-context/evaluate", response_model=ExpressionExerciseEvaluationResponse)
async def evaluate_use_in_context(
    payload: UseInContextAnswerRequest,
    svc: ExpressionExerciseSvcDep,
    current_user: CurrentUserDep,
):
    evaluation = await svc.evaluate_use_in_context(
        user_id=current_user.user_id,
        english_expression_id=payload.english_expression_id,
        target_language_code=payload.target_language_code,
        scenario_native=payload.scenario_native,
        prompt_native=payload.prompt_native,
        expected_answer=payload.expected_answer,
        user_answer=payload.user_answer,
    )
    return ExpressionExerciseEvaluationResponse(
        is_correct=evaluation.is_correct,
        feedback=evaluation.feedback,
        correct_example=evaluation.correct_example,
    )


@router.get("/history", response_model=list[ExpressionExerciseHistoryResponse])
async def get_history(
    svc: ExpressionExerciseSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 50,
):
    records = await svc.get_history(current_user.user_id, skip=skip, limit=limit)
    return [
        ExpressionExerciseHistoryResponse(
            id=r.id,  # type: ignore[arg-type]
            english_expression_id=r.english_expression_id,
            exercise_type=r.exercise_type,
            target_language_code=r.target_language_code,
            scenario_native=r.scenario_native,
            prompt_native=r.prompt_native,
            expected_answer=r.expected_answer,
            user_answer=r.user_answer,
            is_correct=r.is_correct,
            feedback=r.feedback,
            created_at=r.created_at,  # type: ignore[arg-type]
        )
        for r in records
    ]

from typing import Annotated, AsyncIterator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from application.services.authorization_service import AuthorizationService
from application.services.chat_service import ChatService
from application.services.exercise_service import ExerciseService
from application.services.multiple_prepositions_exercise_service import (
    MultiplePrepositionsExerciseService,
)
from application.services.preposition_choice_exercise_service import (
    PrepositionChoiceExerciseService,
)
from application.services.confusable_word_exercise_service import (
    ConfusableWordExerciseService,
)
from application.services.natural_rewrite_exercise_service import (
    NaturalRewriteExerciseService,
)
from application.services.register_switch_exercise_service import (
    RegisterSwitchExerciseService,
)
from application.services.english_expression_catalog_service import (
    EnglishExpressionCatalogService,
)
from application.services.expression_exercise_service import ExpressionExerciseService
from application.services.phrasal_verb_catalog_service import PhrasalVerbCatalogService
from application.services.phrasal_verb_exercise_service import PhrasalVerbExerciseService
from application.services.practice_term_catalog_service import PracticeTermCatalogService
from application.services.prompt_token_service import PromptTokenService
from application.services.token_service import TokenService
from application.services.user_profile_service import UserProfileService
from core.settings import app_settings
from domain.entities.token_claims import UserClaims
from domain.exceptions.auth_errors import MissingRoleError
from domain.interfaces.llm_provider import LLMProviderInterface
from infrastructure.databases.database import get_monitored_db_session
from infrastructure.observability.security_logger import (
    log_authentication_failure,
    log_authentication_success,
    log_role_check_denied,
    log_role_check_granted,
)
from infrastructure.repositories.chat_message_repository import ChatMessageRepository
from infrastructure.repositories.chat_session_repository import ChatSessionRepository
from infrastructure.repositories.exercise_repository import ExerciseRepository
from infrastructure.repositories.language_repository import LanguageRepository
from infrastructure.repositories.multiple_prepositions_exercise_repository import (
    MultiplePrepositionsExerciseRepository,
)
from infrastructure.repositories.preposition_choice_exercise_repository import (
    PrepositionChoiceExerciseRepository,
)
from infrastructure.repositories.confusable_word_exercise_repository import (
    ConfusableWordExerciseRepository,
)
from infrastructure.repositories.natural_rewrite_exercise_repository import (
    NaturalRewriteExerciseRepository,
)
from infrastructure.repositories.register_switch_exercise_repository import (
    RegisterSwitchExerciseRepository,
)
from infrastructure.repositories.english_expression_repository import (
    EnglishExpressionRepository,
)
from infrastructure.repositories.expression_exercise_repository import (
    ExpressionExerciseRepository,
)
from infrastructure.repositories.phrasal_verb_exercise_repository import (
    PhrasalVerbExerciseRepository,
)
from infrastructure.repositories.phrasal_verb_repository import PhrasalVerbRepository
from infrastructure.repositories.practice_term_repository import PracticeTermRepository
from infrastructure.repositories.user_profile_repository import UserProfileRepository


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with get_monitored_db_session() as db:
        yield db


def get_language_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> LanguageRepository:
    return LanguageRepository(db)


def get_practice_term_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> PracticeTermRepository:
    return PracticeTermRepository(db)


def get_user_profile_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> UserProfileRepository:
    return UserProfileRepository(db)


def get_exercise_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> ExerciseRepository:
    return ExerciseRepository(db)


def get_multiple_prepositions_exercise_repository(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> MultiplePrepositionsExerciseRepository:
    return MultiplePrepositionsExerciseRepository(db)


def get_preposition_choice_exercise_repository(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> PrepositionChoiceExerciseRepository:
    return PrepositionChoiceExerciseRepository(db)


def get_confusable_word_exercise_repository(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ConfusableWordExerciseRepository:
    return ConfusableWordExerciseRepository(db)


def get_natural_rewrite_exercise_repository(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> NaturalRewriteExerciseRepository:
    return NaturalRewriteExerciseRepository(db)


def get_register_switch_exercise_repository(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> RegisterSwitchExerciseRepository:
    return RegisterSwitchExerciseRepository(db)


def get_english_expression_repository(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnglishExpressionRepository:
    return EnglishExpressionRepository(db)


def get_expression_exercise_repository(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExpressionExerciseRepository:
    return ExpressionExerciseRepository(db)


def get_phrasal_verb_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> PhrasalVerbRepository:
    return PhrasalVerbRepository(db)


def get_phrasal_verb_exercise_repository(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> PhrasalVerbExerciseRepository:
    return PhrasalVerbExerciseRepository(db)


def get_chat_session_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> ChatSessionRepository:
    return ChatSessionRepository(db)


def get_chat_message_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> ChatMessageRepository:
    return ChatMessageRepository(db)


def get_prompt_token_service() -> PromptTokenService:
    return PromptTokenService(secret_key=app_settings.secret_token_key)


def get_llm_provider() -> LLMProviderInterface:
    from infrastructure.llm.langchain_provider import LangChainProvider
    return LangChainProvider(
        provider=app_settings.llm_provider,
        api_key=app_settings.llm_api_key,
        model=app_settings.llm_model,
        max_tokens=app_settings.llm_max_tokens,
        temperature=app_settings.llm_temperature,
    )


def get_practice_term_catalog_service(
    repo: Annotated[PracticeTermRepository, Depends(get_practice_term_repository)],
) -> PracticeTermCatalogService:
    return PracticeTermCatalogService(repo)


def get_user_profile_service(
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
) -> UserProfileService:
    return UserProfileService(profile_repo, language_repo)


def get_exercise_service(
    exercise_repo: Annotated[ExerciseRepository, Depends(get_exercise_repository)],
    term_repo: Annotated[PracticeTermRepository, Depends(get_practice_term_repository)],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
    llm: Annotated[LLMProviderInterface, Depends(get_llm_provider)],
) -> ExerciseService:
    return ExerciseService(exercise_repo, term_repo, profile_repo, language_repo, llm)


def get_multiple_prepositions_exercise_service(
    exercise_repo: Annotated[
        MultiplePrepositionsExerciseRepository,
        Depends(get_multiple_prepositions_exercise_repository),
    ],
    term_repo: Annotated[PracticeTermRepository, Depends(get_practice_term_repository)],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
    llm: Annotated[LLMProviderInterface, Depends(get_llm_provider)],
    prompt_token_svc: Annotated[PromptTokenService, Depends(get_prompt_token_service)],
) -> MultiplePrepositionsExerciseService:
    return MultiplePrepositionsExerciseService(
        exercise_repo, term_repo, profile_repo, language_repo, llm, prompt_token_svc,
    )


def get_preposition_choice_exercise_service(
    exercise_repo: Annotated[
        PrepositionChoiceExerciseRepository,
        Depends(get_preposition_choice_exercise_repository),
    ],
    term_repo: Annotated[PracticeTermRepository, Depends(get_practice_term_repository)],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
    llm: Annotated[LLMProviderInterface, Depends(get_llm_provider)],
    prompt_token_svc: Annotated[PromptTokenService, Depends(get_prompt_token_service)],
) -> PrepositionChoiceExerciseService:
    return PrepositionChoiceExerciseService(
        exercise_repo, term_repo, profile_repo, language_repo, llm, prompt_token_svc,
    )


def get_confusable_word_exercise_service(
    exercise_repo: Annotated[
        ConfusableWordExerciseRepository,
        Depends(get_confusable_word_exercise_repository),
    ],
    term_repo: Annotated[PracticeTermRepository, Depends(get_practice_term_repository)],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
    llm: Annotated[LLMProviderInterface, Depends(get_llm_provider)],
    prompt_token_svc: Annotated[PromptTokenService, Depends(get_prompt_token_service)],
) -> ConfusableWordExerciseService:
    return ConfusableWordExerciseService(
        exercise_repo, term_repo, profile_repo, language_repo, llm, prompt_token_svc,
    )


def get_natural_rewrite_exercise_service(
    exercise_repo: Annotated[
        NaturalRewriteExerciseRepository,
        Depends(get_natural_rewrite_exercise_repository),
    ],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
    llm: Annotated[LLMProviderInterface, Depends(get_llm_provider)],
    prompt_token_svc: Annotated[PromptTokenService, Depends(get_prompt_token_service)],
) -> NaturalRewriteExerciseService:
    return NaturalRewriteExerciseService(
        exercise_repo, profile_repo, language_repo, llm, prompt_token_svc,
    )


def get_register_switch_exercise_service(
    exercise_repo: Annotated[
        RegisterSwitchExerciseRepository,
        Depends(get_register_switch_exercise_repository),
    ],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
    llm: Annotated[LLMProviderInterface, Depends(get_llm_provider)],
    prompt_token_svc: Annotated[PromptTokenService, Depends(get_prompt_token_service)],
) -> RegisterSwitchExerciseService:
    return RegisterSwitchExerciseService(
        exercise_repo, profile_repo, language_repo, llm, prompt_token_svc,
    )


def get_english_expression_catalog_service(
    repo: Annotated[EnglishExpressionRepository, Depends(get_english_expression_repository)],
) -> EnglishExpressionCatalogService:
    return EnglishExpressionCatalogService(repo)


def get_expression_exercise_service(
    exercise_repo: Annotated[
        ExpressionExerciseRepository,
        Depends(get_expression_exercise_repository),
    ],
    expression_repo: Annotated[
        EnglishExpressionRepository, Depends(get_english_expression_repository),
    ],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
    llm: Annotated[LLMProviderInterface, Depends(get_llm_provider)],
    prompt_token_svc: Annotated[PromptTokenService, Depends(get_prompt_token_service)],
) -> ExpressionExerciseService:
    return ExpressionExerciseService(
        exercise_repo,
        expression_repo,
        profile_repo,
        language_repo,
        llm,
        prompt_token_svc,
    )


def get_phrasal_verb_catalog_service(
    repo: Annotated[PhrasalVerbRepository, Depends(get_phrasal_verb_repository)],
) -> PhrasalVerbCatalogService:
    return PhrasalVerbCatalogService(repo)


def get_phrasal_verb_exercise_service(
    exercise_repo: Annotated[
        PhrasalVerbExerciseRepository,
        Depends(get_phrasal_verb_exercise_repository),
    ],
    phrasal_verb_repo: Annotated[PhrasalVerbRepository, Depends(get_phrasal_verb_repository)],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
    llm: Annotated[LLMProviderInterface, Depends(get_llm_provider)],
) -> PhrasalVerbExerciseService:
    return PhrasalVerbExerciseService(
        exercise_repo,
        phrasal_verb_repo,
        profile_repo,
        language_repo,
        llm,
    )


def get_chat_service(
    session_repo: Annotated[ChatSessionRepository, Depends(get_chat_session_repository)],
    message_repo: Annotated[ChatMessageRepository, Depends(get_chat_message_repository)],
    llm: Annotated[LLMProviderInterface, Depends(get_llm_provider)],
) -> ChatService:
    return ChatService(session_repo, message_repo, llm)


def get_token_service() -> TokenService:
    return TokenService(
        app_settings.secret_token_key,
        app_settings.auth_algorithm,
    )


def get_authorization_service() -> AuthorizationService:
    return AuthorizationService()


oauth_bearer = OAuth2PasswordBearer(tokenUrl=app_settings.token_url)


async def get_authenticated_user(
    token: Annotated[str, Depends(oauth_bearer)],
    token_svc: Annotated[TokenService, Depends(get_token_service)],
) -> UserClaims:
    try:
        claims = token_svc.decode_token(token)
        log_authentication_success(claims.user_id, claims.email)
        return claims
    except Exception:
        log_authentication_failure("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )


def require_role(role_name: str):
    async def role_checker(
            current_user: CurrentUserDep,
            authz_svc: AuthzSvcDep,
    ) -> bool:
        try:
            has_role = authz_svc.check_role(current_user, role_name)
            if has_role:
                log_role_check_granted(current_user.user_id, role_name)
                return True
        except MissingRoleError:
            log_role_check_denied(current_user.user_id, role_name)
            raise
        return False
    return role_checker


LanguageRepoDep = Annotated[LanguageRepository, Depends(get_language_repository)]
PracticeTermSvcDep = Annotated[PracticeTermCatalogService, Depends(get_practice_term_catalog_service)]
UserProfileSvcDep = Annotated[UserProfileService, Depends(get_user_profile_service)]
ExerciseSvcDep = Annotated[ExerciseService, Depends(get_exercise_service)]
MultiplePrepositionsExerciseSvcDep = Annotated[
    MultiplePrepositionsExerciseService,
    Depends(get_multiple_prepositions_exercise_service),
]
PrepositionChoiceExerciseSvcDep = Annotated[
    PrepositionChoiceExerciseService,
    Depends(get_preposition_choice_exercise_service),
]
ConfusableWordExerciseSvcDep = Annotated[
    ConfusableWordExerciseService,
    Depends(get_confusable_word_exercise_service),
]
NaturalRewriteExerciseSvcDep = Annotated[
    NaturalRewriteExerciseService,
    Depends(get_natural_rewrite_exercise_service),
]
RegisterSwitchExerciseSvcDep = Annotated[
    RegisterSwitchExerciseService,
    Depends(get_register_switch_exercise_service),
]
EnglishExpressionSvcDep = Annotated[
    EnglishExpressionCatalogService,
    Depends(get_english_expression_catalog_service),
]
ExpressionExerciseSvcDep = Annotated[
    ExpressionExerciseService,
    Depends(get_expression_exercise_service),
]
PhrasalVerbSvcDep = Annotated[PhrasalVerbCatalogService, Depends(get_phrasal_verb_catalog_service)]
PhrasalVerbExerciseSvcDep = Annotated[
    PhrasalVerbExerciseService,
    Depends(get_phrasal_verb_exercise_service),
]
ChatSvcDep = Annotated[ChatService, Depends(get_chat_service)]
TokenSvcDep = Annotated[TokenService, Depends(get_token_service)]
CurrentUserDep = Annotated[UserClaims, Depends(get_authenticated_user)]
AuthzSvcDep = Annotated[AuthorizationService, Depends(get_authorization_service)]

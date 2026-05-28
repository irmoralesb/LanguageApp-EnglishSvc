from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user_profile_model import (
    UserProfileModel,
    UserPracticeTermSelectionModel,
    UserPhrasalVerbSelectionModel,
)


class UserProfileRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> UserProfileModel | None:
        ...

    @abstractmethod
    async def create(self, profile: UserProfileModel) -> UserProfileModel:
        ...

    @abstractmethod
    async def update(self, profile: UserProfileModel) -> UserProfileModel | None:
        ...

    @abstractmethod
    async def add_learning_language(self, user_id: UUID, language_id: UUID) -> None:
        ...

    @abstractmethod
    async def remove_learning_language(self, user_id: UUID, language_id: UUID) -> None:
        ...

    @abstractmethod
    async def get_practice_term_selections(self, user_id: UUID) -> list[UserPracticeTermSelectionModel]:
        ...

    @abstractmethod
    async def add_practice_term_selection(
        self, user_id: UUID, practice_term_id: UUID,
    ) -> UserPracticeTermSelectionModel:
        ...

    @abstractmethod
    async def remove_practice_term_selection(self, user_id: UUID, practice_term_id: UUID) -> bool:
        ...

    @abstractmethod
    async def get_phrasal_verb_selections(self, user_id: UUID) -> list[UserPhrasalVerbSelectionModel]:
        ...

    @abstractmethod
    async def add_phrasal_verb_selection(
        self, user_id: UUID, phrasal_verb_id: UUID
    ) -> UserPhrasalVerbSelectionModel:
        ...

    @abstractmethod
    async def remove_phrasal_verb_selection(self, user_id: UUID, phrasal_verb_id: UUID) -> bool:
        ...

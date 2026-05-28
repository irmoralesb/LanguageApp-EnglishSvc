from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user_profile_model import UserPhrasalVerbSelectionModel


class PhrasalUserProfileRepositoryInterface(ABC):
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

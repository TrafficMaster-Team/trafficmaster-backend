from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.application.common.query_params.card_filters import CardQueryFilters
from trafficmaster.application.common.query_params.sorting import SortingOrder
from trafficmaster.presentation.http.v1.routes.card.read.schemas import ReadCardResponseSchema


class ReadAllCardsRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    deck_id: UUID = Field(title="Deck ID", description="The ID of the deck whose cards to read")
    limit: int = Field(default=20, ge=1, le=100, title="Pagination", description="Limit for pagination")
    offset: int = Field(default=0, ge=0, title="Pagination", description="Offset for pagination")
    sorting_field: Annotated[
        CardQueryFilters,
        Field(title="Card sorting field", description="Field for sorting", examples=["question", "created_at"]),
    ] = CardQueryFilters.question
    sorting_order: Annotated[
        SortingOrder,
        Field(title="Sorting order", description="Sorting order", examples=["ASC", "DESC"]),
    ] = SortingOrder.DESC
    tags: Annotated[
        list[str] | None,
        Field(title="Tags", description="Filter cards by tags"),
    ] = None


class ReadAllCardsResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    cards: list[ReadCardResponseSchema] = Field(default=[], title="Cards", description="The cards of the deck")

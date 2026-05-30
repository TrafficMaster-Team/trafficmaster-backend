from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.application.common.query_params.sorting import SortingOrder
from trafficmaster.application.common.query_params.user_filters import UserQueryFilters
from trafficmaster.presentation.http.v1.routes.user.read.schemas import ReadUserByIDResponse


class ReadAllUsersRequestSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    limit: int = Field(default=20, ge=1, le=100, description="Limit for pagination", title="Pagination")

    offset: int = Field(
        default=0,
        ge=0,
        description="Offset for pagination",
        title="Pagination",
    )

    sorting_field: Annotated[
        UserQueryFilters,
        Field(
            description="Field for sorting",
            title="User sorting field",
            examples=[
                "email",
                "name",
                "updated_at",
                "created_at",
            ],
        ),
    ] = UserQueryFilters.email

    sorting_order: Annotated[
        SortingOrder,
        Field(
            description="Sorting order",
            title="Pagination",
            examples=["ASC", "DESC"],
        ),
    ] = SortingOrder.DESC


class ReadAllUsersResponseSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    users: list[ReadUserByIDResponse] = Field(
        description="List of users",
        title="Users",
        default=[],
    )

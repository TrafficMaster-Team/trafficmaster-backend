from inspect import getdoc
from typing import TYPE_CHECKING, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from trafficmaster.application.auth.sign_up import SignUpData, SignUpHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.routes.auth.sign_up.schemas import SignUpRequestSchema, SignUpResponseSchema

if TYPE_CHECKING:
    from trafficmaster.application.common.views.auth.sign_up import SignUpView

sign_up_route: Final[APIRouter] = APIRouter(tags=["Auth"], route_class=DishkaRoute)


@sign_up_route.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="Sign up a new user",
    description=getdoc(SignUpHandler),
    response_model=SignUpResponseSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def sign_up(
    request: SignUpRequestSchema,
    interactor: FromDishka[SignUpHandler],
) -> SignUpResponseSchema:
    data: SignUpData = SignUpData(
        email=request.email,
        name=request.name,
        password=request.password,
    )

    view: SignUpView = await interactor(data=data)

    return SignUpResponseSchema(id=view.id)

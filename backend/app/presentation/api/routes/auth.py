from fastapi import APIRouter, status

from dishka.integrations.fastapi import DishkaRoute, FromDishka

from app.application.use_cases.auth.login_user import (
    LoginUserCommand,
    LoginUserUseCase,
)
from app.application.use_cases.auth.register_user import (
    RegisterUserCommand,
    RegisterUserUseCase,
)
from app.presentation.api.schemas import (
    LoginRequest,
    RegisteredUserResponse,
    RegisterUserRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Auth"], route_class=DishkaRoute)


@router.post(
    "/register",
    response_model=RegisteredUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    request: RegisterUserRequest,
    use_case: FromDishka[RegisterUserUseCase],
) -> RegisteredUserResponse:
    result = await use_case.execute(
        RegisterUserCommand(
            email=request.email,
            password=request.password,
        )
    )

    return RegisteredUserResponse.model_validate(result)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login_user(
    request: LoginRequest,
    use_case: FromDishka[LoginUserUseCase],
) -> TokenResponse:
    result = await use_case.execute(
        LoginUserCommand(
            email=request.email,
            password=request.password,
        )
    )

    return TokenResponse(
        access_token=result.access_token,
        token_type=result.token_type,
    )

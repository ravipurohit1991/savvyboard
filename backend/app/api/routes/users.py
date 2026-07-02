from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep, SessionDep
from app.crud.user import update_user
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_user_me(current_user: CurrentUserDep) -> Any:
    return current_user


@router.patch("/me", response_model=UserOut)
def update_user_me(
    session: SessionDep,
    current_user: CurrentUserDep,
    user_in: UserUpdate,
) -> Any:
    if user_in.email and user_in.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email updates are not supported through this endpoint.",
        )
    user = update_user(session, current_user, user_in)
    return user

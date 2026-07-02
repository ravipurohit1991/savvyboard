from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session

from app.core.config import settings
from app.core.db import get_session
from app.core.security import decode_token
from app.crud.workspace import get_member_role
from app.models import User, UserRole, Workspace
from app.schemas.common import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


class OAuth2Optional(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str | None:
        try:
            return await super().__call__(request)
        except HTTPException:
            return None


oauth2_scheme_optional = OAuth2Optional(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator[Session, None, None]:
    with Session(get_session().__next__().bind.engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except JWTError:
        raise credentials_exception
    if token_data.sub is None or token_data.type != "access":
        raise credentials_exception
    user = session.get(User, UUID(token_data.sub))
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def get_optional_current_user(
    session: SessionDep,
    token: Annotated[str | None, Depends(oauth2_scheme_optional)],
) -> User | None:
    if token is None:
        return None
    try:
        payload = decode_token(token)
        if payload is None:
            return None
        token_data = TokenPayload(**payload)
        if token_data.sub is None or token_data.type != "access":
            return None
        user = session.get(User, UUID(token_data.sub))
        return user if user and user.is_active else None
    except (JWTError, ValueError):
        return None


CurrentUserDep = Annotated[User, Depends(get_current_user)]
OptionalUserDep = Annotated[User | None, Depends(get_optional_current_user)]


def require_workspace_role(min_role: UserRole):
    role_order = {UserRole.MEMBER: 0, UserRole.ADMIN: 1, UserRole.OWNER: 2}

    def checker(
        workspace_id: UUID,
        current_user: CurrentUserDep,
        session: SessionDep,
    ) -> Workspace:
        from app.crud.workspace import get_workspace

        workspace = get_workspace(session, workspace_id)
        if not workspace:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
        if current_user.is_superuser:
            return workspace
        role = get_member_role(session, workspace_id, current_user.id)
        if role is None or role_order[role] < role_order[min_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )
        return workspace

    return checker


def get_anonymous_token(anonymous_token: Annotated[str | None, Header()] = None) -> str | None:
    return anonymous_token


AnonTokenDep = Annotated[str | None, Depends(get_anonymous_token)]

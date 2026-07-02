from fastapi import APIRouter

from app.api.routes import (
    auth,
    boards,
    changelog,
    dashboard,
    feedback,
    public,
    roadmap,
    users,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(workspaces.router)
api_router.include_router(boards.router)
api_router.include_router(feedback.router)
api_router.include_router(roadmap.router)
api_router.include_router(changelog.router)
api_router.include_router(dashboard.router)
api_router.include_router(public.router)

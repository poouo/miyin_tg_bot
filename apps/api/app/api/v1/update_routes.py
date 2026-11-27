from fastapi import APIRouter

from apps.api.app.services.update_service import (
    check_update,
    get_online_update_status,
    read_background_status,
    trigger_online_update,
)

router = APIRouter(prefix="/updates", tags=["updates"])


@router.get("/check")
def check_repo_update() -> dict:
    return check_update()


@router.post("/online")
def start_online_update() -> dict:
    return trigger_online_update()


@router.get("/online-status")
def online_update_status() -> dict:
    return get_online_update_status()


@router.get("/background-status")
async def get_background_update_status() -> dict:
    return read_background_status()

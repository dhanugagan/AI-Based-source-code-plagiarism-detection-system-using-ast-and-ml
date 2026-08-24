from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.auth import UserOut
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.admin import Admin
from app.usuarios.schemas import LoginRequest, TokenResponse, AdminResponse
from app.usuarios.service import authenticate_admin, create_access_token

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    admin = await authenticate_admin(db, data.email, data.password)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(admin.email)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me", response_model=AdminResponse)
async def me(admin: Admin = Depends(get_current_admin)):
    return admin

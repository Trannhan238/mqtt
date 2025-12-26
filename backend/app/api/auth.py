from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.session import get_db
from app.models.domain import User
from app.core.security import SecurityHandler
from app.core.config import settings
from app.schemas.auth import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # 1. Kiểm tra User trong DB
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # 2. Xác thực mật khẩu
    if not user or not SecurityHandler.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tài khoản hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Tạo Token
    access_token = SecurityHandler.create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}
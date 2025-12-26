from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.domain import User

# Sử dụng bcrypt để băm mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Định nghĩa cơ chế lấy Token từ Header (Dùng cho Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class SecurityHandler:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(subject: Union[str, Any]) -> str:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES # Lưu ý: check lại typo MINITES/MINUTES trong file config của ông nhé
        )
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def clean_mac(mac: str) -> str:
        """Chuẩn hóa MAC address để làm Topic MQTT (VD: 2C:BC... -> 2CBC...)"""
        return mac.replace(":", "").replace("-", "").upper()

    @staticmethod
    async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
    ) -> User:
        """
        Hàm trung gian (Dependency) để lấy User hiện tại từ JWT Token.
        Nếu Token lỏ hoặc hết hạn, nó sẽ đá văng người dùng ra (401).
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể xác thực quyền truy cập, vui lòng đăng nhập lại!",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            # 1. Giải mã Token
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        # 2. Truy vấn User từ Database
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
        
        return user
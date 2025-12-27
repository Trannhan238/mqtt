from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.domain import User, School
from app.schemas.user import UserCreate, UserResponse # Sếp nhớ định nghĩa Schema nhé
from app.core.security import SecurityHandler

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(SecurityHandler.get_current_user)):
    query = db.query(User)
    # Nếu không phải admin tổng, chỉ lấy user thuộc cùng trường
    if current_user.role != "admin":
        query = query.filter(User.school_id == current_user.school_id)
    return query.all()

@router.post("/", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(SecurityHandler.get_current_user)):
    # Chỉ admin hoặc quản trị trường mới được tạo user
    if current_user.role not in ["admin", "school_admin"]:
        raise HTTPException(status_code=403, detail="Không có quyền tạo người dùng")
    
    # Quản trị trường không được tạo user cho trường khác
    if current_user.role == "school_admin" and user_in.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Bạn chỉ có quyền tạo user cho trường mình")

    db_user = User(
        username=user_in.username,
        password_hash=SecurityHandler.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        school_id=user_in.school_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
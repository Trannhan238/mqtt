from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.domain import School, User
from app.schemas.domain import SchoolCreate, SchoolResponse
from app.core.security import SecurityHandler

router = APIRouter(prefix="/schools", tags=["Schools"])

@router.post("/", response_model=SchoolResponse)
def create_school(
    school_in: SchoolCreate,
    db: Session = Depends(get_db),
    # Dòng này ép buộc phải có Token hợp lệ mới dùng được API này
    current_user: User = Depends(SecurityHandler.get_current_user)
):
    # Kiểm tra xem tên trường đã tồn tại chưa
    db_school = db.query(School).filter(School.name == school_in.name).first()
    if db_school:
        raise HTTPException(status_code=400, detail="Tên trường này đã tồn tại rồi sếp ơi!")
    
    new_school = School(**school_in.model_dump())
    db.add(new_school)
    db.commit()
    db.refresh(new_school)
    return new_school

@router.get("/", response_model=List[SchoolResponse])
def get_all_schools(
    db: Session = Depends(get_db),
    current_user: User = Depends(SecurityHandler.get_current_user)
):
    return db.query(School).all()
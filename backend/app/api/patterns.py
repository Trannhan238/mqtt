from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import BellPattern, User
from app.core.security import SecurityHandler
from pydantic import BaseModel, field_validator

router = APIRouter(prefix="/patterns", tags=["Patterns"])

class PatternCreate(BaseModel):
    name: str
    output_type: str # "CLASSIC" hoặc "SOUND"
    pulse_count: int = 1
    on_duration: float = 3.0  # Đơn vị: Giây
    off_duration: float = 2.0 # Đơn vị: Giây
    school_id: int

    @field_validator("on_duration", "off_duration")
    @classmethod
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Thời gian phải lớn hơn 0")
        return v

@router.post("/")
def create_pattern(p_in: PatternCreate, db: Session = Depends(get_db), current_user: User = Depends(SecurityHandler.get_current_user)):
    # Chuyển đổi Giây -> Mili giây trước khi lưu DB
    pattern_data = p_in.model_dump()
    pattern_data["on_duration"] = int(p_in.on_duration * 1000)
    pattern_data["off_duration"] = int(p_in.off_duration * 1000)
    
    new_p = BellPattern(**pattern_data)
    db.add(new_p)
    db.commit()
    db.refresh(new_p)
    
    print(f"✅ [DB] Đã tạo Pattern: {new_p.name} ({new_p.on_duration}ms ON / {new_p.off_duration}ms OFF)")
    return new_p
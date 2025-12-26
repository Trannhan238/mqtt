from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import BellPattern, User
from app.core.security import SecurityHandler
from pydantic import BaseModel

router = APIRouter(prefix="/patterns", tags=["Patterns"])

class PatternCreate(BaseModel):
    name: str
    output_type: str # "CLASSIC" hoặc "SOUND"
    pulse_count: int = 1
    on_duration: float = 3.0
    off_duration: float = 2.0
    school_id: int

@router.post("/")
def create_pattern(p_in: PatternCreate, db: Session = Depends(get_db), current_user: User = Depends(SecurityHandler.get_current_user)):
    new_p = BellPattern(**p_in.model_dump())
    db.add(new_p)
    db.commit()
    db.refresh(new_p)
    return new_p
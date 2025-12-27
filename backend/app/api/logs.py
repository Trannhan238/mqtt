from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.domain import BellLog, Device
from app.core.security import SecurityHandler

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("/")
def list_logs(
    db: Session = Depends(get_db),
    current_user: str = Depends(SecurityHandler.get_current_user)
):
    """Lấy danh sách nhật ký, ưu tiên cái mới nhất lên đầu"""
    # Nếu là Admin trường, chỉ cho xem log của thiết bị thuộc trường đó
    query = db.query(BellLog).join(Device)
    
    if current_user.role != "admin":
        query = query.filter(Device.school_id == current_user.school_id)
        
    return query.order_by(BellLog.created_at.desc()).limit(100).all()
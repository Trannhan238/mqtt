from pydantic import BaseModel
from datetime import time
from typing import Optional

class ScheduleCreate(BaseModel):
    school_id: int
    day_of_week: int  # 0: Thứ 2, ..., 6: Chủ nhật
    time_point: str   # Định dạng "HH:MM"
    pattern_id: int   # ID của kiểu chuông (Classic/Sound)

class ScheduleResponse(BaseModel):
    id: int
    day_of_week: int
    time_point: time
    is_active: bool

    class Config:
        from_attributes = True
from pydantic import BaseModel
from typing import Optional, List
from datetime import time

class SchoolBase(BaseModel):
    name: str
    address: Optional[str] = None
    use_seasonal_config: bool = False
    winter_start_date: str = "10-15"
    winter_end_date: str = "04-15"
    winter_offset_minutes: int = 15

class SchoolCreate(SchoolBase):
    pass

class SchoolResponse(SchoolBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
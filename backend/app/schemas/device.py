from pydantic import BaseModel
from typing import Optional

class DeviceBase(BaseModel):
    mac_address: str
    name: Optional[str] = "Chuông khu A"
    school_id: int

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: int
    is_active: bool
    is_enabled: bool

    class Config:
        from_attributes = True
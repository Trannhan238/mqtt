import json  # <-- Quan trọng nhất: Để chuyển dict thành chuỗi gửi qua MQTT
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.domain import Device, User
from app.schemas.device import DeviceCreate, DeviceResponse
from app.core.security import SecurityHandler

router = APIRouter(prefix="/devices", tags=["Devices"])

# --- 1. ĐĂNG KÝ THIẾT BỊ ---
@router.post("/", response_model=DeviceResponse)
def register_device(
    device_in: DeviceCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(SecurityHandler.get_current_user)
):
    # Chuẩn hóa MAC (VD: aa:bb -> AABB)
    clean_mac = SecurityHandler.clean_mac(device_in.mac_address)
    
    # Kiểm tra xem MAC đã tồn tại chưa
    db_device = db.query(Device).filter(Device.mac_address == clean_mac).first()
    if db_device:
        raise HTTPException(status_code=400, detail="Thiết bị này đã được đăng ký rồi!")
    
    new_device = Device(
        mac_address=clean_mac,
        name=device_in.name,
        school_id=device_in.school_id,
        is_active=True,
        is_enabled=True
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

# --- 2. LẤY DANH SÁCH THIẾT BỊ ---
@router.get("/", response_model=List[DeviceResponse])
def get_devices(
    db: Session = Depends(get_db), 
    current_user: User = Depends(SecurityHandler.get_current_user)
):
    return db.query(Device).all()

# --- 3. ĐIỀU KHIỂN REO CHUÔNG TỨC THÌ (RING NOW) ---
@router.post("/{mac_address}/ring-now")
async def ring_now(
    mac_address: str,
    request: Request,
    pulses: int = 3,  # Sếp có thể truyền tham số ?pulses=5 trên Swagger
    db: Session = Depends(get_db),
    current_user: User = Depends(SecurityHandler.get_current_user) # Bảo mật: Chỉ Admin mới được bấm
):
    """Lệnh cho chuông reo ngay lập tức qua MQTT"""
    
    # Chuẩn hóa MAC để khớp với Topic MQTT
    clean_mac = mac_address.replace(":", "").upper()
    
    try:
        # Lấy mqtt_handler từ app state đã gắn ở main.py
        if not hasattr(request.app.state, "mqtt_handler"):
            raise HTTPException(status_code=500, detail="Hệ thống MQTT chưa khởi động!")
            
        mqtt_handler = request.app.state.mqtt_handler
        topic = f"school_bell/{clean_mac}/cmd"
        
        # Đóng gói lệnh reo chuông
        payload = {
            "action": "ring_now",
            "p": {
                "n": pulses,
                "on": 1000,   # Thời gian bật LED/Chuông (1 giây)
                "off": 500    # Thời gian nghỉ giữa các hồi (0.5 giây)
            }
        }
        
        # Gửi lệnh đi (json.dumps sẽ biến dict thành chuỗi JSON)
        mqtt_handler.client.publish(topic, json.dumps(payload))
        
        print(f"📡 [Manual] Đã phát lệnh reo {pulses} hồi tới {clean_mac}")
        return {
            "status": "success", 
            "message": f"Đã ra lệnh reo {pulses} hồi tới chuông {clean_mac}"
        }
        
    except Exception as e:
        print(f"❌ Lỗi khi gửi lệnh Ring-now: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")
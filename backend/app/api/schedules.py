from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.session import get_db
from app.models.domain import Schedule, User, Device  # Thêm Device để tìm "đệ tử"
from app.schemas.schedule import ScheduleCreate, ScheduleResponse
from app.core.security import SecurityHandler

router = APIRouter(prefix="/schedules", tags=["Schedules"])

@router.post("/", response_model=ScheduleResponse)
async def create_schedule(
    sch_in: ScheduleCreate, 
    request: Request,        # Thêm Request để lôi đầu ông MQTT ra làm việc
    db: Session = Depends(get_db),
    current_user: User = Depends(SecurityHandler.get_current_user)
):
    # 1. Chuyển chuỗi "07:30" thành đối tượng time của Python cho đúng kiểu DB
    t_obj = datetime.strptime(sch_in.time_point, "%H:%M").time()
    
    # 2. Lưu lịch mới vào Database
    new_sch = Schedule(
        school_id=sch_in.school_id,
        day_of_week=sch_in.day_of_week,
        time_point=t_obj,
        pattern_id=sch_in.pattern_id,
        is_active=True
    )
    db.add(new_sch)
    db.commit()
    db.refresh(new_sch)

    # 3. 🚀 AUTO-PUSH: BÁO TIN CHO CÁC THIẾT BỊ ĐANG ONLINE
    try:
        # Lấy mqtt_handler từ trạng thái của ứng dụng (đã gắn ở main.py)
        mqtt_handler = request.app.state.mqtt_handler
        
        # Tìm tất cả thiết bị (Device) thuộc về trường này
        devices = db.query(Device).filter(Device.school_id == sch_in.school_id).all()
        
        for dev in devices:
            # Gửi tin nhắn vào topic 'sync_now' mà ESP32 đang chờ sẵn
            # Topic này phải khớp 100% với code ESP32 (E05A1BACAB50...)
            topic = f"school_bell/{dev.mac_address}/sync_now"
            
            # Bắn một tín hiệu nhẹ nhàng để ESP32 tự hiểu mà gọi lệnh request_sync
            mqtt_handler.client.publish(topic, "{\"cmd\": \"update_now\"}")
            
            print(f"📡 [Auto-Push] Đã ra lệnh cập nhật cho ESP32 MAC: {dev.mac_address}")
            
    except Exception as e:
        # Nếu MQTT chưa kết nối hoặc lỗi gì đó thì in ra log chứ không làm crash API
        print(f"⚠️ Lỗi khi cố gắng Auto-Push: {e}")

    return new_sch
@router.get("/") # <--- Phải là .get sếp nhé!
def list_schedules(db: Session = Depends(get_db)):
    # Query lấy kèm thông tin pattern để Web hiển thị được tên kiểu chuông
    return db.query(Schedule).all()
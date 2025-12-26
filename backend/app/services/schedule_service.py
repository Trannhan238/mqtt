from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from app.models.domain import School, Device, Schedule, Holiday, BellPattern

class ScheduleService:
    def __init__(self, db: Session):
        self.db = db

    def get_seasonal_time(self, school: School, original_time: time) -> str:
        """Tính toán giờ thực tế sau khi cộng offset mùa đông"""
        if not school.use_seasonal_config:
            return original_time.strftime("%H:%M")

        today_str = datetime.now().strftime("%m-%d")
        is_winter = False
        
        # Xử lý khoảng ngày mùa đông (ví dụ: 15/10 đến 15/04 sang năm)
        if school.winter_start_date > school.winter_end_date:
            if today_str >= school.winter_start_date or today_str <= school.winter_end_date:
                is_winter = True
        else:
            if school.winter_start_date <= today_str <= school.winter_end_date:
                is_winter = True

        if is_winter:
            dummy_dt = datetime.combine(date.today(), original_time)
            new_dt = dummy_dt + timedelta(minutes=school.winter_offset_minutes)
            return new_dt.strftime("%H:%M")
        
        return original_time.strftime("%H:%M")

    def is_holiday(self, school_id: int) -> bool:
        """Kiểm tra xem hôm nay trường có được nghỉ không"""
        today = date.today()
        holiday = self.db.query(Holiday).filter(
            Holiday.school_id == school_id,
            Holiday.start_date <= today,
            Holiday.end_date >= today
        ).first()
        return holiday is not None

    async def get_sync_data(self, mac_address: str):
        """Hàm 'chìa khóa' để nhả dữ liệu về cho ESP32 qua MQTT"""
        # 1. Chuẩn hóa MAC: Xóa dấu ':' và viết HOA để so khớp DB
        clean_mac = mac_address.replace(":", "").upper()
        
        device = self.db.query(Device).filter(Device.mac_address == clean_mac).first()
        if not device:
            print(f"⚠️ [Sync] Thiết bị lạ hoắc, không có trong DB: {clean_mac}")
            return None

        school = device.school
        if not school or not school.is_active:
            return {"en": False, "msg": "School inactive"}

        # 2. Kiểm tra ngày nghỉ
        if self.is_holiday(school.id):
            return {
                "v": datetime.now().strftime("%Y%m%d%H%M"),
                "en": device.is_enabled,
                "sch": [] # Trả về mảng rỗng để chuông không reo
            }

        # 3. Lấy lịch trình hôm nay (Thứ 2=0, ..., Thứ 4=2)
        day_of_week = datetime.now().weekday()
        schedules = self.db.query(Schedule).filter(
            Schedule.school_id == school.id,
            Schedule.day_of_week == day_of_week,
            Schedule.is_active == True
        ).all()

        sync_list = []
        for s in schedules:
            p = s.pattern # Mối quan hệ relationship trong model
            if not p: continue
            
            actual_time = self.get_seasonal_time(school, s.time_point)
            
            sync_list.append({
                "t": actual_time,
                "p": {
                    "ty": p.output_type,
                    "n": p.pulse_count,
                    "on": int(p.on_duration * 1000), # Giây sang mili giây
                    "off": int(p.off_duration * 1000),
                    "f": getattr(p, "audio_file_index", 0) # f=0 nếu không có nhạc
                }
            })

        print(f"✅ [Sync] Đã gửi {len(sync_list)} lịch trình cho {clean_mac}")
        return {
            "v": datetime.now().strftime("%Y%m%d%H%M"),
            "en": device.is_enabled,
            "sch": sync_list
        }
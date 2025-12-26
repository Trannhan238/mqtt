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
        today = date.today()
        holiday = self.db.query(Holiday).filter(
            Holiday.school_id == school_id,
            Holiday.start_date <= today,
            Holiday.end_date >= today
        ).first()
        return holiday is not None

    async def get_sync_data(self, mac_address: str):
        clean_mac = mac_address.replace(":", "").upper()
        device = self.db.query(Device).filter(Device.mac_address == clean_mac).first()
        
        if not device:
            print(f"⚠️ [Sync] Thiết bị không tồn tại: {clean_mac}")
            return None

        school = device.school
        if not school or not school.is_active:
            print(f"⚠️ [Sync] Trường học của {clean_mac} đang bị khóa.")
            return {"en": False, "msg": "School inactive"}

        # Lấy múi giờ hiện tại
        now = datetime.now()
        day_of_week = now.weekday()

        # LOG DEBUG: Kiểm tra tổng số lịch trong DB trước khi lọc
        total_in_db = self.db.query(Schedule).filter(Schedule.school_id == school.id).count()
        
        # Lấy lịch trình và SẮP XẾP theo thời gian (giúp ESP32 chạy ổn định hơn)
        schedules = self.db.query(Schedule).filter(
            Schedule.school_id == school.id,
            Schedule.day_of_week == day_of_week,
            Schedule.is_active == True
        ).order_by(Schedule.time_point).all()

        sync_list = []
        for s in schedules:
            p = s.pattern
            if not p: continue
            
            actual_time = self.get_seasonal_time(school, s.time_point)
            
            # QUAN TRỌNG: p.on_duration đã là mili giây từ DB (không nhân 1000 nữa)
            sync_list.append({
                "t": actual_time,
                "p": {
                    "ty": p.output_type,
                    "n": p.pulse_count,
                    "on": int(p.on_duration), 
                    "off": int(p.off_duration),
                    "f": getattr(p, "audio_file_index", 0)
                }
            })

        print(f"✅ [Sync] MAC: {clean_mac} | DB có: {total_in_db} | Gửi đi: {len(sync_list)} (Cho Thứ {day_of_week + 2})")

        return {
            "v": now.strftime("%Y%m%d%H%M%S"),
            "en": device.is_enabled,
            "sch": sync_list,
            "server_time": int(now.timestamp()) # THÊM DÒNG NÀY ĐỂ ESP32 SYNC GIỜ NGAY
        }
import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.domain import School, Schedule, BellPattern, Holiday, Device, BellLog
from app.core.security import SecurityHandler

class BellService:
    @staticmethod
    async def run_scheduler(mqtt_client):
        """Vòng lặp chạy ngầm, mỗi phút quét một lần"""
        while True:
            now = datetime.now()
            # Đợi cho đến giây đầu tiên của phút tiếp theo để quét cho chính xác
            await asyncio.sleep(60 - now.second) 
            
            db = SessionLocal()
            try:
                await BellService.check_and_trigger(db, mqtt_client)
            except Exception as e:
                print(f"❌ Lỗi Scheduler: {e}")
            finally:
                db.close()

    @staticmethod
    async def check_and_trigger(db: Session, mqtt_client):
        now = datetime.now()
        current_time = now.time().replace(second=0, microsecond=0)
        current_day = now.weekday() # 0-6 (Thứ 2 - CN)
        today_date = now.date()

        # 1. Lấy tất cả các trường đang hoạt động
        schools = db.query(School).filter(School.is_active == True).all()

        for school in schools:
            # 2. Check ngày nghỉ (Holiday)
            is_holiday = db.query(Holiday).filter(
                Holiday.school_id == school.id,
                Holiday.start_date <= today_date,
                Holiday.end_date >= today_date
            ).first()
            if is_holiday: continue

            # 3. Tính toán Offset mùa đông (nếu có)
            # Nếu đang mùa đông, mình sẽ tìm những lịch có (giờ gốc + offset = giờ hiện tại)
            offset = 0
            if school.use_seasonal_config:
                today_mmdd = now.strftime("%m-%d")
                # Check xem có trong khoảng mùa đông MM-DD không
                if school.winter_start_date <= today_mmdd or today_mmdd <= school.winter_end_date:
                    offset = school.winter_offset_minutes

            # 4. Tìm lịch trình khớp với giờ hiện tại (đã trừ offset)
            target_time = (datetime.combine(today_date, current_time) - timedelta(minutes=offset)).time()
            
            schedules = db.query(Schedule).filter(
                Schedule.school_id == school.id,
                Schedule.day_of_week == current_day,
                Schedule.time_point == target_time,
                Schedule.is_active == True
            ).all()

            for sch in schedules:
                await BellService.trigger_bell(db, sch, school, mqtt_client)

    @staticmethod
    async def trigger_bell(db, schedule, school, mqtt_client):
        pattern = schedule.pattern
        devices = db.query(Device).filter(Device.school_id == school.id, Device.is_enabled == True).all()

        for dev in devices:
            # Tạo payload theo đúng format con ESP32 của sếp cần
            payload = {
                "cmd": "RING",
                "type": pattern.output_type, # CLASSIC hoặc AUDIO
                "pulses": pattern.pulse_count,
                "on": pattern.on_duration,
                "off": pattern.off_duration,
                "file": pattern.audio_file_index,
                "vol": pattern.volume
            }
            
            topic = f"bell/{dev.mac_address}/cmd"
            mqtt_client.publish(topic, json.dumps(payload))
            
            # Ghi log vào DB cho sếp "soi"
            new_log = BellLog(
                device_id=dev.id,
                event_type="AUTO",
                status="SUCCESS",
                message=f"🔔 Reo tự động: {pattern.name}"
            )
            db.add(new_log)
        
        db.commit()
        print(f"✅ [SCH] Đã gửi lệnh reo cho trường: {school.name} ({schedule.time_point})")
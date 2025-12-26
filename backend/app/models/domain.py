from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Time, Date, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database.session import Base

# --- 1. TRƯỜNG HỌC ---
class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200))
    is_active = Column(Boolean, default=True)  # Khóa cả trường nếu nợ cước
    contract_end_date = Column(Date)
    
    # Cấu hình mùa đông/hè
    use_seasonal_config = Column(Boolean, default=False)
    winter_start_date = Column(String(5), default="10-15") # MM-DD
    winter_end_date = Column(String(5), default="04-15")
    winter_offset_minutes = Column(Integer, default=15)

    # Quan hệ
    users = relationship("User", back_populates="school")
    devices = relationship("Device", back_populates="school")
    schedules = relationship("Schedule", back_populates="school")
    patterns = relationship("BellPattern", back_populates="school")
    holidays = relationship("Holiday", back_populates="school")

# --- 2. NGƯỜI DÙNG ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="school_admin") # admin, school_admin
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    
    school = relationship("School", back_populates="users")

# --- 3. THIẾT BỊ (CHUÔNG) ---
class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    mac_address = Column(String(17), unique=True, index=True, nullable=False) # Luôn viết HOA, ko dấu :
    name = Column(String(100))
    school_id = Column(Integer, ForeignKey("schools.id"))
    
    is_active = Column(Boolean, default=True) 
    is_enabled = Column(Boolean, default=True) # Khóa/mở từng thiết bị
    
    status = Column(String(20), default="offline") # online, offline
    # Tự động cập nhật thời gian mỗi khi thiết bị gửi tín hiệu
    last_seen = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    mqtt_prefix = Column(String(100))
    firmware_version = Column(String(20))
    
    # Quan hệ
    school = relationship("School", back_populates="devices")
    logs = relationship("BellLog", back_populates="device") # Liên kết với bảng Log

# --- 4. KIỂU REO (MẪU CHUÔNG) ---
class BellPattern(Base):
    __tablename__ = "bell_patterns"
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    name = Column(String(50)) # e.g., "Vào lớp 3 hồi"
    output_type = Column(String(10)) # CLASSIC hoặc AUDIO
    
    # Config cho Classic (Relay)
    pulse_count = Column(Integer, default=1)
    on_duration = Column(Integer, default=3000) # Mili giây (đồng bộ với ESP32)
    off_duration = Column(Integer, default=2000) # Mili giây
    
    # Config cho Audio
    audio_file_index = Column(Integer, default=1)
    volume = Column(Integer, default=25)

    school = relationship("School", back_populates="patterns")
    schedules = relationship("Schedule", back_populates="pattern")

# --- 5. LỊCH TRÌNH REO ---
class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    pattern_id = Column(Integer, ForeignKey("bell_patterns.id"))
    
    day_of_week = Column(Integer, nullable=False) # 0-6 (CN-T7)
    time_point = Column(Time, nullable=False) 
    is_active = Column(Boolean, default=True)

    school = relationship("School", back_populates="schedules")
    pattern = relationship("BellPattern", back_populates="schedules")

# --- 6. NGÀY NGHỈ (LỄ/TẾT) ---
class Holiday(Base):
    __tablename__ = "holidays"
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    name = Column(String(100))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_recurring = Column(Boolean, default=False)

    school = relationship("School", back_populates="holidays")

# --- 7. NHẬT KÝ REO CHUÔNG (MỚI) ---
class BellLog(Base):
    __tablename__ = "bell_logs"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    event_type = Column(String(20)) # AUTO (Theo lịch), MANUAL (Bấm tay), SYNC (Đồng bộ)
    status = Column(String(20))     # SUCCESS, FAILED
    message = Column(Text)          # Chi tiết log (ví dụ: "Đã reo xong 3 hồi")
    created_at = Column(DateTime, server_default=func.now())

    device = relationship("Device", back_populates="logs")
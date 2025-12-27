import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import auth, schools, devices, schedules, patterns, users, logs
from app.core.config import settings
from app.database.session import engine, SessionLocal
from app.models import domain
from app.core.mqtt_client import MQTTHandler
from app.services.schedule_service import ScheduleService
from app.services.bell_service import BellService

# --- 1. KHỞI TẠO HỆ THỐNG ---
if not os.path.exists("data"):
    os.makedirs("data")
    print("📂 [System] Đã tạo thư mục data cho sếp!")

# Tạo bảng trong SQLite (Chạy trên OpenWrt cực nhẹ)
domain.Base.metadata.create_all(bind=engine)

# --- 2. HELPERS ---
@asynccontextmanager
async def get_schedule_service():
    db = SessionLocal()
    try:
        yield ScheduleService(db)
    finally:
        db.close()

# --- 3. QUẢN LÝ VÒNG ĐỜI (LIFESPAN) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lấy mqtt_handler từ state
    handler = app.state.mqtt_handler
    
    # A. Khởi động MQTT Worker
    mqtt_task = asyncio.create_task(handler.connect())
    print(f"📡 [MQTT] Đang kết nối tới {settings.MQTT_BROKER}...")
    
    # B. Khởi động TRÁI TIM: Bộ quét lịch tự động
    # Truyền handler.client vào để BellService có thể publish lệnh RING
    bell_task = asyncio.create_task(BellService.run_scheduler(handler.client))
    print("🔔 [Scheduler] Hệ thống quét lịch tự động đã lên nòng!")
    
    yield
    
    # C. Dọn dẹp khi tắt Server
    bell_task.cancel() # Tắt bộ quét lịch
    if handler.client.is_connected:
        await handler.client.disconnect()
    mqtt_task.cancel()
    print("😴 [System] MQTT và Scheduler đã đi ngủ.")

# --- 4. KHỞI TẠO FASTAPI ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# --- 5. KHỞI TẠO MQTT VÀ GẮN VÀO STATE ---
mqtt_handler = MQTTHandler(get_schedule_service)
app.state.mqtt_handler = mqtt_handler 

# --- 6. CẤU HÌNH MIDDLEWARE (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 7. ĐĂNG KÝ CÁC ROUTERS ---
app.include_router(auth.router)
app.include_router(users.router)      # Sếp nhớ thêm router User
app.include_router(schools.router)
app.include_router(devices.router)
app.include_router(schedules.router)
app.include_router(patterns.router)
app.include_router(logs.router)       # Sếp nhớ thêm router Log

# --- 8. HEALTH CHECK ---
@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "mqtt_broker": settings.MQTT_BROKER,
        "message": "Backend IOT School Bell đã sẵn sàng phục vụ sếp!"
    }

# --- 9. CHẠY SERVER ---
if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0 để các thiết bị trong mạng LAN (ESP32) có thể kết nối tới
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
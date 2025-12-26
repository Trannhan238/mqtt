import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import auth, schools, devices, schedules, patterns
from app.core.config import settings
from app.database.session import engine, SessionLocal
from app.models import domain
from app.core.mqtt_client import MQTTHandler
from app.services.schedule_service import ScheduleService

# --- 1. KHỞI TẠO HỆ THỐNG (Folder & Database) ---
if not os.path.exists("data"):
    os.makedirs("data")
    print("[System] Đã tạo thư mục data cho sếp!")

# Tạo bảng trong SQLite nếu chưa có
domain.Base.metadata.create_all(bind=engine)

# --- 2. HELPERS ---
@asynccontextmanager
async def get_schedule_service():
    """Hàm hỗ trợ MQTT Handler lấy dữ liệu từ DB"""
    db = SessionLocal()
    try:
        yield ScheduleService(db)
    finally:
        db.close()

# --- 3. QUẢN LÝ VÒNG ĐỜI ỨNG DỤNG (Lifespan) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lấy mqtt_handler từ state đã gắn ở bước 5
    handler = app.state.mqtt_handler
    
    # Khởi động Task MQTT chạy ngầm
    mqtt_task = asyncio.create_task(handler.connect())
    print(f"[System] MQTT Worker đang kết nối tới {settings.MQTT_BROKER}...")
    
    yield
    
    # Dọn dẹp khi tắt Server
    if handler.client.is_connected:
        await handler.client.disconnect()
    mqtt_task.cancel()
    print("[System] MQTT Worker đã đi ngủ.")

# --- 4. KHỞI TẠO FASTAPI ---
# (Phải tạo app trước khi gán app.state)
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# --- 5. KHỞI TẠO MQTT VÀ GẮN VÀO STATE ---
# (Đây là 'chìa khóa' để các file API khác gọi được MQTT)
mqtt_handler = MQTTHandler(get_schedule_service)
app.state.mqtt_handler = mqtt_handler 

# --- 6. CẤU HÌNH MIDDLEWARE (CORS) ---


app.add_middleware(
    CORSMiddleware,
    # Cho phép cổng 5173 của React truy cập
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 7. ĐĂNG KÝ CÁC ROUTERS ---
app.include_router(auth.router)
app.include_router(schools.router)
app.include_router(devices.router)
app.include_router(schedules.router)
app.include_router(patterns.router)

# --- 8. HEALTH CHECK ---
@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "mqtt_broker": settings.MQTT_BROKER,
        "message": "Backend IOT School Bell đã lên sàn!"
    }

# --- 9. CHẠY SERVER ---
if __name__ == "__main__":
    import uvicorn
    # Lưu ý: file này tên là main.py nên để "main:app"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
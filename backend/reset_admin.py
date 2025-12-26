import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.domain import Base, User
from app.core.security import SecurityHandler
from app.core.config import settings

# 1. In ra đường dẫn thực tế để kiểm tra
db_path = os.path.abspath("./data/bell.db")
print(f"🚀 Đường dẫn DB thực tế: {db_path}")

# 2. Kết nối thẳng bằng URL từ config
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# 3. Tạo lại bảng (nếu chưa có)
Base.metadata.create_all(bind=engine)

# 4. Xóa sạch User cũ và tạo mới
db.query(User).filter(User.username == "admin").delete()
hashed_pw = SecurityHandler.get_password_hash("admin123")

new_admin = User(
    username="admin",
    password_hash=hashed_pw,
    full_name="Quản trị viên",
    role="admin"
)

db.add(new_admin)
db.commit()
print("✅ Đã tạo xong Admin: admin / admin123")
db.close()
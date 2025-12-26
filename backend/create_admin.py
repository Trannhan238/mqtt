from app.database.session import SessionLocal
from app.models.domain import User
from app.core.security import SecurityHandler

def create_superuser():
    db = SessionLocal()
    # Kiểm tra xem đã có admin chưa
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        hashed_pw = SecurityHandler.get_password_hash("admin123") # Mật khẩu mặc định
        new_admin = User(
            username="admin",
            password_hash=hashed_pw,
            full_name="Quản trị viên",
            role="admin"
        )
        db.add(new_admin)
        db.commit()
        print("Đã tạo tài khoản admin/admin123 thành công!")
    else:
        print("Tài khoản admin đã tồn tại.")
    db.close()

if __name__ == "__main__":
    create_superuser()
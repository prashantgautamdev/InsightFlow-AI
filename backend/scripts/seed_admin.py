"""
Run once to create an initial admin account:
    python -m scripts.seed_admin
"""
from app.core.security import hash_password
from app.database.session import SessionLocal, Base, engine
from app.models.user import User, UserRole

ADMIN_EMAIL = "admin@insightflow.ai"
ADMIN_PASSWORD = "ChangeMe123!"


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if existing:
            print(f"Admin user already exists: {ADMIN_EMAIL}")
            return

        admin = User(
            full_name="Platform Admin",
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
            is_email_verified=True,
        )
        db.add(admin)
        db.commit()
        print(f"Created admin user: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print("IMPORTANT: change this password immediately in production.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL
if db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db_defaults():
    """Ensure essential initial records (such as default user) exist to prevent foreign key violations."""
    from app.models.models import User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            default_user = User(
                id=1,
                email="admin@travelagent.ai",
                hashed_password="$2b$12$e80yq9D36k8uK7s8yF7aNuC9oE3Y2x8.p9zJ9E0y/4U7m.wzH0q.",
                full_name="Admin Traveler",
                language="vi",
                currency="VND",
                timezone="Asia/Ho_Chi_Minh",
                is_active=True
            )
            db.add(default_user)
            db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()


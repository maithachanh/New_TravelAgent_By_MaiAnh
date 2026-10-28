from sqlalchemy import create_engine, text
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

def apply_compatible_schema_migrations():
    """Apply additive SQLite migrations for developer installations.

    Production PostgreSQL should use the deployment migration system, while
    this keeps existing local ``travel_agent.db`` files compatible after a
    pull without requiring the user to delete travel data.
    """
    if not db_url.startswith("sqlite"):
        return
    additions = {
        "payment_provider": "VARCHAR(30)",
        "payment_transaction_id": "VARCHAR(120)",
        "paid_at": "DATETIME",
        "voucher_code": "VARCHAR(120)",
        "share_token": "VARCHAR(80)",
    }
    with engine.begin() as connection:
        columns = {row[1] for row in connection.execute(text("PRAGMA table_info(bookings)"))}
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE bookings ADD COLUMN {name} {definition}"))
        trip_columns = {row[1] for row in connection.execute(text("PRAGMA table_info(trips)"))}
        for name, definition in {"share_token": "VARCHAR(80)"}.items():
            if name not in trip_columns:
                connection.execute(text(f"ALTER TABLE trips ADD COLUMN {name} {definition}"))

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


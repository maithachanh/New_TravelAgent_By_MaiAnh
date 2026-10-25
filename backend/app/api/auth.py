from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token
)
from app.models.models import User
from app.schemas.schemas import (
    UserRegister,
    UserLogin,
    Token,
    UserProfile,
    UserPreferencesUpdate
)

router = APIRouter(prefix="/auth", tags=["Authentication & User Profile"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_user_optional(token: str = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)) -> User:
    """Returns authenticated user if token present, otherwise falls back to default user (id=1)."""
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user:
                    return user
        except Exception:
            pass
    # Demo/local fallback
    default_user = db.query(User).filter(User.id == 1).first()
    if default_user:
        return default_user
    # If no user exists, create one on the fly
    new_user = User(
        id=1,
        email="admin@travelagent.ai",
        hashed_password="$2b$12$e80yq9D36k8uK7s8yF7aNuC9oE3Y2x8.p9zJ9E0y/4U7m.wzH0q.",
        full_name="Admin Traveler",
        language="vi",
        currency="VND",
        timezone="Asia/Ho_Chi_Minh",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
        
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        language=user_in.language or "vi",
        currency=user_in.currency or "VND",
        timezone=user_in.timezone or "Asia/Ho_Chi_Minh",
        travel_styles=user_in.travel_styles or []
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/preferences", response_model=UserProfile)
def update_preferences(
    prefs: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if prefs.language is not None:
        current_user.language = prefs.language
    if prefs.currency is not None:
        current_user.currency = prefs.currency
    if prefs.timezone is not None:
        current_user.timezone = prefs.timezone
    if prefs.travel_styles is not None:
        current_user.travel_styles = prefs.travel_styles
        
    db.commit()
    db.refresh(current_user)
    return current_user

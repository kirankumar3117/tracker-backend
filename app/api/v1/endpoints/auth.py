from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserLogin, AuthResponse, AuthResponseData, UserResponse, GoogleLoginRequest
from app.models import User
from app.api.deps import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from google.oauth2 import id_token
from google.auth.transport import requests

router = APIRouter()

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system",
        )
    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Automatically populate the new user's dashboard with default habits
    from app.services.habit_service import _seed_default_habits
    _seed_default_habits(db, user.id)

    access_token = create_access_token(subject=user.id)
    return AuthResponse(
        success=True,
        data=AuthResponseData(
            user=UserResponse.model_validate(user),
            token=access_token
        )
    )

@router.post("/login", response_model=AuthResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    
    if user and user.auth_provider == "google":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account was created using Google. Please click 'Continue with Google' to log in.",
        )
        
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(subject=str(user.id))
    return AuthResponse(
        success=True,
        data=AuthResponseData(
            user=UserResponse.model_validate(user),
            token=access_token
        )
    )

@router.post("/google", response_model=AuthResponse)
def google_auth(request_data: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        # Verify the token cryptographically
        id_info = id_token.verify_oauth2_token(
            request_data.token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        email = id_info.get("email")
        name = id_info.get("name")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google token"
            )
            
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create a new User record
            user = User(
                name=name or "Google User",
                email=email,
                password_hash=None,
                auth_provider="google"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Automatically populate the new user's dashboard with default habits
            from app.services.habit_service import _seed_default_habits
            _seed_default_habits(db, user.id)
            
        access_token = create_access_token(subject=str(user.id))
        return AuthResponse(
            success=True,
            data=AuthResponseData(
                user=UserResponse.model_validate(user),
                token=access_token
            )
        )
    except ValueError as e:
        # Invalid token
        print(f"Google Token Verification Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google token",
        )

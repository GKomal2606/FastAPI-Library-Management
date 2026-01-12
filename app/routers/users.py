# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from .. import models, schemas
from ..database import get_db
from ..utils.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    create_reset_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..auth import get_current_active_user
from ..tasks import send_welcome_email, send_password_reset_email

# ============================================
# CREATE ROUTER
# ============================================

router = APIRouter(
    prefix="/api/users",  # All routes start with /api/users
    tags=["users"]        # Group in Swagger docs
)


# ============================================
# 1. SIGN UP ENDPOINT (UNCHANGED)
# ============================================

@router.post("/signup", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Sends welcome email asynchronously.
    """
    
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send welcome email asynchronously
    send_welcome_email.delay(db_user.email, db_user.username)
    
    return db_user


# ============================================
# 2. LOGIN ENDPOINT - JSON
# ============================================

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token.
    """
    
    # Find user by email
    user = db.query(models.User).filter(
        models.User.email == user_credentials.email
    ).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    # Return token
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }


# ============================================
# 3. GET MY PROFILE ENDPOINT
# ============================================

@router.get("/me", response_model=schemas.User)
async def get_my_profile(
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get current user's profile.
    
    Requires authentication (JWT token).
    
    Returns:
        Current user's data
    """
    return current_user


# ============================================
# 4. UPDATE MY PROFILE ENDPOINT
# ============================================
@router.put("/me", response_model=schemas.User)
async def update_my_profile(
    full_name: str = None,
    username: str = None,
    email: str = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    """
    
    if full_name is not None:
        current_user.full_name = full_name
    
    if username is not None:
        existing_user = db.query(models.User).filter(
            models.User.username == username,
            models.User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        current_user.username = username
    
    if email is not None:
        # Check if email is already taken
        existing_user = db.query(models.User).filter(
            models.User.email == email,
            models.User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        current_user.email = email
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
    


# ============================================
# 5. FORGOT PASSWORD - REQUEST RESET
# ============================================

@router.post("/forgot-password")
def forgot_password(request: schemas.ForgotPassword, db: Session = Depends(get_db)):
    """
    Request password reset token.
    Sends reset email asynchronously.
    """
    
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = create_reset_token(user.email)
    
    # Store token
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    # Send email asynchronously
    send_password_reset_email.delay(user.email, reset_token)
    
    return {"message": "Password reset email sent"}

# ============================================
# 6. RESET PASSWORD
# ============================================

@router.post("/reset-password")
def reset_password(request: schemas.ResetPassword, db: Session = Depends(get_db)):
    """
    Reset password using reset token.
    
    Steps:
    1. Decode and verify token
    2. Check token type is "reset"
    3. Find user by email from token
    4. Verify token matches database
    5. Check token not expired
    6. Update password
    7. Clear reset token
    
    Returns:
        Success message
    
    Raises:
        400: If token is invalid or expired
    """
    
    from jose import jwt, JWTError
    from ..utils.security import SECRET_KEY, ALGORITHM
    
    try:
        # Decode the reset token
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")
        
        # Verify this is a reset token (not login token)
        if token_type != "reset":
            raise HTTPException(
                status_code=400, 
                detail="Invalid token type"
            )
            
    except JWTError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid or expired token"
        )
    
    # Find user by email from token
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # Verify user exists and token matches
    if not user or user.reset_token != request.token:
        raise HTTPException(
            status_code=400, 
            detail="Invalid token"
        )
    
    # Check if token has expired
    if user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=400, 
            detail="Token has expired"
        )
    
    # Update password (hash it first!)
    user.hashed_password = get_password_hash(request.new_password)
    
    # Clear reset token (can only be used once)
    user.reset_token = None
    user.reset_token_expires = None
    
    # Save changes
    db.commit()
    
    return {"message": "Password reset successful"}
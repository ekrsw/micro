from typing import Any, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, validate_token
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfile as UserProfileSchema
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate
from app.services import user_profile as user_profile_service

router = APIRouter()


@router.get("/", response_model=List[UserProfileSchema])
def read_user_profiles(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Retrieve user profiles.
    """
    # Only superusers can list all profiles
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    user_profiles = user_profile_service.get_multi(db, skip=skip, limit=limit)
    return user_profiles


@router.post("/", response_model=UserProfileSchema)
def create_user_profile(
    *,
    db: Session = Depends(get_db),
    user_profile_in: UserProfileCreate,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Create new user profile.
    """
    # Check if user is creating their own profile
    if current_user.get("id") != str(user_profile_in.user_id) and not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    user_profile = user_profile_service.get_by_user_id(db, user_id=user_profile_in.user_id)
    if user_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile for this user already exists",
        )
    
    user_profile = user_profile_service.create(db, obj_in=user_profile_in)
    return user_profile


@router.get("/me", response_model=UserProfileSchema)
def read_user_profile_me(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Get current user profile.
    """
    user_profile = user_profile_service.get_by_user_id(db, user_id=uuid.UUID(current_user.get("id")))
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return user_profile


@router.put("/me", response_model=UserProfileSchema)
def update_user_profile_me(
    *,
    db: Session = Depends(get_db),
    user_profile_in: UserProfileUpdate,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Update own user profile.
    """
    user_profile = user_profile_service.get_by_user_id(db, user_id=uuid.UUID(current_user.get("id")))
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    
    user_profile = user_profile_service.update(db, db_obj=user_profile, obj_in=user_profile_in)
    return user_profile


@router.get("/{profile_id}", response_model=UserProfileSchema)
def read_user_profile(
    *,
    db: Session = Depends(get_db),
    profile_id: uuid.UUID,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Get user profile by ID.
    """
    user_profile = user_profile_service.get_by_id(db, id=profile_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    
    # Check if user is getting their own profile
    if user_profile.user_id != uuid.UUID(current_user.get("id")) and not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return user_profile


@router.put("/{profile_id}", response_model=UserProfileSchema)
def update_user_profile(
    *,
    db: Session = Depends(get_db),
    profile_id: uuid.UUID,
    user_profile_in: UserProfileUpdate,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Update a user profile.
    """
    user_profile = user_profile_service.get_by_id(db, id=profile_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    
    # Check if user is updating their own profile
    if user_profile.user_id != uuid.UUID(current_user.get("id")) and not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    user_profile = user_profile_service.update(db, db_obj=user_profile, obj_in=user_profile_in)
    return user_profile


@router.delete("/{profile_id}", response_model=UserProfileSchema)
def delete_user_profile(
    *,
    db: Session = Depends(get_db),
    profile_id: uuid.UUID,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Delete a user profile.
    """
    user_profile = user_profile_service.get_by_id(db, id=profile_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    
    # Only superusers or the owners can delete profiles
    if user_profile.user_id != uuid.UUID(current_user.get("id")) and not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    user_profile = user_profile_service.delete(db, id=profile_id)
    return user_profile
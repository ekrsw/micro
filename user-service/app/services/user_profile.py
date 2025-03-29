from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate


def get_by_id(db: Session, id: uuid.UUID) -> Optional[UserProfile]:
    return db.query(UserProfile).filter(UserProfile.id == id).first()


def get_by_user_id(db: Session, user_id: uuid.UUID) -> Optional[UserProfile]:
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[UserProfile]:
    return db.query(UserProfile).offset(skip).limit(limit).all()


def create(db: Session, obj_in: UserProfileCreate) -> UserProfile:
    db_obj = UserProfile(
        user_id=obj_in.user_id,
        first_name=obj_in.first_name,
        last_name=obj_in.last_name,
        birth_date=obj_in.birth_date,
        phone_number=obj_in.phone_number,
        address=obj_in.address,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: UserProfile, obj_in: UserProfileUpdate) -> UserProfile:
    update_data = obj_in.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, id: uuid.UUID) -> UserProfile:
    obj = db.query(UserProfile).get(id)
    db.delete(obj)
    db.commit()
    return obj
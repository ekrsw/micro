from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_by_id(db: Session, id: uuid.UUID) -> Optional[Category]:
    return db.query(Category).filter(Category.id == id).first()


def get_by_name(db: Session, name: str) -> Optional[Category]:
    return db.query(Category).filter(Category.name == name).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    return db.query(Category).offset(skip).limit(limit).all()


def create(db: Session, obj_in: CategoryCreate) -> Category:
    db_obj = Category(
        name=obj_in.name,
        description=obj_in.description,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: Category, obj_in: CategoryUpdate) -> Category:
    update_data = obj_in.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, id: uuid.UUID) -> Category:
    obj = db.query(Category).get(id)
    db.delete(obj)
    db.commit()
    return obj
from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate


def get_by_id(db: Session, id: uuid.UUID) -> Optional[Product]:
    return db.query(Product).filter(Product.id == id).first()


def get_by_sku(db: Session, sku: str) -> Optional[Product]:
    return db.query(Product).filter(Product.sku == sku).first()


def get_multi(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[uuid.UUID] = None
) -> List[Product]:
    query = db.query(Product)
    if category_id:
        query = query.join(Product.categories).filter(Category.id == category_id)
    return query.offset(skip).limit(limit).all()


def create(db: Session, obj_in: ProductCreate) -> Product:
    categories = []
    if obj_in.category_ids:
        categories = db.query(Category).filter(Category.id.in_(obj_in.category_ids)).all()
    
    db_obj = Product(
        name=obj_in.name,
        description=obj_in.description,
        price=obj_in.price,
        stock=obj_in.stock if obj_in.stock is not None else 0,
        sku=obj_in.sku,
        is_active=obj_in.is_active if obj_in.is_active is not None else True,
        categories=categories
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, 
    db_obj: Product, 
    obj_in: ProductUpdate
) -> Product:
    update_data = obj_in.dict(exclude_unset=True, exclude={"category_ids"})
    
    # Update basic fields
    for key, value in update_data.items():
        if value is not None:
            setattr(db_obj, key, value)
    
    # Update categories if provided
    if obj_in.category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(obj_in.category_ids)).all()
        db_obj.categories = categories
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, id: uuid.UUID) -> Product:
    obj = db.query(Product).get(id)
    db.delete(obj)
    db.commit()
    return obj


def update_stock(db: Session, id: uuid.UUID, quantity: int) -> Product:
    product = get_by_id(db, id=id)
    if not product:
        return None
    
    product.stock += quantity
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
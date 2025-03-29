from typing import Any, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, validate_token
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryWithProducts
from app.services import category as category_service

router = APIRouter()


@router.get("/", response_model=List[Category])
def read_categories(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve categories.
    """
    categories = category_service.get_multi(db, skip=skip, limit=limit)
    return categories


@router.post("/", response_model=Category)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Create new category.
    """
    # Only superusers can create categories
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    category = category_service.get_by_name(db, name=category_in.name)
    if category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists",
        )
    
    category = category_service.create(db, obj_in=category_in)
    return category


@router.get("/{category_id}", response_model=CategoryWithProducts)
def read_category(
    *,
    db: Session = Depends(get_db),
    category_id: uuid.UUID,
) -> Any:
    """
    Get category by ID.
    """
    category = category_service.get_by_id(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return category


@router.put("/{category_id}", response_model=Category)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: uuid.UUID,
    category_in: CategoryUpdate,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Update a category.
    """
    # Only superusers can update categories
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    category = category_service.get_by_id(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Check if the updated name already exists
    if category_in.name and category_in.name != category.name:
        existing_category = category_service.get_by_name(db, name=category_in.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists",
            )
    
    category = category_service.update(db, db_obj=category, obj_in=category_in)
    return category


@router.delete("/{category_id}", response_model=Category)
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: uuid.UUID,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Delete a category.
    """
    # Only superusers can delete categories
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    category = category_service.get_by_id(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Check if category has products
    if category.products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with associated products",
        )
    
    category = category_service.delete(db, id=category_id)
    return category
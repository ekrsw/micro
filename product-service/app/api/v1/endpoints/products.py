from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, validate_token
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.services import product as product_service

router = APIRouter()


@router.get("/", response_model=List[Product])
def read_products(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[uuid.UUID] = None,
) -> Any:
    """
    Retrieve products.
    """
    products = product_service.get_multi(
        db, skip=skip, limit=limit, category_id=category_id
    )
    return products


@router.post("/", response_model=Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Create new product.
    """
    # Only superusers can create products
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    product = product_service.get_by_sku(db, sku=product_in.sku)
    if product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists",
        )
    
    product = product_service.create(db, obj_in=product_in)
    return product


@router.get("/{product_id}", response_model=Product)
def read_product(
    *,
    db: Session = Depends(get_db),
    product_id: uuid.UUID,
) -> Any:
    """
    Get product by ID.
    """
    product = product_service.get_by_id(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.put("/{product_id}", response_model=Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: uuid.UUID,
    product_in: ProductUpdate,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Update a product.
    """
    # Only superusers can update products
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    product = product_service.get_by_id(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    product = product_service.update(db, db_obj=product, obj_in=product_in)
    return product


@router.delete("/{product_id}", response_model=Product)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: uuid.UUID,
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Delete a product.
    """
    # Only superusers can delete products
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    product = product_service.get_by_id(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    product = product_service.delete(db, id=product_id)
    return product


@router.put("/{product_id}/stock", response_model=Product)
def update_product_stock(
    *,
    db: Session = Depends(get_db),
    product_id: uuid.UUID,
    quantity: int = Query(..., description="Quantity to add/subtract from stock"),
    current_user: dict = Depends(validate_token),
) -> Any:
    """
    Update product stock.
    """
    # Only superusers can update stock
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    product = product_service.get_by_id(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    # Check if quantity would make stock negative
    if product.stock + quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reduce stock below zero",
        )
    
    product = product_service.update_stock(db, id=product_id, quantity=quantity)
    return product